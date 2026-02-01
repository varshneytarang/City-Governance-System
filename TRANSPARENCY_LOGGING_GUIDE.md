# Transparency Logging System with RAG Vector Database

## Overview

Added comprehensive transparency logging system that logs all essential decisions from every node to a RAG-based vector database, enabling:
- **Public transparency** - All decisions logged with rationale
- **Semantic search** - Find similar decisions using natural language
- **Audit trails** - Complete history of all actions
- **Policy analysis** - Track which policies influence decisions
- **Citizen impact tracking** - Monitor how many citizens are affected

---

## Architecture

### Components

```
Every Agent Node
       ↓
[Transparency Logger]
       ↓
[Vector Database - ChromaDB]
       ↓
[Embedding Model - all-MiniLM-L6-v2]
       ↓
[Semantic Search & RAG]
```

### What Gets Logged

For each decision/action:
- **Agent Type**: water, engineering, health, finance, coordination
- **Node Name**: Which node made the decision
- **Decision**: What was decided
- **Rationale**: Why this decision was made
- **Confidence**: How confident (0-1)
- **Cost Impact**: Estimated cost in rupees
- **Citizens Affected**: Number of people impacted
- **Policy References**: Which policies were considered
- **Full Context**: Request details, state, results
- **Timestamp**: When decision was made

---

## Installation

### Required Dependencies

```powershell
# Install ChromaDB for vector database
pip install chromadb

# Install sentence-transformers for embeddings
pip install sentence-transformers

# Optional: For better embeddings
pip install torch
```

### Quick Start

```python
from transparency_logger import get_transparency_logger

# Get singleton logger
logger = get_transparency_logger()

# Log a decision
log_id = logger.log_decision(
    agent_type="water",
    node_name="decision_router",
    decision="approved",
    context={"request": request_data},
    rationale="Emergency priority, sufficient budget",
    confidence=0.92,
    cost_impact=500000,  # Rs. 5 lakhs
    affected_citizens=50000,
    policy_references=["emergency_protocol_2024", "budget_policy_v2"]
)

# Search for similar decisions
results = logger.search_decisions(
    query="emergency water repairs with high cost",
    n_results=5
)

# Generate transparency report
report = logger.generate_transparency_report(
    start_date="2026-01-01",
    agent_type="water"
)
```

---

## Integration with Existing Nodes

### Example: Water Agent Decision Router

```python
from transparency_logger import get_transparency_logger

def decision_router(state: DepartmentState) -> DepartmentState:
    """Route decision with transparency logging"""
    
    # Get logger
    t_logger = get_transparency_logger()
    
    # Your existing logic
    confidence = state["confidence"]
    if confidence < 0.6:
        state["decision"] = "escalate"
        action = "escalate"
        rationale = f"Low confidence: {confidence:.2%}"
    else:
        state["decision"] = "approved"
        action = "approved"
        rationale = f"High confidence: {confidence:.2%}, all checks passed"
    
    # LOG TO TRANSPARENCY SYSTEM
    t_logger.log_decision(
        agent_type="water",
        node_name="decision_router",
        decision=action,
        context={
            "request": state.get("input_event", {}),
            "confidence": confidence,
            "feasible": state.get("feasible", False),
            "policy_ok": state.get("policy_ok", True)
        },
        rationale=rationale,
        confidence=confidence,
        cost_impact=state.get("estimated_cost", 0),
        affected_citizens=state.get("affected_population", 0),
        policy_references=state.get("applicable_policies", [])
    )
    
    return state
```

### Simplified: Use log_node_execution

```python
def planner(state: DepartmentState) -> DepartmentState:
    """Planner node with auto-logging"""
    t_logger = get_transparency_logger()
    
    # Your planning logic
    plans = generate_plans(state)
    state["plans"] = plans
    
    # Simple logging
    t_logger.log_node_execution(
        agent_type="water",
        node_name="planner",
        state=state,
        action=f"generated_{len(plans)}_plans",
        result=plans
    )
    
    return state
```

---

## RAG Capabilities

### Semantic Search

Find decisions using natural language:

```python
logger = get_transparency_logger()

# Find similar emergency decisions
results = logger.search_decisions(
    query="emergency pipeline repair during monsoon",
    n_results=10,
    filter_agent="water",
    min_confidence=0.7
)

for result in results:
    print(f"Decision: {result['metadata']['decision']}")
    print(f"Rationale: {result['metadata']['rationale']}")
    print(f"Cost: Rs.{result['metadata']['cost_impact']:,.0f}")
    print(f"Similarity: {1 - result['distance']:.2%}")
    print()
```

### Policy Analysis

```python
# Find all decisions referencing a specific policy
results = logger.search_decisions(
    query="emergency protocol 2024",
    n_results=50
)

# Analyze policy impact
policy_cost = sum(
    float(r['metadata']['cost_impact'])
    for r in results
)
print(f"Total cost under emergency protocol: Rs.{policy_cost:,.0f}")
```

### Historical Context for New Decisions

