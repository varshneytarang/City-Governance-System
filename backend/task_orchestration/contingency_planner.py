"""
LLM-Powered Contingency Planner

Generates intelligent backup plans when tasks fail or encounter blockers.
Uses LLM (Groq/OpenAI) to create context-aware alternative approaches.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .database import get_queries, TaskQueries
from .config import task_config
from .models import ContingencyPlanCreate, ContingencyPlanResponse

logger = logging.getLogger(__name__)


class ContingencyPlanner:
    """
    Generates and manages contingency plans for tasks
    """
    
    def __init__(self):
        self.queries: TaskQueries = get_queries()
        self.llm_client = None
        self._initialize_llm()
        logger.info("✓ Contingency Planner initialized")
    
    def _initialize_llm(self):
        """Initialize LLM client based on configuration"""
        try:
            if task_config.LLM_PROVIDER == "groq" and task_config.GROQ_API_KEY:
                from langchain_groq import ChatGroq
                self.llm_client = ChatGroq(
                    api_key=task_config.GROQ_API_KEY,
                    model_name=task_config.LLM_MODEL,
                    temperature=task_config.LLM_TEMPERATURE
                )
                logger.info(f"✓ LLM initialized: Groq ({task_config.LLM_MODEL})")
            elif task_config.LLM_PROVIDER == "openai" and task_config.OPENAI_API_KEY:
                from langchain_openai import ChatOpenAI
                self.llm_client = ChatOpenAI(
                    api_key=task_config.OPENAI_API_KEY,
                    model_name=task_config.LLM_MODEL,
                    temperature=task_config.LLM_TEMPERATURE
                )
                logger.info(f"✓ LLM initialized: OpenAI ({task_config.LLM_MODEL})")
            else:
                logger.warning("⚠️  No LLM configured - contingency generation will use fallback rules")
                self.llm_client = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            self.llm_client = None
    
    # ==================== CONTINGENCY GENERATION ====================
    
    def generate_contingency_plans(
        self,
        task_id: str,
        failure_reason: str,
        num_plans: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ContingencyPlanResponse]:
        """
        Generate contingency plans for a failed/blocked task
        
        Args:
            task_id: Task that needs contingency plans
            failure_reason: Why the task failed/blocked
            num_plans: Number of alternative plans to generate
            context: Additional context for plan generation
        
        Returns:
            List of generated contingency plans
        """
        logger.info(f"Generating {num_plans} contingency plans for task {task_id}")
        
        # Get task details
        task = self.queries.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        workflow = self.queries.get_workflow(str(task['workflow_id']))
        
        # Build context for LLM
        full_context = self._build_context(task, workflow, failure_reason, context)
        
        # Generate plans
        if self.llm_client and task_config.AUTO_GENERATE_CONTINGENCY:
            plans = self._generate_llm_plans(full_context, num_plans)
        else:
            plans = self._generate_fallback_plans(full_context, num_plans)
        
        # Save plans to database
        saved_plans = []
        for i, plan_data in enumerate(plans, start=1):
            plan = self._save_contingency_plan(
                task_id=task_id,
                workflow_id=str(task['workflow_id']),
                plan_data=plan_data,
                plan_order=i
            )
            if plan:
                saved_plans.append(plan)
        
        logger.info(f"✓ Generated {len(saved_plans)} contingency plans")
        return saved_plans
    
    def _build_context(
        self,
        task: Dict[str, Any],
        workflow: Dict[str, Any],
        failure_reason: str,
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build comprehensive context for contingency plan generation"""
        return {
            "task": {
                "title": task['task_title'],
                "description": task.get('task_description', ''),
                "department": task['assigned_department'],
                "priority": task['priority'],
                "estimated_cost": task.get('estimated_cost', 0),
                "estimated_duration_hours": task.get('estimated_duration_hours', 0),
                "required_resources": task.get('required_resources', {})
            },
            "workflow": {
                "name": workflow['workflow_name'],
                "type": workflow.get('workflow_type', ''),
                "description": workflow.get('workflow_description', '')
            },
            "failure": {
                "reason": failure_reason,
                "timestamp": datetime.utcnow().isoformat()
            },
            "constraints": {
                "available_budget": additional_context.get('available_budget') if additional_context else None,
                "deadline": task.get('deadline'),
                "critical": task['priority'] in ['critical', 'emergency']
            },
            "additional": additional_context or {}
        }
    
    def _generate_llm_plans(
        self,
        context: Dict[str, Any],
        num_plans: int
    ) -> List[Dict[str, Any]]:
        """Generate contingency plans using LLM"""
        prompt = self._build_llm_prompt(context, num_plans)
        
        try:
            response = self.llm_client.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse LLM response
            plans = self._parse_llm_response(content, context)
            
            return plans[:num_plans]
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            logger.info("Falling back to rule-based plans")
            return self._generate_fallback_plans(context, num_plans)
    
    def _build_llm_prompt(self, context: Dict[str, Any], num_plans: int) -> str:
        """Build prompt for LLM contingency plan generation"""
        task = context['task']
        workflow = context['workflow']
        failure = context['failure']
        
        prompt = f"""You are an expert city governance operations planner. A task has failed and needs contingency plans.

WORKFLOW CONTEXT:
- Workflow: {workflow['name']}
- Type: {workflow['type']}
- Description: {workflow.get('description', 'N/A')}

FAILED TASK:
- Title: {task['title']}
- Description: {task.get('description', 'N/A')}
- Department: {task['department']}
- Priority: {task['priority']}
- Estimated Cost: ${task.get('estimated_cost', 0):,.2f}
- Duration: {task.get('estimated_duration_hours', 0)} hours

FAILURE REASON:
{failure['reason']}

CONSTRAINTS:
- Budget: {context['constraints'].get('available_budget', 'Unknown')}
- Deadline: {context['constraints'].get('deadline', 'None specified')}
- Critical: {'Yes' if context['constraints'].get('critical') else 'No'}

TASK:
Generate {num_plans} alternative contingency plans to achieve the same goal. For each plan provide:

1. Plan Name (concise, descriptive)
2. Detailed approach (what to do differently)
3. Alternative resources needed (if any)
4. Estimated cost (be realistic)
5. Estimated duration in hours
6. Risk level (low/medium/high)
7. Success probability (0-100%)
8. Trigger conditions (when to activate this plan)

Focus on practical, actionable alternatives that address the failure reason.

Respond in JSON format:
{{
  "plans": [
    {{
      "name": "Plan name",
      "approach": "Detailed description of alternative approach",
      "alternative_department": "Department name if different, or null",
      "resources": {{"workers": 3, "equipment": ["list"]}},
      "estimated_cost": 50000,
      "estimated_duration_hours": 24,
      "risk_level": "medium",
      "success_probability": 0.85,
      "trigger_conditions": {{"if": "budget_rejected", "threshold": 50000}}
    }}
  ]
}}
"""
        return prompt
    
    def _parse_llm_response(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into structured contingency plans"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            plans = []
            for plan_data in data.get('plans', []):
                plans.append({
                    "plan_name": plan_data.get('name', 'Alternative Plan'),
                    "plan_description": plan_data.get('approach', ''),
                    "alternative_approach": plan_data.get('approach', ''),
                    "alternative_department": plan_data.get('alternative_department'),
                    "alternative_resources": plan_data.get('resources', {}),
                    "estimated_cost": plan_data.get('estimated_cost', 0),
                    "estimated_duration_hours": plan_data.get('estimated_duration_hours', 0),
                    "risk_level": plan_data.get('risk_level', 'medium'),
                    "success_probability": plan_data.get('success_probability', 0.7),
                    "trigger_conditions": plan_data.get('trigger_conditions', {}),
                    "generated_by": "llm",
                    "llm_model": task_config.LLM_MODEL
                })
            
            return plans
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []
    
    def _generate_fallback_plans(
        self,
        context: Dict[str, Any],
        num_plans: int
    ) -> List[Dict[str, Any]]:
        """Generate rule-based contingency plans (fallback when LLM unavailable)"""
        task = context['task']
        failure_reason = context['failure']['reason'].lower()
        
        plans = []
        
        # Plan 1: Extended timeline
        if num_plans >= 1:
            plans.append({
                "plan_name": "Extended Timeline Approach",
                "plan_description": "Extend the timeline and reallocate resources to complete the task with additional time.",
                "alternative_approach": "Request deadline extension and proceed with original plan but with more thorough execution.",
                "alternative_department": None,
                "alternative_resources": task.get('required_resources', {}),
                "estimated_cost": task.get('estimated_cost', 0) * 1.1,  # 10% overhead
                "estimated_duration_hours": int(task.get('estimated_duration_hours', 0) * 1.5),
                "risk_level": "low",
                "success_probability": 0.85,
                "trigger_conditions": {"if": "timeline_insufficient"},
                "generated_by": "rule_based",
                "llm_model": None
            })
        
        # Plan 2: Budget-conscious alternative
        if num_plans >= 2:
            if "budget" in failure_reason or "cost" in failure_reason:
                plans.append({
                    "plan_name": "Reduced Scope Approach",
                    "plan_description": "Scale down the scope to fit within available budget while achieving core objectives.",
                    "alternative_approach": "Focus on essential components only, defer nice-to-have features.",
                    "alternative_department": None,
                    "alternative_resources": {k: int(v * 0.7) if isinstance(v, (int, float)) else v 
                                            for k, v in task.get('required_resources', {}).items()},
                    "estimated_cost": task.get('estimated_cost', 0) * 0.6,
                    "estimated_duration_hours": int(task.get('estimated_duration_hours', 0) * 0.8),
                    "risk_level": "medium",
                    "success_probability": 0.75,
                    "trigger_conditions": {"if": "budget_exceeded", "threshold": task.get('estimated_cost', 0)},
                    "generated_by": "rule_based",
                    "llm_model": None
                })
            else:
                plans.append({
                    "plan_name": "Alternative Resource Approach",
                    "plan_description": "Use different resources or methods to achieve the same goal.",
                    "alternative_approach": "Leverage alternative resources or external partnerships.",
                    "alternative_department": None,
                    "alternative_resources": {},
                    "estimated_cost": task.get('estimated_cost', 0) * 0.9,
                    "estimated_duration_hours": task.get('estimated_duration_hours', 0),
                    "risk_level": "medium",
                    "success_probability": 0.70,
                    "trigger_conditions": {"if": "resources_unavailable"},
                    "generated_by": "rule_based",
                    "llm_model": None
                })
        
        # Plan 3: Emergency/expedited approach
        if num_plans >= 3:
            if task['priority'] in ['critical', 'emergency']:
                plans.append({
                    "plan_name": "Emergency Escalation",
                    "plan_description": "Escalate to emergency protocols with rapid response team and expedited approvals.",
                    "alternative_approach": "Use emergency powers to bypass normal approval chains and deploy rapid response resources.",
                    "alternative_department": None,
                    "alternative_resources": task.get('required_resources', {}),
                    "estimated_cost": task.get('estimated_cost', 0) * 1.5,  # Emergency premium
                    "estimated_duration_hours": int(task.get('estimated_duration_hours', 0) * 0.5),  # Faster
                    "risk_level": "high",
                    "success_probability": 0.80,
                    "trigger_conditions": {"if": "emergency", "priority": "critical"},
                    "generated_by": "rule_based",
                    "llm_model": None
                })
            else:
                plans.append({
                    "plan_name": "Phased Implementation",
                    "plan_description": "Break task into smaller phases and complete incrementally.",
                    "alternative_approach": "Divide work into manageable phases, complete and validate each before proceeding.",
                    "alternative_department": None,
                    "alternative_resources": task.get('required_resources', {}),
                    "estimated_cost": task.get('estimated_cost', 0) * 1.2,
                    "estimated_duration_hours": int(task.get('estimated_duration_hours', 0) * 1.3),
                    "risk_level": "low",
                    "success_probability": 0.90,
                    "trigger_conditions": {"if": "complexity_high"},
                    "generated_by": "rule_based",
                    "llm_model": None
                })
        
        return plans[:num_plans]
    
    def _save_contingency_plan(
        self,
        task_id: str,
        workflow_id: str,
        plan_data: Dict[str, Any],
        plan_order: int
    ) -> Optional[ContingencyPlanResponse]:
        """Save a contingency plan to database"""
        try:
            plan_create = ContingencyPlanCreate(
                task_id=task_id,
                workflow_id=workflow_id,
                plan_name=plan_data['plan_name'],
                plan_description=plan_data['plan_description'],
                plan_order=plan_order,
                trigger_conditions=plan_data.get('trigger_conditions', {}),
                alternative_approach=plan_data['alternative_approach'],
                alternative_department=plan_data.get('alternative_department'),
                alternative_resources=plan_data.get('alternative_resources', {}),
                estimated_cost=plan_data.get('estimated_cost'),
                estimated_duration_hours=plan_data.get('estimated_duration_hours'),
                risk_level=plan_data.get('risk_level', 'medium'),
                success_probability=plan_data.get('success_probability', 0.7),
                generated_by=plan_data.get('generated_by', 'llm')
            )
            
            plan_id = self.queries.create_contingency_plan(plan_create.dict())
            
            if plan_id:
                # Fetch saved plan
                plans = self.queries.get_task_contingency_plans(task_id)
                saved_plan = next((p for p in plans if str(p['plan_id']) == plan_id), None)
                
                if saved_plan:
                    return ContingencyPlanResponse(**saved_plan)
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to save contingency plan: {e}")
            return None
    
    # ==================== CONTINGENCY ACTIVATION ====================
    
    def activate_contingency_plan(
        self,
        plan_id: str,
        activated_by: str = "system",
        reason: Optional[str] = None
    ) -> bool:
        """
        Activate a contingency plan
        
        Marks plan as active and creates a new task based on the contingency
        """
        logger.info(f"Activating contingency plan {plan_id}")
        
        # Get plan details
        plans = self.queries.get_task_contingency_plans(None)  # Get all
        plan = next((p for p in plans if str(p['plan_id']) == plan_id), None)
        
        if not plan:
            logger.error(f"Plan {plan_id} not found")
            return False
        
        # Update plan status
        from .database import get_db
        db = get_db()
        
        update_query = """
            UPDATE contingency_plans
            SET status = 'active', activated_at = CURRENT_TIMESTAMP
            WHERE plan_id = %s
        """
        db.execute_query(update_query, (plan_id,), fetch_all=False)
        
        logger.info(f"✓ Contingency plan {plan_id} activated by {activated_by}")
        
        # TODO: Create new task based on contingency plan
        # This will be implemented when we have the full task creation flow
        
        return True
    
    def evaluate_plan_triggers(
        self,
        task_id: str,
        current_situation: Dict[str, Any]
    ) -> Optional[str]:
        """
        Evaluate if any contingency plans should be triggered
        
        Args:
            task_id: Task to check
            current_situation: Current state/context
        
        Returns:
            plan_id of best matching plan, or None
        """
        plans = self.queries.get_task_contingency_plans(task_id)
        
        if not plans:
            return None
        
        # Check trigger conditions for each plan
        for plan in plans:
            if plan['status'] != 'ready':
                continue
            
            triggers = plan.get('trigger_conditions', {})
            
            if self._check_triggers(triggers, current_situation):
                logger.info(f"Contingency plan {plan['plan_id']} triggered")
                return str(plan['plan_id'])
        
        return None
    
    def _check_triggers(
        self,
        triggers: Dict[str, Any],
        situation: Dict[str, Any]
    ) -> bool:
        """Check if trigger conditions are met"""
        if not triggers:
            return False
        
        # Simple trigger matching
        if 'if' in triggers:
            condition = triggers['if']
            
            # Check if condition exists in situation
            if condition in situation:
                # Check threshold if present
                if 'threshold' in triggers:
                    return situation.get(condition, 0) >= triggers['threshold']
                return bool(situation.get(condition))
        
        return False
    
    # ==================== PLAN MANAGEMENT ====================
    
    def get_task_plans(self, task_id: str) -> List[ContingencyPlanResponse]:
        """Get all contingency plans for a task"""
        plans = self.queries.get_task_contingency_plans(task_id)
        return [ContingencyPlanResponse(**p) for p in plans]
    
    def rank_plans(
        self,
        plans: List[ContingencyPlanResponse],
        criteria: Optional[Dict[str, float]] = None
    ) -> List[ContingencyPlanResponse]:
        """
        Rank contingency plans by desirability
        
        Args:
            plans: List of plans to rank
            criteria: Weighting for ranking {risk: 0.3, cost: 0.3, success: 0.4}
        
        Returns:
            Sorted list (best first)
        """
        if not criteria:
            criteria = {
                "risk": 0.25,
                "cost": 0.25,
                "success": 0.35,
                "duration": 0.15
            }
        
        def calculate_score(plan: ContingencyPlanResponse) -> float:
            # Risk score (lower is better)
            risk_scores = {"low": 1.0, "medium": 0.6, "high": 0.3}
            risk_score = risk_scores.get(plan.risk_level, 0.5)
            
            # Cost score (lower is better, normalized)
            max_cost = max((p.estimated_cost or 0) for p in plans)
            cost_score = 1.0 - ((plan.estimated_cost or 0) / max_cost if max_cost > 0 else 0)
            
            # Success score (higher is better)
            success_score = plan.success_probability or 0.5
            
            # Duration score (shorter is better, normalized)
            max_duration = max((p.estimated_duration_hours or 0) for p in plans)
            duration_score = 1.0 - ((plan.estimated_duration_hours or 0) / max_duration if max_duration > 0 else 0)
            
            # Weighted total
            total = (
                risk_score * criteria.get("risk", 0.25) +
                cost_score * criteria.get("cost", 0.25) +
                success_score * criteria.get("success", 0.35) +
                duration_score * criteria.get("duration", 0.15)
            )
            
            return total
        
        # Sort by score (highest first)
        ranked = sorted(plans, key=calculate_score, reverse=True)
        
        return ranked


# Singleton instance
_contingency_planner = None


def get_contingency_planner() -> ContingencyPlanner:
    """Get contingency planner singleton"""
    global _contingency_planner
    if _contingency_planner is None:
        _contingency_planner = ContingencyPlanner()
    return _contingency_planner
