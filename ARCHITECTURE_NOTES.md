# City Governance System - Architecture Notes

## 🏛️ Hierarchical Pyramid Architecture

```
                    ┌─────────────────────────────┐
                    │   LAYER 1: COORDINATOR      │
                    │   + Human Intervention      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
         ┌──────────▼─────────┐       ┌──────────▼─────────┐
         │  LAYER 2: MIDDLE   │       │  LAYER 2: MIDDLE   │
         │  Coordination      │◄─────►│  Coordination      │
         │  Agent 1           │       │  Agent 2           │
         └──────────┬─────────┘       └──────────┬─────────┘
                    │                             │
         ┌──────────▼─────────┐                   │
         │  LAYER 2: MIDDLE   │                   │
         │  Coordination      │◄──────────────────┘
         │  Agent 3           │
         └──────────┬─────────┘
                    │
    ┌───────────────┼───────────────┬─────────────
    │               │               │
┌───▼───┐       ┌───▼───┐       ┌───▼───┐
│ LAYER │       │ LAYER │       │ LAYER │
│   3   │       │   3   │       │   3   │
│ Dept  │       │ Dept  │       │ Dept  │
│Agents │       │Agents │       │Agents │
└───────┘       └───────┘       └───────┘
Water           Fire            Engineering
Health          Roads           Finance
```

---

## 🔄 Agent Interaction Types (CRITICAL)

### **Problem Identified:**
If Agent A asks Agent B for data, and Agent B runs through its full 6-node workflow, that's inefficient and doesn't fit the use case.

### **Solution: Multiple Entry Points**

Each department agent needs **3 different interaction modes**:

#### **1. Primary Request (Full Workflow)**
**Source:** Citizen/User → Department Agent  
**Flow:** Complete 6-node workflow  
**Example:** Citizen requests water connection

```python
class WaterAgent:
    async def process_request(self, request: UserRequest):
        """
        Full workflow for primary citizen requests
        6 nodes: validation → collection → compliance → decision → coordination → response
        """
        workflow = create_water_agent_workflow()
        result = await workflow.ainvoke({
            "request_type": request.type,
            "request_data": request.data,
            # ... full state initialization
        })
        return result
```

#### **2. Data Query (Lightweight)**
**Source:** Another Agent (via Middle Layer) → Department Agent  
**Flow:** Direct data retrieval - NO workflow  
**Example:** Engineering asks Water for supply capacity data

```python
class WaterAgent:
    async def provide_data(self, query_type: str, context: Dict):
        """
        Lightweight data provision for other agents
        NO workflow - just fetch and return data
        """
        if query_type == "water_supply_capacity":
            location = context["location"]
            pipelines = await fetch_pipeline_data(self.db, location)
            reservoir = await get_reservoir_status(self.db, location)
            
            return {
                "department": "water",
                "query_type": query_type,
                "data": {
                    "available_capacity": reservoir["available_capacity"],
                    "existing_connections": pipelines["connection_count"],
                    "pipeline_diameter": pipelines["diameter"],
                    "pressure": pipelines["pressure"],
                    "supply_reliability": "high"  # based on historical data
                },
                "metadata": {
                    "data_age": "real-time",
                    "confidence": "high"
                }
            }
        
        elif query_type == "water_quality":
            return await self._get_water_quality_data(context)
        
        elif query_type == "pipeline_route":
            return await self._get_pipeline_route(context)
        
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    # Other lightweight query methods
    async def check_conflicts(self, location: str, project_type: str):
        """Check if location has any water-related conflicts"""
        conflicts = await check_conflicts_with_projects(self.db, location)
        return {"has_conflicts": len(conflicts) > 0, "conflicts": conflicts}
```

#### **3. Coordination Request (Post-Decision)**
**Source:** Another Agent → Department Agent  
**Flow:** Receive notification/approval request - Limited processing  
**Example:** Engineering sends NOC request after building approval decision

```python
class WaterAgent:
    async def handle_coordination_request(self, coordination: CoordinationRequest):
        """
        Handle post-decision coordination from other agents
        Lighter than full workflow, but more than just data query
        """
        if coordination.type == "noc_request":
            # Quick assessment for NOC
            assessment = await self._quick_noc_assessment(coordination.data)
            
            # Store in agent_messages table
            await self._log_coordination(coordination)
            
            if assessment["complexity"] == "simple":
                # Auto-approve simple cases
                return {
                    "status": "approved",
                    "conditions": assessment.get("conditions", []),
                    "response_time": "immediate"
                }
            else:
                # Complex cases → create full request for detailed review
                full_request_id = await self._create_full_request_from_coordination(
                    coordination
                )
                return {
                    "status": "under_review",
                    "request_id": full_request_id,
                    "estimated_time": "2-3 days"
                }
        
        elif coordination.type == "notification":
            # Just acknowledge and log
            await self._log_notification(coordination)
            return {"status": "acknowledged"}
```

---

## 🔀 Updated Communication Flows

