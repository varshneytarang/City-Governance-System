"""
Workflow Engine - Dependency Resolution and State Management

This engine:
- Resolves task dependencies
- Manages workflow state machines
- Determines task execution order
- Handles blocking and unblocking
- Triggers notifications when tasks become ready
"""

import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID
from collections import deque, defaultdict

from .database import get_queries, TaskQueries
from .models import TaskStatus, DependencyType
from .task_manager import get_task_manager, TaskManager

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Orchestrates workflow execution through dependency resolution
    """
    
    def __init__(self):
        self.queries: TaskQueries = get_queries()
        self.task_manager: TaskManager = get_task_manager()
        logger.info("✓ Workflow Engine initialized")
    
    # ==================== DEPENDENCY RESOLUTION ====================
    
    def resolve_dependencies(self, workflow_id: str) -> Dict[str, Any]:
        """
        Resolve all dependencies for a workflow and determine execution order
        
        Returns:
            {
                "ready_tasks": [task_ids that can execute now],
                "blocked_tasks": [task_ids waiting on dependencies],
                "execution_order": [ordered list of task_ids],
                "critical_path": [task_ids on critical path],
                "circular_dependencies": [list of circular dependency chains]
            }
        """
        logger.info(f"Resolving dependencies for workflow {workflow_id}")
        
        tasks = self.queries.get_workflow_tasks(workflow_id)
        
        if not tasks:
            return {
                "ready_tasks": [],
                "blocked_tasks": [],
                "execution_order": [],
                "critical_path": [],
                "circular_dependencies": []
            }
        
        # Build dependency graph
        task_graph = self._build_dependency_graph(tasks)
        
        # Find circular dependencies
        circular_deps = self._find_circular_dependencies(task_graph)
        
        # Determine ready tasks (no unsatisfied dependencies)
        ready_tasks = []
        blocked_tasks = []
        
        for task in tasks:
            task_id = str(task['task_id'])
            
            if task['status'] in ['completed', 'cancelled']:
                continue
            
            dependencies = self.queries.get_task_dependencies(task_id)
            
            if not dependencies:
                # No dependencies = ready
                if task['status'] in ['pending', 'ready']:
                    ready_tasks.append(task_id)
            else:
                # Check if all dependencies satisfied
                all_satisfied = all(d['satisfied'] for d in dependencies)
                
                if all_satisfied and task['status'] in ['pending', 'ready']:
                    ready_tasks.append(task_id)
                elif not all_satisfied:
                    blocked_tasks.append(task_id)
        
        # Calculate execution order (topological sort)
        execution_order = self._topological_sort(task_graph)
        
        # Find critical path
        critical_path = self._find_critical_path(tasks, task_graph)
        
        result = {
            "ready_tasks": ready_tasks,
            "blocked_tasks": blocked_tasks,
            "execution_order": execution_order,
            "critical_path": critical_path,
            "circular_dependencies": circular_deps
        }
        
        logger.info(
            f"Dependency resolution complete: "
            f"{len(ready_tasks)} ready, {len(blocked_tasks)} blocked"
        )
        
        return result
    
    def _build_dependency_graph(self, tasks: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """
        Build adjacency list representing task dependencies
        
        Returns:
            {task_id: set(depends_on_task_ids)}
        """
        graph = defaultdict(set)
        
        for task in tasks:
            task_id = str(task['task_id'])
            graph[task_id]  # Ensure node exists even if no dependencies
            
            dependencies = self.queries.get_task_dependencies(task_id)
            for dep in dependencies:
                graph[task_id].add(str(dep['depends_on_task_id']))
        
        return graph
    
    def _find_circular_dependencies(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """
        Find all circular dependency chains using DFS
        
        Returns:
            List of circular dependency chains
        """
        visited = set()
        rec_stack = set()
        circular_chains = []
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    circular_chains.append(cycle)
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return circular_chains
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """
        Topological sort using Kahn's algorithm
        
        Returns execution order for tasks (respecting dependencies)
        """
        # Calculate in-degree for each node
        in_degree = defaultdict(int)
        
        for node in graph:
            if node not in in_degree:
                in_degree[node] = 0
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # Start with nodes that have no dependencies
        queue = deque([node for node in graph if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # For each task that depends on this task
            for other_node in graph:
                if node in graph[other_node]:
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        queue.append(other_node)
        
        return result
    
    def _find_critical_path(
        self, 
        tasks: List[Dict[str, Any]], 
        graph: Dict[str, Set[str]]
    ) -> List[str]:
        """
        Find the critical path (longest path through the workflow)
        Uses dynamic programming to calculate longest path
        """
        # Build task duration map
        duration_map = {}
        for task in tasks:
            task_id = str(task['task_id'])
            duration_map[task_id] = task.get('estimated_duration_hours', 0) or 0
        
        # Calculate longest path to each node
        longest_path = {}
        
        def calculate_longest_path(node: str) -> int:
            if node in longest_path:
                return longest_path[node]
            
            if not graph[node]:
                # No dependencies
                longest_path[node] = duration_map[node]
                return longest_path[node]
            
            max_path = 0
            for dep in graph[node]:
                max_path = max(max_path, calculate_longest_path(dep))
            
            longest_path[node] = max_path + duration_map[node]
            return longest_path[node]
        
        # Calculate for all nodes
        for node in graph:
            calculate_longest_path(node)
        
        # Find the path with maximum duration
        if not longest_path:
            return []
        
        critical_node = max(longest_path, key=longest_path.get)
        
        # Reconstruct the path
        path = [critical_node]
        current = critical_node
        
        while graph[current]:
            # Find the dependency with longest path
            next_node = max(
                graph[current],
                key=lambda n: longest_path.get(n, 0)
            )
            path.append(next_node)
            current = next_node
        
        return list(reversed(path))
    
    # ==================== WORKFLOW STATE MANAGEMENT ====================
    
    def start_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Start a workflow (transition from draft/active to in_progress)
        
        Returns:
            Status and list of tasks that can be started
        """
        logger.info(f"Starting workflow {workflow_id}")
        
        # Update workflow status
        self.task_manager.update_workflow_status(
            workflow_id,
            "in_progress",
            reason="Workflow started"
        )
        
        # Resolve dependencies and find ready tasks
        resolution = self.resolve_dependencies(workflow_id)
        
        # Update ready tasks to 'ready' status
        for task_id in resolution['ready_tasks']:
            task = self.queries.get_task(task_id)
            if task and task['status'] == 'pending':
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.READY,
                    reason="Workflow started, no dependencies",
                    updated_by="system",
                    updated_by_type="automation"
                )
        
        logger.info(f"✓ Workflow {workflow_id} started with {len(resolution['ready_tasks'])} ready tasks")
        
        return {
            "workflow_id": workflow_id,
            "status": "in_progress",
            "ready_tasks": resolution['ready_tasks'],
            "execution_order": resolution['execution_order'],
            "warnings": resolution['circular_dependencies']
        }
    
    def check_workflow_completion(self, workflow_id: str) -> bool:
        """
        Check if all tasks in a workflow are complete
        If yes, mark workflow as completed
        
        Returns:
            True if workflow is complete
        """
        tasks = self.queries.get_workflow_tasks(workflow_id)
        
        if not tasks:
            return False
        
        all_complete = all(
            task['status'] in ['completed', 'cancelled'] 
            for task in tasks
        )
        
        if all_complete:
            # Check if any tasks failed
            any_failed = any(task['status'] == 'failed' for task in tasks)
            
            if any_failed:
                logger.info(f"Workflow {workflow_id} completed with failures")
            else:
                logger.info(f"✓ Workflow {workflow_id} completed successfully")
            
            self.task_manager.update_workflow_status(
                workflow_id,
                "completed",
                reason="All tasks completed"
            )
            
            return True
        
        return False
    
    def unblock_task(
        self, 
        task_id: str, 
        unblock_reason: str,
        unblocked_by: str = "human_agent"
    ) -> bool:
        """
        Manually unblock a blocked task
        
        Args:
            task_id: Task to unblock
            unblock_reason: Why task is being unblocked
            unblocked_by: Who unblocked it
        
        Returns:
            True if successful
        """
        task = self.queries.get_task(task_id)
        if not task:
            return False
        
        if task['status'] != 'blocked':
            logger.warning(f"Task {task_id} is not blocked (status: {task['status']})")
            return False
        
        # Check if dependencies are satisfied
        dependencies_ok = self.task_manager.check_task_ready(task_id)
        
        new_status = TaskStatus.READY if dependencies_ok else TaskStatus.IN_PROGRESS
        
        success = self.task_manager.update_task_status(
            task_id,
            new_status,
            reason=f"Unblocked: {unblock_reason}",
            updated_by=unblocked_by,
            updated_by_type="human"
        )
        
        if success:
            logger.info(f"✓ Task {task_id} unblocked by {unblocked_by}")
        
        return success
    
    # ==================== DEPENDENCY ANALYSIS ====================
    
    def analyze_task_dependencies(self, task_id: str) -> Dict[str, Any]:
        """
        Detailed analysis of a task's dependencies
        
        Returns:
            {
                "task_id": str,
                "can_start": bool,
                "blocking_tasks": [list of tasks blocking this one],
                "depends_on_count": int,
                "dependent_count": int (tasks waiting on this),
                "estimated_wait_time": int (hours),
                "on_critical_path": bool
            }
        """
        task = self.queries.get_task(task_id)
        if not task:
            return {}
        
        dependencies = self.queries.get_task_dependencies(task_id)
        dependent_tasks = self.queries.get_dependent_tasks(task_id)
        
        # Find blocking tasks (unsatisfied dependencies)
        blocking_tasks = []
        estimated_wait = 0
        
        for dep in dependencies:
            if not dep['satisfied']:
                blocking_task = self.queries.get_task(str(dep['depends_on_task_id']))
                blocking_tasks.append({
                    "task_id": str(dep['depends_on_task_id']),
                    "task_title": dep['depends_on_title'],
                    "status": dep['depends_on_status'],
                    "dependency_type": dep['dependency_type']
                })
                
                # Estimate wait time
                if blocking_task:
                    remaining_hours = blocking_task.get('estimated_duration_hours', 0) or 0
                    progress = blocking_task.get('progress_percentage', 0) or 0
                    remaining = remaining_hours * (1 - progress / 100)
                    estimated_wait += remaining
        
        can_start = len(blocking_tasks) == 0 and task['status'] in ['pending', 'ready']
        
        # Check if on critical path
        workflow_id = str(task['workflow_id'])
        resolution = self.resolve_dependencies(workflow_id)
        on_critical_path = task_id in resolution.get('critical_path', [])
        
        return {
            "task_id": task_id,
            "task_title": task['task_title'],
            "status": task['status'],
            "can_start": can_start,
            "blocking_tasks": blocking_tasks,
            "depends_on_count": len(dependencies),
            "dependent_count": len(dependent_tasks),
            "estimated_wait_time_hours": round(estimated_wait, 1),
            "on_critical_path": on_critical_path
        }
    
    def get_next_tasks_to_execute(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the next N tasks that should be executed in optimal order
        
        Considers:
        - Dependencies
        - Priority
        - Critical path
        - Resource availability (future enhancement)
        
        Returns:
            List of tasks with execution recommendations
        """
        resolution = self.resolve_dependencies(workflow_id)
        ready_task_ids = resolution['ready_tasks']
        
        if not ready_task_ids:
            return []
        
        # Get full task details
        tasks_with_details = []
        
        for task_id in ready_task_ids[:limit]:
            task = self.queries.get_task(task_id)
            if not task:
                continue
            
            analysis = self.analyze_task_dependencies(task_id)
            
            # Calculate priority score
            priority_scores = {
                'emergency': 100,
                'critical': 80,
                'high': 60,
                'medium': 40,
                'low': 20
            }
            
            priority_score = priority_scores.get(task['priority'], 40)
            critical_path_bonus = 50 if analysis['on_critical_path'] else 0
            dependent_count_score = min(analysis['dependent_count'] * 5, 30)
            
            total_score = priority_score + critical_path_bonus + dependent_count_score
            
            tasks_with_details.append({
                "task_id": task_id,
                "task_title": task['task_title'],
                "assigned_department": task['assigned_department'],
                "priority": task['priority'],
                "on_critical_path": analysis['on_critical_path'],
                "dependent_tasks_count": analysis['dependent_count'],
                "execution_score": total_score,
                "estimated_duration_hours": task.get('estimated_duration_hours', 0),
                "recommendation": self._generate_task_recommendation(task, analysis)
            })
        
        # Sort by execution score (highest first)
        tasks_with_details.sort(key=lambda x: x['execution_score'], reverse=True)
        
        return tasks_with_details
    
    def _generate_task_recommendation(
        self, 
        task: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> str:
        """Generate a recommendation for task execution"""
        reasons = []
        
        if analysis['on_critical_path']:
            reasons.append("on critical path")
        
        if task['priority'] in ['emergency', 'critical']:
            reasons.append(f"{task['priority']} priority")
        
        if analysis['dependent_count'] > 0:
            reasons.append(f"{analysis['dependent_count']} tasks waiting")
        
        if not reasons:
            return "Ready to execute"
        
        return f"Execute soon: {', '.join(reasons)}"
    
    # ==================== WORKFLOW OPTIMIZATION ====================
    
    def suggest_workflow_optimizations(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Analyze workflow and suggest optimizations
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        resolution = self.resolve_dependencies(workflow_id)
        
        # Check for circular dependencies
        if resolution['circular_dependencies']:
            suggestions.append({
                "type": "error",
                "title": "Circular Dependencies Detected",
                "description": f"Found {len(resolution['circular_dependencies'])} circular dependency chains",
                "severity": "critical",
                "action": "Review and remove circular dependencies"
            })
        
        # Check for long critical path
        critical_path = resolution['critical_path']
        if len(critical_path) > 10:
            suggestions.append({
                "type": "warning",
                "title": "Long Critical Path",
                "description": f"Critical path has {len(critical_path)} tasks",
                "severity": "medium",
                "action": "Consider parallelizing some tasks to reduce overall duration"
            })
        
        # Check for bottleneck tasks (many tasks depend on one)
        tasks = self.queries.get_workflow_tasks(workflow_id)
        for task in tasks:
            dependent_count = len(self.queries.get_dependent_tasks(str(task['task_id'])))
            if dependent_count > 5:
                suggestions.append({
                    "type": "info",
                    "title": "Bottleneck Task",
                    "description": f"Task '{task['task_title']}' has {dependent_count} dependent tasks",
                    "severity": "low",
                    "action": "Consider splitting this task or providing contingency plans"
                })
        
        return suggestions


# Singleton instance
_workflow_engine = None


def get_workflow_engine() -> WorkflowEngine:
    """Get workflow engine singleton"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
