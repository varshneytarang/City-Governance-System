from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
import operator


class GovernanceState(TypedDict):
    """State for the governance workflow"""
    messages: Annotated[list, operator.add]
    current_step: str
    data: dict


def analyze_request(state: GovernanceState) -> GovernanceState:
    """Analyze incoming governance request"""
    print(f"Analyzing request: {state.get('current_step', 'initial')}")
    
    state["messages"].append(
        AIMessage(content="Request analyzed successfully")
    )
    state["current_step"] = "analysis_complete"
    
    return state


def process_governance(state: GovernanceState) -> GovernanceState:
    """Process governance decision"""
    print(f"Processing governance at step: {state.get('current_step')}")
    
    state["messages"].append(
        AIMessage(content="Governance process completed")
    )
    state["current_step"] = "processed"
    
    return state


def should_continue(state: GovernanceState) -> str:
    """Determine if workflow should continue"""
    if state.get("current_step") == "analysis_complete":
        return "process"
    return "end"


# Build the LangGraph workflow
def create_governance_workflow():
    """Create and return the governance workflow graph"""
    
    workflow = StateGraph(GovernanceState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_request)
    workflow.add_node("process", process_governance)
    
    # Add edges
    workflow.set_entry_point("analyze")
    workflow.add_conditional_edges(
        "analyze",
        should_continue,
        {
            "process": "process",
            "end": END
        }
    )
    workflow.add_edge("process", END)
    
    return workflow.compile()


# Example usage
if __name__ == "__main__":
    # Create the workflow
    governance_graph = create_governance_workflow()
    
    # Test the workflow
    initial_state = {
        "messages": [HumanMessage(content="New governance request")],
        "current_step": "initial",
        "data": {}
    }
    
    result = governance_graph.invoke(initial_state)
    print("\n=== Workflow Result ===")
    print(f"Final step: {result['current_step']}")
    print(f"Messages: {len(result['messages'])}")
    for msg in result['messages']:
        print(f"  - {msg.content}")