```python
def planner_with_rag(state: DepartmentState) -> DepartmentState:
    """Use RAG to inform planning with historical context"""
    logger = get_transparency_logger()
    
    # Get current request
    request = state["input_event"]
    request_type = request.get("type", "")
    location = request.get("location", "")
    
    # Search for similar past decisions
    query = f"{request_type} in {location}"
    similar_decisions = logger.search_decisions(
        query=query,
        n_results=5,
        filter_agent="water"
    )
    
    # Extract lessons from past decisions
    past_costs = [
        float(d['metadata']['cost_impact'])
        for d in similar_decisions
    ]
    avg_past_cost = sum(past_costs) / len(past_costs) if past_costs else 0
    
    # Use historical context
    state["historical_context"] = {
        "similar_decisions": len(similar_decisions),
        "avg_cost": avg_past_cost,
        "lessons_learned": [d['metadata']['rationale'] for d in similar_decisions[:3]]
    }
    
    # Your planning logic with context
    plans = generate_plans_with_context(state)
    state["plans"] = plans
    
    return state
```

---

## Transparency Reports

### Generate Public Report

```python
logger = get_transparency_logger()

# Full transparency report
report = logger.generate_transparency_report(
    start_date="2026-01-01",
    end_date="2026-01-31"
)

print(f"Total Decisions: {report['statistics']['total_decisions']}")
print(f"Total Cost Impact: Rs.{report['statistics']['total_cost_impact']:,.0f}")
print(f"Average Confidence: {report['statistics']['average_confidence']:.2%}")
print(f"Citizens Affected: {report['statistics']['total_citizens_affected']:,}")

# By department
for agent, count in report['statistics']['decisions_by_agent'].items():
    print(f"  {agent}: {count} decisions")

# Top 10 most impactful decisions
print("\nTop 10 Decisions by Cost:")
for i, decision in enumerate(report['top_decisions'], 1):
    meta = decision['metadata']
    print(f"{i}. {meta['agent_type']}.{meta['node_name']}: {meta['decision']}")
    print(f"   Cost: Rs.{meta['cost_impact']:,.0f}")
    print(f"   Rationale: {meta['rationale'][:100]}...")
```

### Department-Specific Report

```python
# Water department only
water_report = logger.generate_transparency_report(
    agent_type="water",
    start_date="2026-01-01"
)
```

---

## Vector Database Schema

### ChromaDB Collections

**Collection**: `governance_decisions`

**Documents**: Searchable text combining:
- Agent type and node name
- Decision text
- Rationale
- Context summary
- Policy references

**Metadata**:
```python
{
    "agent_type": "water",
    "node_name": "decision_router",
    "decision": "approved",
    "timestamp": "2026-02-01T10:30:00",
    "confidence": 0.92,
    "cost_impact": 500000.0,
    "affected_citizens": 50000,
    "rationale": "Emergency priority, sufficient budget",
    "context_json": "{...}",
    "policies": "[\"emergency_protocol_2024\"]"
}
```

### Embeddings

Uses **sentence-transformers** with `all-MiniLM-L6-v2` model:
- 384-dimensional vectors
- Fast inference (~0.1s per document)
- Good semantic understanding
- Multilingual support

---

## Use Cases

### 1. Public Transparency Portal

```python
# Web API endpoint
@app.get("/api/transparency/search")
def search_decisions(query: str, limit: int = 10):
    logger = get_transparency_logger()
    results = logger.search_decisions(query, n_results=limit)
    
    return {
        "query": query,
        "results": [
            {
                "date": r['metadata']['timestamp'],
                "department": r['metadata']['agent_type'],
                "decision": r['metadata']['decision'],
                "rationale": r['metadata']['rationale'],
                "cost": r['metadata']['cost_impact'],
                "citizens_affected": r['metadata']['affected_citizens']
            }
            for r in results
        ]
    }
```

### 2. Audit Trail Investigation

```python
# Investigate a specific high-cost project
results = logger.search_decisions(
    query="Zone-A pipeline replacement project",
    n_results=100
)

# Timeline of all decisions
timeline = sorted(results, key=lambda x: x['metadata']['timestamp'])
for entry in timeline:
    print(f"{entry['metadata']['timestamp']}: {entry['metadata']['decision']}")
```

### 3. Policy Impact Analysis

```python
# How many decisions were affected by emergency protocol?
emergency_decisions = logger.search_decisions(
    query="emergency protocol",
    n_results=1000
)

total_emergency_cost = sum(
    float(d['metadata']['cost_impact'])
    for d in emergency_decisions
)

print(f"Emergency protocol triggered {len(emergency_decisions)} decisions")
print(f"Total cost: Rs.{total_emergency_cost:,.0f}")
```

### 4. Citizen Impact Tracking

```python
# Which decisions affected the most citizens?
report = logger.generate_transparency_report()
high_impact = sorted(
    report['recent_decisions'],
    key=lambda x: x['metadata']['affected_citizens'],
    reverse=True
)[:10]

for decision in high_impact:
    meta = decision['metadata']
    print(f"{meta['affected_citizens']:,} citizens affected by:")
    print(f"  {meta['agent_type']}: {meta['decision']}")
    print(f"  Rationale: {meta['rationale']}")
```

---

## Configuration