### **Flow 1: Citizen Request (Full Workflow)**

```
Citizen → Water Agent.process_request()
                ↓
    [6-node workflow runs]
                ↓
         Full decision made
```

### **Flow 2: Inter-Agent Data Query (via Middle Layer)**

```
Engineering Agent (data_collection_node)
        ↓
    "I need water supply data for this location"
        ↓
Middle Agent.get_peer_department_data()
        ↓
Water Agent.provide_data("water_supply_capacity")
        ↓
    [NO WORKFLOW - just fetch data]
        ↓
    Returns data immediately
        ↓
Engineering gets data in seconds
```

### **Flow 3: Post-Decision Coordination**

```
Engineering Agent (decision made: "approve building")
        ↓
    coordination_node
        ↓
Middle Agent.send_coordination_request()
        ↓
Water Agent.handle_coordination_request("noc_request")
        ↓
    [Quick assessment - NO full workflow]
        ↓
    Returns: approve/review_needed
```

---

## 📋 Department Agent Interface

Each department agent implements this standard interface:

```python
class DepartmentAgentInterface:
    """
    Standard interface for all Layer 3 department agents
    """
    
    # PRIMARY REQUEST (Full workflow)
    async def process_request(self, request: UserRequest) -> AgentResponse:
        """
        Full 6-node workflow for citizen/user requests
        Returns: Complete decision with reasoning
        """
        pass
    
    # DATA QUERIES (Lightweight - no workflow)
    async def provide_data(self, query_type: str, context: Dict) -> Dict:
        """
        Provide data to other agents (via middle layer)
        Returns: Raw data, no decision-making
        """
        pass
    
    async def check_conflicts(self, location: str, project_type: str) -> Dict:
        """
        Quick conflict check for other agents
        Returns: Boolean + conflict details
        """
        pass
    
    async def get_status(self, entity_id: str) -> Dict:
        """
        Get current status of entity (connection, project, incident)
        Returns: Current status
        """
        pass
    
    # COORDINATION (Post-decision)
    async def handle_coordination_request(self, request: CoordinationRequest) -> Dict:
        """
        Handle NOC requests, notifications from other agents
        Returns: Approval/review decision
        """
        pass
    
    async def receive_notification(self, notification: Notification) -> Dict:
        """
        Receive FYI notifications from other agents
        Returns: Acknowledgment
        """
        pass
```

---

## 🎯 Query Types by Department

### **Water Agent - Data Queries**
```python
WATER_QUERY_TYPES = [
    "water_supply_capacity",      # Can location support new connections?
    "water_quality",               # Current water quality metrics
    "pipeline_route",              # Pipeline locations/routes
    "pressure_availability",       # Water pressure at location
    "drainage_capacity",           # Drainage infrastructure
    "flood_risk",                  # Flooding history/risk
    "water_conflicts",             # Ongoing projects/issues
    "supply_schedule",             # Water supply timings
    "reservoir_status",            # Current reservoir levels
]
```

### **Fire Agent - Data Queries**
```python
FIRE_QUERY_TYPES = [
    "fire_station_coverage",      # Is location covered by fire station?
    "response_time_estimate",     # Expected response time
    "fire_hydrant_availability",  # Hydrants near location
    "fire_risk_assessment",       # Fire risk level for area
    "emergency_access",           # Can fire trucks access?
    "fire_history",               # Past fire incidents
    "evacuation_routes",          # Emergency evacuation paths
    "equipment_availability",     # Fire equipment at nearby station
]
```

### **Engineering Agent - Data Queries**
```python
ENGINEERING_QUERY_TYPES = [
    "building_structural_info",    # Building specifications
    "land_use_zone",              # Zoning classification
    "approved_buildings",         # Existing approved buildings
    "construction_activity",      # Ongoing construction
    "structural_stability",       # Building stability status
    "seismic_zone",              # Seismic zone classification
    "floor_space_index",         # FAR/FSI for area
    "building_height_limits",    # Height restrictions
    "setback_requirements",      # Required setbacks
]
```

### **Health Agent - Data Queries**
```python
HEALTH_QUERY_TYPES = [
    "disease_prevalence",         # Disease stats for area
    "hospital_capacity",          # Nearby hospital beds
    "sanitation_status",          # Sanitation infrastructure
    "food_safety_history",        # Food safety violations
    "vector_control",             # Mosquito/pest control
    "health_hazards",             # Known health hazards
    "vaccination_coverage",       # Immunization rates
]
```

### **Roads Agent - Data Queries**
```python
ROADS_QUERY_TYPES = [
    "road_access",                # Road connectivity
    "traffic_impact",             # Traffic congestion level
    "road_width",                 # Width of access roads
    "parking_availability",       # Parking spaces
    "public_transport",           # Bus/metro connectivity
    "road_condition",             # Road quality/maintenance
    "traffic_violations",         # Accident/violation history
]
```

---

## 💡 Benefits of Multiple Entry Points

