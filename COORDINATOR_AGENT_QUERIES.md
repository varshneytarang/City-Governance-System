# Coordination Agent: Bidirectional Agent Communication

## Overview

The Coordination Agent now has the ability to **call other agents** to gather information during conflict resolution. This enables truly intelligent, context-aware coordination.

## What's New

### Before
```
Agents → Coordinator → Decision
   ↓
(One-way communication)
```

### After
```
Agents ⇄ Coordinator ⇄ Agents
   ↕         ↕         ↕
(Bidirectional communication)
```

The coordinator can now:
- ✅ Query any agent for information
- ✅ Request status updates from multiple agents
- ✅ Gather context before making coordination decisions
- ✅ Ask agents for details during conflict resolution

## Architecture

### Components

#### 1. AgentDispatcher
**File:** `coordination_agent/agent_dispatcher.py`

Handles dynamic agent loading and query routing:
- Lazy-loads agent classes to avoid circular imports
- Caches agent instances for efficiency
- Routes queries to appropriate agents
- Handles errors gracefully

#### 2. Coordination Agent Integration
**File:** `coordination_agent/agent.py` (enhanced)

New methods added:
- `query_agent()` - Query single agent
- `query_multiple_agents()` - Query multiple agents
- `get_agent_status()` - Get agent metadata
- `gather_agent_context()` - Gather context for location

## Usage Examples

### Example 1: Query Single Agent

```python
from coordination_agent.agent import CoordinationAgent

coordinator = CoordinationAgent()

# Ask Water agent about capacity
response = coordinator.query_agent(
    agent_type="water",
    request={
        "type": "capacity_query",
        "location": "Downtown",
        "query": "What is current water capacity?"
    },
    reason="Checking capacity for conflict resolution"
)

print(f"Response: {response}")
# {
#     "success": True,
#     "agent_type": "water",
#     "response": {...},
#     "duration_seconds": 2.5
# }
```

### Example 2: Query Multiple Agents

```python
# Ask multiple agents about Downtown simultaneously
responses = coordinator.query_multiple_agents(
    queries={
        "water": {
            "type": "capacity_query",
            "location": "Downtown"
        },
        "engineering": {
            "type": "project_planning",
            "location": "Downtown"
        },
        "fire": {
            "type": "readiness_assessment",
            "location": "Downtown"
        }
    },
    reason="Gathering comprehensive Downtown context"
)

for agent_type, response in responses.items():
    if response['success']:
        print(f"{agent_type}: {response['response']['decision']}")
```

### Example 3: Gather Location Context

```python
# Gather context from all agents about a location
context = coordinator.gather_agent_context(
    agent_types=["water", "engineering", "sanitation"],
    location="Downtown",
    context_type="capacity_query"
)

print(f"Context from {context['successful_responses']} agents")
```

### Example 4: During Conflict Resolution

```python
# When conflict detected, query involved agents for details
def resolve_location_conflict(self, conflict):
    """Enhanced conflict resolution with agent queries"""
    
    location = conflict['location']
    agents_involved = conflict['agents_involved']
    
    # Step 1: Gather context from all involved agents
    context = self.gather_agent_context(
        agent_types=agents_involved,
        location=location,
        context_type="capacity_query"
    )
    
    # Step 2: Analyze responses
    priorities = {}
    for agent_type, response in context['responses'].items():
        if response['success']:
            agent_data = response['response']
            priorities[agent_type] = agent_data.get('priority', 'normal')
    
    # Step 3: Make informed decision
    high_priority_agent = max(priorities, key=lambda k: priority_score(priorities[k]))
    
    # Step 4: Notify other agents to reschedule
    for agent_type in agents_involved:
        if agent_type != high_priority_agent:
            self.query_agent(
                agent_type,
                {
                    "type": "schedule_adjustment",
                    "reason": f"{high_priority_agent} has priority in {location}",
                    "suggested_alternative": "Schedule after completion"
                },
                reason="Conflict resolution notification"
            )
    
    return f"{high_priority_agent} proceeds, others reschedule"
```

## Use Cases

### 1. Conflict Resolution Enhancement

**Before:** Coordinator makes decisions based only on initial requests
**After:** Coordinator queries agents for current status, priorities, and constraints

```python
# Conflict: Water and Engineering both want Downtown
water_status = coordinator.query_agent("water", {
    "type": "capacity_query",
    "location": "Downtown"
})

eng_status = coordinator.query_agent("engineering", {
    "type": "project_planning",
    "location": "Downtown"
})

# Now make informed decision based on actual agent state
```

### 2. Budget Validation

**Scenario:** Engineering requests $100k budget, coordinator asks Finance to verify

