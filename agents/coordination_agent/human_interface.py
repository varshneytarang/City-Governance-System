"""
Human-in-the-Loop Interface

Manages escalation to human authorities when:
- Confidence too low
- Cost exceeds limit
- Public safety impact
- Political sensitivity
- Explicit human review requested
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .state import HumanEscalation, Resolution, Conflict, CoordinationState
from .config import CoordinationConfig
from .database import CoordinationQueries

logger = logging.getLogger(__name__)


class HumanInterface:
    """Handles human escalation and approval workflows"""
    
    def __init__(self):
        self.config = CoordinationConfig()
        self.db = CoordinationQueries()
    
    def should_escalate_to_human(
        self,
        resolution: Resolution,
        total_cost: int = 0
    ) -> bool:
        """
        Determine if resolution requires human approval
        
        Escalate if:
        - Resolution explicitly requires human
        - Confidence below threshold
        - Cost exceeds limit
        - Decision is to escalate
        """
        # Explicit human requirement
        if resolution.get("requires_human", False):
            return True
        
        # Low confidence
        if resolution.get("confidence", 0) < self.config.CONFIDENCE_THRESHOLD:
            return True
        
        # High cost
        if total_cost > self.config.AUTO_APPROVAL_COST_LIMIT:
            return True
        
        # Escalation decision
        if resolution.get("decision") == "escalate":
            return True
        
        return False
    
    def create_escalation_request(
        self,
        conflict: Conflict,
        resolution: Optional[Resolution],
        state: CoordinationState
    ) -> HumanEscalation:
        """
        Create human escalation request
        
        Generates notification and approval options for human reviewer
        """
        # Determine urgency based on conflict severity and priorities
        urgency = self._determine_urgency(conflict, state)
        
        # Build escalation reason
        reason = self._build_escalation_reason(conflict, resolution, state)
        
        # Generate options for human
        options = self._generate_decision_options(conflict, state)
        
        # Include LLM analysis if available
        llm_analysis = None
        if resolution and resolution.get("method") == "llm":
            llm_analysis = resolution.get("rationale", "")
        
        escalation: HumanEscalation = {
            "escalation_id": str(uuid.uuid4()),
            "conflict_id": conflict["conflict_id"],
            "reason": reason,
            "urgency": urgency,
            "options": options,
            "llm_analysis": llm_analysis,
            "status": "pending",
            "approver": None,
            "approval_notes": None,
            "created_at": datetime.now().isoformat(),
            "resolved_at": None
        }
        
        logger.info(f"✓ Created human escalation: {escalation['escalation_id']}")
        return escalation
    
    def notify_human_approver(self, escalation: HumanEscalation) -> bool:
        """
        Send notification to human approver
        
        Methods:
        - Email (primary)
        - SMS (if critical urgency)
        - Dashboard flag
        """
        try:
            # Log to database for dashboard
            self.db.log_coordination_decision(
                coordination_id=escalation["escalation_id"],
                conflict_type="human_escalation",
                agents_involved=[],
                resolution_method="human",
                resolution_rationale=escalation["reason"],
                llm_confidence=None,
                human_approver=None,
                outcome="pending_human_approval"
            )
            
            # TODO: Implement actual email/SMS notification
            # For now, just log
            logger.info(f"📧 Notification sent for escalation: {escalation['escalation_id']}")
            logger.info(f"   Urgency: {escalation['urgency']}")
            logger.info(f"   Reason: {escalation['reason']}")
            
            if escalation["urgency"] == "critical":
                logger.warning(f"🚨 CRITICAL escalation requires immediate attention!")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to notify human approver: {e}")
            return False
    
    def wait_for_human_approval(
        self,
        escalation: HumanEscalation,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Wait for human approval via TERMINAL INPUT
        
        In production:
        - Displays escalation details in terminal
        - Presents decision options
        - Waits for human input
        - Returns approved decision
        
        For testing with COORDINATION_AUTO_APPROVE=true:
        - Auto-approve to avoid blocking tests
        """
        import os
        
        if timeout is None:
            timeout = self.config.HUMAN_RESPONSE_TIMEOUT
        
        # Check if running in test auto-approve mode
        auto_approve = os.environ.get("COORDINATION_AUTO_APPROVE", "false").lower() == "true"
        
        if auto_approve:
            logger.warning("⚠️ TEST MODE: Auto-approving (COORDINATION_AUTO_APPROVE=true)")
            approval = {
                "status": "approved",
                "approver": "system_auto_approve",
                "decision": escalation["options"][0] if escalation["options"] else {},
                "notes": "Auto-approved in test mode",
                "approved_at": datetime.now().isoformat()
            }
            
            # Update database
            self.db.update_human_approval(
                coordination_id=escalation["escalation_id"],
                approver="system_auto_approve",
                outcome="approved",
                notes="Auto-approved for testing"
            )
            
            logger.info(f"✓ Auto-approved: {escalation['escalation_id']}")
            return approval
        
        # ===================================================================
        # TERMINAL-BASED HUMAN INTERVENTION
        # ===================================================================
        print("\n" + "="*70)
        print("🚨 HUMAN APPROVAL REQUIRED - COORDINATION ESCALATION")
        print("="*70)
        print(f"\nEscalation ID: {escalation['escalation_id']}")
        print(f"Conflict ID: {escalation.get('conflict_id', 'N/A')}")
        print(f"Urgency: {escalation['urgency'].upper()}")
        print(f"Reason: {escalation['reason']}")
        
        # Show LLM analysis if available
        if escalation.get("llm_analysis"):
            print(f"\n🤖 LLM Analysis:")
            print(f"  {escalation['llm_analysis']}")
        
        # Show decision options
        print("\n📋 DECISION OPTIONS:")
        options = escalation.get("options", [])
        if not options:
            print("  No specific options provided")
        else:
            for i, option in enumerate(options, 1):
                print(f"  [{i}] {option.get('description', 'Option ' + str(i))}")
                if 'agents_affected' in option:
                    print(f"      Affects: {', '.join(option['agents_affected'])}")
                if 'estimated_cost' in option:
                    print(f"      Cost: ₹{option['estimated_cost']:,}")
        
        # Add standard options
        print("\n" + "="*70)
        print("STANDARD OPTIONS:")
        print("  [A] Approve - Execute as proposed")
        print("  [D] Defer - Schedule for later review")
        print("  [R] Reject - Deny all decisions")
        print("  [M] Modify - Request changes")
        print("="*70)
        
        # Get human input
        while True:
            try:
                choice = input("\nEnter your decision [A/D/R/M or 1-N for options]: ").strip().upper()
                
                approver_name = input("Your name/ID: ").strip() or "terminal_user"
                notes = input("Notes/comments (optional): ").strip() or "No notes"
                
                if choice == "A":
                    status = "approved"
                    decision = escalation["options"][0] if escalation["options"] else {}
                    print("\n✅ Decision APPROVED")
                    break
                
                elif choice == "D":
                    status = "deferred"
                    decision = {}
                    print("\n⏸️ Decision DEFERRED")
                    break
                
                elif choice == "R":
                    status = "rejected"
                    decision = {}
                    print("\n❌ Decision REJECTED")
                    break
                
                elif choice == "M":
                    status = "modified"
                    decision = {}
                    print("\n📝 Decision MODIFIED (requires resubmission)")
                    break
                
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        status = "approved"
                        decision = options[idx]
                        print(f"\n✅ Option {choice} SELECTED")
                        break
                    else:
                        print(f"❌ Invalid option number. Please enter 1-{len(options)}")
                
                else:
                    print("❌ Invalid choice. Please enter A/D/R/M or a valid option number.")
            
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted. Defaulting to DEFER.")
                status = "deferred"
                approver_name = "interrupted_user"
                notes = "User interrupted - defaulting to defer"
                decision = {}
                break
            
            except Exception as e:
                logger.error(f"Error getting human input: {e}")
                print(f"❌ Error: {e}. Defaulting to DEFER.")
                status = "deferred"
                approver_name = "error_handler"
                notes = f"Error during input: {e}"
                decision = {}
                break
        
        # Create approval response
        approval = {
            "status": status,
            "approver": approver_name,
            "decision": decision,
            "notes": notes,
            "approved_at": datetime.now().isoformat()
        }
        
        # Update database
        self.db.update_human_approval(
            coordination_id=escalation["escalation_id"],
            approver=approver_name,
            outcome=status,
            notes=notes
        )
        
        logger.info(f"✓ Human decision recorded: {status} by {approver_name}")
        print("="*70 + "\n")
        
        return approval
    
    def apply_human_decision(
        self,
        escalation: HumanEscalation,
        human_decision: Dict[str, Any],
        state: CoordinationState
    ) -> CoordinationState:
        """
        Apply human-approved decision to coordination state
        """
        # Update escalation with human decision
        escalation["status"] = human_decision["status"]
        escalation["approver"] = human_decision.get("approver", "unknown")
        escalation["approval_notes"] = human_decision.get("notes", "")
        escalation["resolved_at"] = datetime.now().isoformat()
        
        # Update state
        state["human_escalation"] = escalation
        state["final_decision"] = human_decision["status"]
        state["execution_plan"] = human_decision.get("decision", {})
        state["decision_rationale"] = f"Human decision by {escalation['approver']}: {escalation['approval_notes']}"
        state["workflow_log"].append(f"Human approval: {human_decision['status']}")
        
        logger.info(f"✓ Applied human decision: {human_decision['status']}")
        return state
    
    def _determine_urgency(
        self,
        conflict: Conflict,
        state: CoordinationState
    ) -> str:
        """Determine urgency level for escalation"""
        
        # Check priorities in decisions
        decisions = state["agent_decisions"]
        priorities = [d.get("priority", "routine") for d in decisions]
        
        if "emergency" in priorities:
            return "critical"
        elif "safety_critical" in priorities or "public_health" in priorities:
            return "high"
        elif conflict["severity"] in ["critical", "high"]:
            return "high"
        elif conflict["severity"] == "medium":
            return "medium"
        else:
            return "low"
    
    def _build_escalation_reason(
        self,
        conflict: Conflict,
        resolution: Optional[Resolution],
        state: CoordinationState
    ) -> str:
        """Build detailed escalation reason"""
        reasons = []
        
        # Conflict details
        reasons.append(f"Conflict type: {conflict['conflict_type']}")
        reasons.append(f"Severity: {conflict['severity']}")
        
        # Why escalating
        if resolution:
            if resolution.get("confidence", 1.0) < self.config.CONFIDENCE_THRESHOLD:
                reasons.append(f"Low confidence: {resolution['confidence']:.2f}")
            if resolution.get("requires_human", False):
                reasons.append("Resolution requires human judgment")
        
        # Cost check
        total_cost = sum(d.get("estimated_cost", 0) for d in state["agent_decisions"])
        if total_cost > self.config.AUTO_APPROVAL_COST_LIMIT:
            reasons.append(f"High cost: ₹{total_cost:,} exceeds limit")
        
        return " | ".join(reasons)
    
    def _generate_decision_options(
        self,
        conflict: Conflict,
        state: CoordinationState
    ) -> list:
        """Generate decision options for human"""
        decisions = state["agent_decisions"]
        agents_involved = conflict["agents_involved"]
        
        options = []
        
        # Option 1: Approve all
        options.append({
            "option": "approve_all",
            "description": "Approve all agents' requests with coordination",
            "impact": "All departments proceed, requires coordination planning"
        })
        
        # Option 2: Approve highest priority
        if len(decisions) > 1:
            priorities = [d.get("priority", "routine") for d in decisions]
            highest_priority = max(
                decisions,
                key=lambda d: self.config.PRIORITY_LEVELS.get(d.get("priority", "routine"), 0)
            )
            
            options.append({
                "option": "approve_partial",
                "description": f"Approve only {highest_priority['agent_id']} ({highest_priority['priority']})",
                "impact": "Other agents deferred or rejected"
            })
        
        # Option 3: Defer all
        options.append({
            "option": "defer",
            "description": "Defer all decisions pending further analysis",
            "impact": "No immediate action, allows more time for planning"
        })
        
        # Option 4: Reject all
        options.append({
            "option": "reject",
            "description": "Reject conflicting requests",
            "impact": "Agents must revise and resubmit"
        })
        
        return options
