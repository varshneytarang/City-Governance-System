"""
Smart Notification Service

Manages task notifications, reminders, and department alerts.
Sends notifications when tasks become ready, deadlines approach, or approvals needed.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from .database import get_queries, TaskQueries
from .models import NotificationCreate, NotificationResponse, NotificationType
from .config import task_config

logger = logging.getLogger(__name__)


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationService:
    """
    Smart notification and reminder service
    """
    
    def __init__(self):
        self.queries: TaskQueries = get_queries()
        logger.info("✓ Notification Service initialized")
    
    # ==================== NOTIFICATION CREATION ====================
    
    def create_notification(
        self,
        notification_type: NotificationType,
        recipient_department: str,
        task_id: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[NotificationResponse]:
        """
        Create a new notification
        
        Args:
            notification_type: Type of notification
            recipient_department: Department to notify
            task_id: Related task
            message: Notification message
            priority: Notification priority
            action_url: Optional URL for action button
            metadata: Additional data
        
        Returns:
            Created notification or None
        """
        try:
            notification_data = NotificationCreate(
                task_id=task_id,
                notification_type=notification_type,
                recipient_department=recipient_department,
                message=message,
                priority=priority,
                action_url=action_url,
                metadata=metadata or {}
            )
            
            notif_id = self.queries.create_notification(notification_data.dict())
            
            if notif_id:
                logger.info(f"✓ Created {notification_type} notification for {recipient_department}")
                
                # TODO: Send actual notification (email, push, webhook)
                self._send_notification(notification_data)
                
                return NotificationResponse(
                    notification_id=notif_id,
                    **notification_data.dict(),
                    status="sent",
                    sent_at=datetime.utcnow(),
                    read_at=None,
                    created_at=datetime.utcnow()
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None
    
    def notify_task_ready(self, task_id: str) -> bool:
        """
        Notify department when task becomes ready to start
        
        Triggered when: All dependencies completed, task status -> ready
        """
        task = self.queries.get_task(task_id)
        
        if not task or task['task_status'] != 'ready':
            return False
        
        message = (
            f"🎯 Task ready to start: {task['task_title']}\n\n"
            f"All dependencies have been completed. You can now begin work on this task.\n"
            f"Priority: {task['priority'].upper()}\n"
        )
        
        if task.get('deadline'):
            deadline_str = task['deadline'].strftime('%Y-%m-%d %H:%M')
            message += f"Deadline: {deadline_str}\n"
        
        if task.get('estimated_duration_hours'):
            message += f"Estimated Duration: {task['estimated_duration_hours']} hours\n"
        
        priority = self._map_task_priority_to_notif(task['priority'])
        
        notification = self.create_notification(
            notification_type=NotificationType.TASK_READY,
            recipient_department=task['assigned_department'],
            task_id=task_id,
            message=message,
            priority=priority,
            action_url=f"/tasks/{task_id}",
            metadata={
                "task_title": task['task_title'],
                "workflow_id": str(task['workflow_id'])
            }
        )
        
        return notification is not None
    
    def notify_dependency_completed(
        self,
        task_id: str,
        completed_dependency_id: str
    ) -> bool:
        """
        Notify when a dependency completes (but task not ready yet)
        
        Keeps departments informed of progress toward task readiness
        """
        task = self.queries.get_task(task_id)
        completed_task = self.queries.get_task(completed_dependency_id)
        
        if not task or not completed_task:
            return False
        
        # Get remaining dependencies
        remaining = self.queries.get_task_dependencies(task_id)
        remaining_count = sum(
            1 for dep in remaining
            if self.queries.get_task(str(dep['depends_on_task_id']))['task_status'] != 'completed'
        )
        
        message = (
            f"📢 Dependency completed: {completed_task['task_title']}\n\n"
            f"One of your task dependencies has been completed.\n"
            f"Task: {task['task_title']}\n"
            f"Remaining dependencies: {remaining_count}\n"
        )
        
        notification = self.create_notification(
            notification_type=NotificationType.DEPENDENCY_COMPLETED,
            recipient_department=task['assigned_department'],
            task_id=task_id,
            message=message,
            priority=NotificationPriority.LOW,
            action_url=f"/tasks/{task_id}",
            metadata={
                "completed_task_id": completed_dependency_id,
                "remaining_dependencies": remaining_count
            }
        )
        
        return notification is not None
    
    def notify_deadline_approaching(
        self,
        task_id: str,
        hours_remaining: float
    ) -> bool:
        """
        Send reminder for approaching deadline
        
        Triggered by scheduled checks (e.g., 24h before, 1h before)
        """
        task = self.queries.get_task(task_id)
        
        if not task or not task.get('deadline'):
            return False
        
        # Don't notify for already completed/failed tasks
        if task['task_status'] in ['completed', 'failed', 'cancelled']:
            return False
        
        deadline_str = task['deadline'].strftime('%Y-%m-%d %H:%M')
        
        if hours_remaining <= 1:
            urgency = "🚨 URGENT"
            priority = NotificationPriority.URGENT
        elif hours_remaining <= 24:
            urgency = "⚠️  HIGH PRIORITY"
            priority = NotificationPriority.HIGH
        else:
            urgency = "⏰ Reminder"
            priority = NotificationPriority.MEDIUM
        
        message = (
            f"{urgency}: Deadline approaching\n\n"
            f"Task: {task['task_title']}\n"
            f"Deadline: {deadline_str}\n"
            f"Time Remaining: {hours_remaining:.1f} hours\n"
            f"Current Status: {task['task_status']}\n"
        )
        
        if task['task_status'] == 'ready':
            message += "\n⚡ Task is ready to start - please begin work immediately!"
        elif task['task_status'] == 'pending':
            message += "\n⚠️  Task still has unmet dependencies!"
        
        notification = self.create_notification(
            notification_type=NotificationType.DEADLINE_REMINDER,
            recipient_department=task['assigned_department'],
            task_id=task_id,
            message=message,
            priority=priority,
            action_url=f"/tasks/{task_id}",
            metadata={
                "hours_remaining": hours_remaining,
                "deadline": deadline_str
            }
        )
        
        return notification is not None
    
    def notify_approval_needed(
        self,
        workflow_id: str,
        task_id: Optional[str] = None,
        approval_type: str = "workflow",
        reason: str = ""
    ) -> bool:
        """
        Notify when approval is needed
        
        Args:
            workflow_id: Workflow requiring approval
            task_id: Specific task (optional)
            approval_type: Type of approval (workflow, budget, contingency, etc.)
            reason: Reason for approval request
        """
        workflow = self.queries.get_workflow(workflow_id)
        
        if not workflow:
            return False
        
        # Notify coordination agent (central approval)
        message = (
            f"✋ Approval Required: {approval_type}\n\n"
            f"Workflow: {workflow['workflow_name']}\n"
        )
        
        if task_id:
            task = self.queries.get_task(task_id)
            if task:
                message += f"Task: {task['task_title']}\n"
        
        if reason:
            message += f"\nReason: {reason}\n"
        
        message += "\nPlease review and approve or reject this request."
        
        notification = self.create_notification(
            notification_type=NotificationType.APPROVAL_NEEDED,
            recipient_department="coordination",  # Central coordination agent
            task_id=task_id or workflow_id,
            message=message,
            priority=NotificationPriority.HIGH,
            action_url=f"/workflows/{workflow_id}/approval",
            metadata={
                "approval_type": approval_type,
                "reason": reason,
                "workflow_id": workflow_id,
                "task_id": task_id
            }
        )
        
        return notification is not None
    
    def notify_task_blocked(
        self,
        task_id: str,
        blocker_reason: str,
        blocker_id: Optional[str] = None
    ) -> bool:
        """
        Notify when task becomes blocked
        """
        task = self.queries.get_task(task_id)
        
        if not task:
            return False
        
        message = (
            f"🚫 Task Blocked: {task['task_title']}\n\n"
            f"Reason: {blocker_reason}\n"
            f"Department: {task['assigned_department']}\n"
            f"\nPlease address the blocker to continue."
        )
        
        # Notify both assigned department and coordination
        notifications = []
        
        # Department notification
        notif1 = self.create_notification(
            notification_type=NotificationType.TASK_BLOCKED,
            recipient_department=task['assigned_department'],
            task_id=task_id,
            message=message,
            priority=NotificationPriority.HIGH,
            action_url=f"/tasks/{task_id}",
            metadata={
                "blocker_reason": blocker_reason,
                "blocker_id": blocker_id
            }
        )
        notifications.append(notif1)
        
        # Coordination notification
        notif2 = self.create_notification(
            notification_type=NotificationType.TASK_BLOCKED,
            recipient_department="coordination",
            task_id=task_id,
            message=f"⚠️  Coordination Alert\n\n{message}",
            priority=NotificationPriority.HIGH,
            action_url=f"/tasks/{task_id}",
            metadata={
                "blocker_reason": blocker_reason,
                "blocker_id": blocker_id
            }
        )
        notifications.append(notif2)
        
        return all(n is not None for n in notifications)
    
    def notify_workflow_completed(self, workflow_id: str) -> bool:
        """
        Notify when entire workflow completes
        """
        workflow = self.queries.get_workflow(workflow_id)
        
        if not workflow:
            return False
        
        # Get workflow statistics
        tasks = self.queries.get_workflow_tasks(workflow_id)
        total_cost = sum(t.get('actual_cost', 0) or t.get('estimated_cost', 0) for t in tasks)
        
        # Calculate total duration
        start_times = [t['started_at'] for t in tasks if t.get('started_at')]
        end_times = [t['completed_at'] for t in tasks if t.get('completed_at')]
        
        if start_times and end_times:
            duration = max(end_times) - min(start_times)
            duration_hours = duration.total_seconds() / 3600
        else:
            duration_hours = 0
        
        message = (
            f"✅ Workflow Completed: {workflow['workflow_name']}\n\n"
            f"All {len(tasks)} tasks have been successfully completed!\n\n"
            f"Statistics:\n"
            f"• Total Tasks: {len(tasks)}\n"
            f"• Total Duration: {duration_hours:.1f} hours\n"
            f"• Total Cost: ${total_cost:,.2f}\n"
        )
        
        # Notify all departments involved
        departments = set(t['assigned_department'] for t in tasks)
        
        for dept in departments:
            self.create_notification(
                notification_type=NotificationType.WORKFLOW_COMPLETED,
                recipient_department=dept,
                task_id=workflow_id,
                message=message,
                priority=NotificationPriority.MEDIUM,
                action_url=f"/workflows/{workflow_id}",
                metadata={
                    "total_tasks": len(tasks),
                    "duration_hours": duration_hours,
                    "total_cost": total_cost
                }
            )
        
        return True
    
    # ==================== SCHEDULED REMINDERS ====================
    
    def check_and_send_deadline_reminders(self) -> int:
        """
        Check for approaching deadlines and send reminders
        
        Should be run periodically (e.g., every hour)
        
        Returns:
            Number of reminders sent
        """
        logger.info("Checking for deadline reminders...")
        
        reminder_count = 0
        
        # Get all active tasks with deadlines
        from .database import get_db
        db = get_db()
        
        query = """
            SELECT task_id, deadline, task_status
            FROM tasks
            WHERE deadline IS NOT NULL
            AND task_status NOT IN ('completed', 'failed', 'cancelled')
            AND deadline > CURRENT_TIMESTAMP
            ORDER BY deadline ASC
        """
        
        tasks = db.execute_query(query)
        
        now = datetime.utcnow()
        
        for task in tasks:
            task_id = str(task['task_id'])
            deadline = task['deadline']
            
            # Calculate hours until deadline
            hours_remaining = (deadline - now).total_seconds() / 3600
            
            # Check if we should send reminder
            if self._should_send_reminder(task_id, hours_remaining):
                if self.notify_deadline_approaching(task_id, hours_remaining):
                    reminder_count += 1
        
        logger.info(f"✓ Sent {reminder_count} deadline reminders")
        return reminder_count
    
    def _should_send_reminder(
        self,
        task_id: str,
        hours_remaining: float
    ) -> bool:
        """
        Determine if reminder should be sent based on configuration
        """
        # Check if we already sent a reminder recently
        from .database import get_db
        db = get_db()
        
        query = """
            SELECT sent_at
            FROM task_notifications
            WHERE task_id = %s
            AND notification_type = 'deadline_reminder'
            AND sent_at > CURRENT_TIMESTAMP - INTERVAL '1 hour'
            ORDER BY sent_at DESC
            LIMIT 1
        """
        
        recent = db.execute_query(query, (task_id,))
        
        if recent:
            return False  # Already sent reminder in last hour
        
        # Send reminder at 1 hour, 6 hours, 24 hours, 48 hours
        reminder_thresholds = [1, 6, 24, 48]
        
        for threshold in reminder_thresholds:
            if threshold - 0.5 <= hours_remaining <= threshold + 0.5:
                return True
        
        return False
    
    # ==================== NOTIFICATION MANAGEMENT ====================
    
    def get_department_notifications(
        self,
        department: str,
        include_read: bool = False,
        limit: int = 50
    ) -> List[NotificationResponse]:
        """
        Get notifications for a department
        
        Args:
            department: Department name
            include_read: Include already-read notifications
            limit: Maximum number to return
        
        Returns:
            List of notifications
        """
        from .database import get_db
        db = get_db()
        
        query = """
            SELECT 
                notification_id, task_id, notification_type,
                recipient_department, message, priority,
                action_url, metadata, status,
                sent_at, read_at, created_at
            FROM task_notifications
            WHERE recipient_department = %s
        """
        
        params = [department]
        
        if not include_read:
            query += " AND read_at IS NULL"
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        results = db.execute_query(query, tuple(params))
        
        return [NotificationResponse(**row) for row in results]
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        from .database import get_db
        db = get_db()
        
        query = """
            UPDATE task_notifications
            SET read_at = CURRENT_TIMESTAMP, status = 'read'
            WHERE notification_id = %s
        """
        
        try:
            db.execute_query(query, (notification_id,), fetch_all=False)
            logger.info(f"✓ Marked notification {notification_id} as read")
            return True
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    def get_unread_count(self, department: str) -> int:
        """Get count of unread notifications for department"""
        from .database import get_db
        db = get_db()
        
        query = """
            SELECT COUNT(*) as count
            FROM task_notifications
            WHERE recipient_department = %s
            AND read_at IS NULL
        """
        
        result = db.execute_query(query, (department,))
        return result[0]['count'] if result else 0
    
    # ==================== NOTIFICATION DELIVERY ====================
    
    def _send_notification(self, notification: NotificationCreate):
        """
        Send notification through configured channels
        
        TODO: Implement actual delivery (email, push, webhook, websocket)
        """
        # For now, just log
        logger.info(
            f"📬 NOTIFICATION [{notification.priority}] => {notification.recipient_department}: "
            f"{notification.message[:50]}..."
        )
        
        # Future implementations:
        # - Email via SMTP
        # - Push notifications via Firebase/OneSignal
        # - Webhooks to external systems
        # - WebSocket for real-time updates
        # - SMS for urgent notifications
    
    # ==================== UTILITY METHODS ====================
    
    def _map_task_priority_to_notif(self, task_priority: str) -> NotificationPriority:
        """Map task priority to notification priority"""
        mapping = {
            "low": NotificationPriority.LOW,
            "medium": NotificationPriority.MEDIUM,
            "high": NotificationPriority.HIGH,
            "critical": NotificationPriority.URGENT,
            "emergency": NotificationPriority.URGENT
        }
        return mapping.get(task_priority, NotificationPriority.MEDIUM)


# Singleton instance
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get notification service singleton"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