```python
finance_check = coordinator.query_agent("finance", {
    "type": "budget_approval",
    "amount": 100000,
    "requesting_department": "engineering",
    "location": "Downtown"
})

if finance_check['response']['fiscal_feasible']:
    # Approve Engineering's request
else:
    # Suggest alternative or escalate
```

### 3. Resource Availability Check

**Scenario:** Multiple agents need same resource, coordinator checks availability

```python
# Check with all agents about resource usage
responses = coordinator.query_multiple_agents({
    "water": {"type": "capacity_query", "resource": "excavation_equipment"},
    "engineering": {"type": "capacity_query", "resource": "excavation_equipment"},
    "sanitation": {"type": "capacity_query", "resource": "excavation_equipment"}
})

# Determine who has equipment, who needs it, schedule accordingly
```

### 4. Emergency Coordination

**Scenario:** Fire emergency in Downtown, coordinator queries all agents

```python
# Emergency: Fire in Downtown
context = coordinator.gather_agent_context(
    agent_types=["water", "fire", "health", "engineering"],
    location="Downtown",
    context_type="emergency_response"
)

# Water: Ensure hydrants operational
# Fire: Deploy response team
# Health: Prepare medical support
# Engineering: Close roads for access
```

## API Reference

### CoordinationAgent Methods

#### `query_agent(agent_type, request, reason=None)`
Query a single agent.

**Parameters:**
- `agent_type` (str): Agent to query (water, engineering, fire, etc.)
- `request` (dict): Request to send to agent
- `reason` (str, optional): Reason for query (logging)

**Returns:**
```python
{
    "success": bool,
    "agent_type": str,
    "response": dict,  # Agent's response
    "duration_seconds": float,
    "timestamp": str
}
```

#### `query_multiple_agents(queries, reason=None)`
Query multiple agents simultaneously.

**Parameters:**
- `queries` (dict): Mapping of agent_type → request
- `reason` (str, optional): Reason for queries

**Returns:**
```python
{
    "agent_type1": {...},  # Response from agent1
    "agent_type2": {...},  # Response from agent2
    ...
}
```

#### `gather_agent_context(agent_types, location, context_type)`
Gather context from multiple agents about a location.

**Parameters:**
- `agent_types` (list): List of agent types to query
- `location` (str): Location to ask about
- `context_type` (str): Type of query

**Returns:**
```python
{
    "location": str,
    "agents_queried": list,
    "responses": dict,
    "successful_responses": int,
    "timestamp": str
}
```

#### `get_agent_status(agent_type)`
Get metadata about an agent.

**Parameters:**
- `agent_type` (str): Agent type

**Returns:**
```python
{
    "agent_type": str,
    "version": str,
    "available": bool
}
```

## Testing

### Run Comprehensive Test
```bash
python test_coordinator_agent_queries.py
```

### Test Coverage
1. ✅ Single agent query
2. ✅ Multiple agent queries
3. ✅ Context gathering
4. ✅ Conflict resolution with queries

## Performance Considerations

### Agent Caching
- Agent instances are cached after first use
- Reduces initialization overhead
- Call `coordinator.agent_dispatcher.clear_cache()` to reset

### Parallel Queries
- `query_multiple_agents()` could be enhanced for true parallelism
- Currently executes sequentially
- Future: Use asyncio for concurrent queries

### Timeout Handling
- Default timeout: 30 seconds per agent query
- Configure via dispatcher settings
- Graceful degradation if agent unavailable

## Benefits

✅ **Informed Decisions** - Coordinator makes decisions based on actual agent state
✅ **Dynamic Coordination** - Adapt to real-time conditions
✅ **Reduced Conflicts** - Query agents before conflicts escalate
✅ **Better Resource Management** - Understand resource availability across departments
✅ **Enhanced Transparency** - All queries logged for audit trail

## Future Enhancements

### 1. Async Agent Queries
```python
# Future: Truly parallel agent queries
responses = await coordinator.query_agents_async({...})
```

### 2. Agent Subscriptions
```python
# Future: Agents subscribe to coordination events
coordinator.subscribe(agent_type="water", event="budget_approved")
```

### 3. Agent Callbacks
```python
# Future: Agents can callback to coordinator
def on_completion(result):
    coordinator.notify_completion(agent_type, result)
```

### 4. LLM Integration
```python
# Future: LLM decides which agents to query
llm_recommendation = llm.suggest_agents_to_query(conflict)
responses = coordinator.query_multiple_agents(llm_recommendation)
```

## Conclusion

The Coordination Agent can now engage in **bidirectional communication** with all department agents, enabling:
- Context-aware conflict resolution
- Real-time information gathering
- Dynamic coordination based on actual agent state
- More intelligent decision-making

This transforms the coordinator from a passive arbiter to an **active orchestrator** that can gather information and make truly informed decisions.