### **1. Performance**
- Full workflow: 5-10 seconds (LLM calls, policy checks)
- Data query: <1 second (database fetch)
- **10x faster** for inter-agent communication

### **2. Resource Efficiency**
- No unnecessary LLM invocations
- No policy evaluations for simple data queries
- Reduced token costs

### **3. Clarity**
- Clear separation: decision-making vs data provision
- Easier to debug (which type of call failed?)
- Better logging and monitoring

### **4. Scalability**
- Handle hundreds of data queries per second
- Full workflows limited by LLM rate limits
- Independent scaling strategies

### **5. Realism**
- Real departments provide data quickly to other departments
- Complex decisions take time (full workflow)
- Matches real government operations

---

## 🔧 Implementation Pattern

### **Updated Department Agent Structure**

```python
class WaterAgent:
    def __init__(self, db, middle_agent):
        self.db = db
        self.middle_agent = middle_agent
        self.llm = ChatGroq(model="llama-3.3-70b-versatile")
        self.workflow = None  # Created lazily for full requests
    
    # ========== PRIMARY REQUESTS (Full Workflow) ==========
    async def process_request(self, request: UserRequest):
        """Entry point 1: Full 6-node workflow"""
        if not self.workflow:
            self.workflow = create_water_agent_workflow(self.db)
        
        state = {
            "request_type": request.type,
            # ... initialize full state
        }
        return await self.workflow.ainvoke(state)
    
    # ========== DATA QUERIES (Lightweight) ==========
    async def provide_data(self, query_type: str, context: Dict):
        """Entry point 2: Quick data provision"""
        # Direct database queries - NO workflow
        handler = self._get_query_handler(query_type)
        return await handler(context)
    
    async def _get_water_supply_capacity(self, context):
        """Specific query handler"""
        location = context["location"]
        pipelines = await fetch_pipeline_data(self.db, location)
        return {"capacity": pipelines["available_capacity"]}
    
    # ========== COORDINATION (Post-Decision) ==========
    async def handle_coordination_request(self, request: CoordinationRequest):
        """Entry point 3: Handle coordination from other agents"""
        if request.type == "noc_request":
            return await self._assess_noc_request(request)
        elif request.type == "notification":
            return await self._log_notification(request)
```

---

## 📊 Comparison: Full Workflow vs Data Query

| Aspect | Full Workflow | Data Query |
|--------|--------------|------------|
| **Entry Point** | `process_request()` | `provide_data()` |
| **Source** | Citizen/User | Other Agent (via middle) |
| **Nodes** | 6 nodes | 0 nodes (direct function) |
| **LLM Calls** | 2-3 calls | 0 calls |
| **Policy Checks** | 5-8 policies | 0 policies |
| **Response Time** | 5-10 seconds | <1 second |
| **Output** | Decision + reasoning | Data only |
| **State Management** | Full TypedDict state | Simple Dict |
| **Database Queries** | 5-10 queries | 1-2 queries |
| **Token Cost** | $0.01-0.05 | $0 |

---

## 🎬 Real Example Scenario

**Scenario:** Engineering approves 10-story building

### **With Old Approach (Everything through workflow):**
```
Engineering: "I need water data"
    → Water Agent: Run full 6-node workflow (10 seconds)
    → Returns: "Approved for water supply" (decision we don't need)

Engineering: "I need fire data"
    → Fire Agent: Run full 6-node workflow (10 seconds)
    → Returns: "Fire safety assessment: Approved" (decision we don't need)

Total time: 20+ seconds just to get data
```

### **With New Approach (Multiple entry points):**
```
Engineering: "I need water data"
    → Water Agent.provide_data("water_supply_capacity") (0.5 seconds)
    → Returns: {capacity: 5000L/day, pressure: adequate}

Engineering: "I need fire data"
    → Fire Agent.provide_data("fire_station_coverage") (0.5 seconds)
    → Returns: {coverage: yes, response_time: 5min, hydrants: 3}

Total time: 1 second to get data

... Engineering makes decision with this data ...

Engineering: "Building approved, send NOC requests"
    → Water Agent.handle_coordination_request("noc_request")
    → Quick assessment (2 seconds)
    → Returns: "NOC approved with conditions"
```

**Result:** 21 seconds → 3 seconds (7x faster)

---

## ✅ Architecture Decision: FINALIZED

**Department agents have 3 entry points:**

1. **`process_request()`** - Full workflow for citizen requests
2. **`provide_data()`** - Lightweight data queries from other agents
3. **`handle_coordination_request()`** - Post-decision coordination

**Communication via Middle Layer:**
- Middle agent calls appropriate entry point based on request type
- Data queries → `provide_data()`
- Coordination → `handle_coordination_request()`
- Never triggers full workflow unnecessarily

---

## 📝 Next Steps

1. ✅ Architecture decision made: Multiple entry points
2. [ ] Update existing Water/Fire agents with new interface
3. [ ] Implement middle layer that routes to correct entry point
4. [ ] Define standard query types for each department
5. [ ] Implement coordinator layer
6. [ ] Add remaining department agents