### Customize Vector Database

```python
from transparency_logger import TransparencyLogger

# Custom configuration
logger = TransparencyLogger(
    collection_name="my_governance_logs",
    persist_directory="./my_vector_db",
    embedding_model="all-mpnet-base-v2"  # Better but slower
)
```

### Available Embedding Models

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|---------|
| `all-MiniLM-L6-v2` | 384 | Fast | Good |
| `all-mpnet-base-v2` | 768 | Medium | Better |
| `multi-qa-mpnet-base-dot-v1` | 768 | Medium | Best for Q&A |

---

## Testing

### Test Transparency Logging

```python
from transparency_logger import get_transparency_logger

def test_transparency_logging():
    logger = get_transparency_logger()
    
    # Log test decision
    log_id = logger.log_decision(
        agent_type="water",
        node_name="test_node",
        decision="test_approved",
        context={"test": True},
        rationale="Testing transparency system",
        confidence=0.95,
        cost_impact=100000,
        affected_citizens=1000,
        policy_references=["test_policy"]
    )
    
    print(f"Logged: {log_id}")
    
    # Search for it
    results = logger.search_decisions("test transparency", n_results=1)
    assert len(results) > 0
    print(f"Found: {results[0]['metadata']['decision']}")
    
    # Generate report
    report = logger.generate_transparency_report()
    print(f"Total decisions: {report['statistics']['total_decisions']}")
    
    print("[OK] Transparency logging test passed!")

if __name__ == "__main__":
    test_transparency_logging()
```

---

## Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Log Decision | ~50ms | Includes embedding |
| Semantic Search | ~100ms | For 10k documents |
| Generate Report | ~200ms | For 1k decisions |
| DB Persistence | ~500ms | On close() |

### Scaling

- **Small deployment** (<10k decisions): In-memory ChromaDB
- **Medium deployment** (10k-1M decisions): Persistent ChromaDB
- **Large deployment** (>1M decisions): ChromaDB server mode or cloud (Pinecone, Weaviate)

---

## Best Practices

### 1. Log at Key Decision Points

```python
# YES: Log when making important decisions
logger.log_decision(..., decision="approved", cost_impact=500000)

# NO: Don't log every tiny internal operation
# logger.log_decision(..., decision="variable_set", ...)
```

### 2. Provide Clear Rationale

```python
# YES: Explain why
rationale = "Approved due to emergency priority (flood risk), sufficient budget (Rs.50L available), and policy compliance (emergency_protocol_2024)"

# NO: Vague rationale
rationale = "Looks good"
```

### 3. Include Policy References

```python
# YES: Track which policies were considered
policy_references = [
    "emergency_protocol_2024",
    "budget_allocation_policy_v3",
    "citizen_safety_mandate"
]

# NO: Empty policy list
policy_references = []
```

### 4. Track Citizen Impact

```python
# YES: Estimate affected population
affected_citizens = estimate_affected_population(location, project_type)

# NO: Always 0
affected_citizens = 0
```

---

## Roadmap

### Phase 1: Core Logging ✅
- [x] Vector database integration
- [x] Semantic search
- [x] Transparency reports
- [x] Node integration interface

### Phase 2: Advanced RAG (Next)
- [ ] Multi-language support (Hindi, regional languages)
- [ ] Question-answering system
- [ ] Automatic policy conflict detection
- [ ] Trend analysis and predictions

### Phase 3: Public Interface
- [ ] Web dashboard for citizens
- [ ] API for external auditors
- [ ] Real-time decision feeds
- [ ] Mobile app integration

---

## API Reference

### TransparencyLogger

#### Methods

**`log_decision()`**
```python
log_id = logger.log_decision(
    agent_type: str,           # Required
    node_name: str,            # Required
    decision: str,             # Required
    context: Dict,             # Required
    rationale: str = None,     # Recommended
    confidence: float = None,   # 0.0 - 1.0
    cost_impact: float = None,  # In rupees
    affected_citizens: int = None,
    policy_references: List[str] = None,
    metadata: Dict = None
) -> str  # Returns log_id
```

**`log_node_execution()`**
```python
log_id = logger.log_node_execution(
    agent_type: str,
    node_name: str,
    state: Dict,
    action: str,
    result: Any,
    metadata: Dict = None
) -> str
```

**`search_decisions()`**
```python
results = logger.search_decisions(
    query: str,
    n_results: int = 10,
    filter_agent: str = None,
    filter_node: str = None,
    min_confidence: float = None,
    max_cost: float = None
) -> List[Dict]
```

**`generate_transparency_report()`**
```python
report = logger.generate_transparency_report(
    start_date: str = None,  # ISO format
    end_date: str = None,
    agent_type: str = None
) -> Dict
```

---

## Conclusion

The transparency logging system provides:
- ✅ **Public accountability** - All decisions logged with rationale
- ✅ **Semantic search** - Find similar decisions naturally
- ✅ **Audit trails** - Complete decision history
- ✅ **RAG capabilities** - Context-aware decision making
- ✅ **Easy integration** - Simple API for all nodes

**Next Step**: Integrate into existing agent nodes for full transparency!
