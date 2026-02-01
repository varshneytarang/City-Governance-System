"""
Test Transparency Logging System

Tests the RAG-based vector database logging for public transparency.

Run: python test_transparency_logging.py
"""

import pytest
from datetime import datetime, timedelta
from transparency_logger import TransparencyLogger, get_transparency_logger


class TestTransparencyLogger:
    """Test transparency logging functionality"""
    
    def setup_method(self):
        """Setup test logger"""
        self.logger = TransparencyLogger(
            collection_name="test_governance",
            persist_directory="./test_chroma_db"
        )
    
    def teardown_method(self):
        """Cleanup"""
        if hasattr(self, 'logger'):
            self.logger.close()
    
    def test_log_decision_basic(self):
        """Test basic decision logging"""
        log_id = self.logger.log_decision(
            agent_type="water",
            node_name="decision_router",
            decision="approved",
            context={"request_type": "emergency"},
            rationale="High confidence and emergency priority",
            confidence=0.92,
            cost_impact=500000,
            affected_citizens=50000,
            policy_references=["emergency_protocol_2024"]
        )
        
        assert log_id is not None
        assert isinstance(log_id, str)
        print(f"[OK] Logged decision: {log_id}")
    
    def test_log_multiple_decisions(self):
        """Test logging multiple decisions"""
        decisions = [
            ("water", "planner", "plan_generated", 0.85, 300000),
            ("engineering", "feasibility", "feasible", 0.78, 800000),
            ("health", "risk_estimator", "low_risk", 0.91, 200000),
            ("finance", "budget_check", "approved", 0.88, 1500000),
        ]
        
        log_ids = []
        for agent, node, decision, conf, cost in decisions:
            log_id = self.logger.log_decision(
                agent_type=agent,
                node_name=node,
                decision=decision,
                context={"test": True},
                rationale=f"{agent} {node} decision",
                confidence=conf,
                cost_impact=cost,
                affected_citizens=10000
            )
            log_ids.append(log_id)
        
        assert len(log_ids) == 4
        print(f"[OK] Logged {len(log_ids)} decisions")
    
    def test_semantic_search(self):
        """Test semantic search across decisions"""
        # Log some test decisions
        self.logger.log_decision(
            agent_type="water",
            node_name="planner",
            decision="emergency_repair",
            context={"type": "pipeline_burst"},
            rationale="Emergency pipeline repair due to burst in monsoon season",
            confidence=0.95,
            cost_impact=600000,
            affected_citizens=75000,
            policy_references=["emergency_protocol", "monsoon_preparedness"]
        )
        
        self.logger.log_decision(
            agent_type="engineering",
            node_name="planner",
            decision="routine_maintenance",
            context={"type": "road_repair"},
            rationale="Routine road maintenance in dry season",
            confidence=0.80,
            cost_impact=200000,
            affected_citizens=5000
        )
        
        # Search for emergency decisions
        results = self.logger.search_decisions(
            query="emergency pipeline repair monsoon",
            n_results=5
        )
        
        assert len(results) > 0
        print(f"[OK] Found {len(results)} results for emergency query")
        
        # Check if emergency decision is in results
        found_emergency = any(
            'emergency' in r['metadata']['rationale'].lower()
            for r in results
        )
        assert found_emergency
        print("[OK] Emergency decision found in search results")
    
    def test_filter_by_agent(self):
        """Test filtering search by agent type"""
        # Log decisions from different agents
        self.logger.log_decision(
            agent_type="water",
            node_name="test",
            decision="water_decision",
            context={},
            rationale="Water department decision"
        )
        
        self.logger.log_decision(
            agent_type="engineering",
            node_name="test",
            decision="engineering_decision",
            context={},
            rationale="Engineering department decision"
        )
        
        # Search with filter
        results = self.logger.search_decisions(
            query="decision",
            filter_agent="water",
            n_results=10
        )
        
        # All results should be from water agent
        water_only = all(
            r['metadata']['agent_type'] == 'water'
            for r in results
        )
        assert water_only
        print(f"[OK] Filtered to {len(results)} water agent results only")
    
    def test_transparency_report(self):
        """Test transparency report generation"""
        # Log several decisions
        for i in range(5):
            self.logger.log_decision(
                agent_type="water",
                node_name=f"node_{i}",
                decision=f"decision_{i}",
                context={"index": i},
                rationale=f"Test decision {i}",
                confidence=0.8 + (i * 0.02),
                cost_impact=100000 * (i + 1),
                affected_citizens=1000 * (i + 1)
            )
        
        # Generate report
        report = self.logger.generate_transparency_report()
        
        assert "statistics" in report
        assert report["statistics"]["total_decisions"] >= 5
        assert report["statistics"]["total_cost_impact"] > 0
        assert report["statistics"]["total_citizens_affected"] > 0
        
        print(f"[OK] Report generated:")
        print(f"  Decisions: {report['statistics']['total_decisions']}")
        print(f"  Cost: Rs.{report['statistics']['total_cost_impact']:,.0f}")
        print(f"  Citizens: {report['statistics']['total_citizens_affected']:,}")
    
    def test_log_node_execution(self):
        """Test simplified node execution logging"""
        state = {
            "input_event": {"type": "emergency", "location": "Zone-A"},
            "confidence": 0.87,
            "estimated_cost": 450000,
            "feasible": True,
            "policy_ok": True,
            "rationale": "All checks passed"
        }
        
        log_id = self.logger.log_node_execution(
            agent_type="water",
            node_name="decision_router",
            state=state,
            action="approved",
            result={"status": "success"}
        )
        
        assert log_id is not None
        print(f"[OK] Node execution logged: {log_id}")
    
    def test_policy_impact_analysis(self):
        """Test analyzing decisions by policy"""
        # Log decisions with different policies
        policies = [
            ("emergency_protocol", 800000),
            ("emergency_protocol", 600000),
            ("routine_maintenance", 200000),
            ("emergency_protocol", 1000000),
        ]
        
        for policy, cost in policies:
            self.logger.log_decision(
                agent_type="water",
                node_name="test",
                decision="test",
                context={},
                rationale=f"Decision under {policy}",
                cost_impact=cost,
                policy_references=[policy]
            )
        
        # Search for emergency protocol decisions
        results = self.logger.search_decisions(
            query="emergency protocol",
            n_results=10
        )
        
        # Calculate total emergency cost
        emergency_cost = sum(
            float(r['metadata']['cost_impact'])
            for r in results
            if 'emergency' in r['metadata']['rationale'].lower()
        )
        
        assert emergency_cost > 0
        print(f"[OK] Emergency protocol total cost: Rs.{emergency_cost:,.0f}")


def test_integration_example():
    """Example of integrating with agent nodes"""
    logger = get_transparency_logger()
    
    # Simulate water agent decision router
    state = {
        "input_event": {
            "type": "emergency_repair",
            "location": "Zone-B",
            "reason": "Pipeline burst during heavy rain"
        },
        "confidence": 0.94,
        "estimated_cost": 750000,
        "feasible": True,
        "policy_ok": True,
        "applicable_policies": ["emergency_protocol_2024", "monsoon_response_v2"],
        "affected_population": 85000
    }
    
    # Log the decision
    log_id = logger.log_decision(
        agent_type="water",
        node_name="decision_router",
        decision="approved",
        context={
            "request": state["input_event"],
            "feasibility": "feasible",
            "policy_status": "compliant"
        },
        rationale="Emergency approval: High confidence (94%), feasible plan, policy compliant, 85k citizens affected",
        confidence=state["confidence"],
        cost_impact=state["estimated_cost"],
        affected_citizens=state.get("affected_population", 0),
        policy_references=state.get("applicable_policies", [])
    )
    
    print(f"\n[INTEGRATION EXAMPLE]")
    print(f"Logged decision: {log_id}")
    print(f"Agent: water.decision_router")
    print(f"Decision: approved")
    print(f"Cost: Rs.{state['estimated_cost']:,}")
    print(f"Citizens: {state.get('affected_population', 0):,}")
    
    # Search for similar decisions
    similar = logger.search_decisions(
        query="emergency pipeline repair monsoon",
        n_results=3
    )
    
    print(f"\nFound {len(similar)} similar past decisions:")
    for i, result in enumerate(similar, 1):
        meta = result['metadata']
        print(f"{i}. {meta['agent_type']}.{meta['node_name']}: {meta['decision']}")
        print(f"   Cost: Rs.{meta['cost_impact']:,.0f}, Confidence: {meta['confidence']:.0%}")
    
    logger.close()


def test_public_transparency_query():
    """Simulate public citizen querying the transparency system"""
    logger = get_transparency_logger()
    
    # Log some public decisions
    decisions = [
        {
            "agent": "water",
            "node": "decision_router",
            "decision": "approved",
            "rationale": "Zone-A water pipeline replacement for 50,000 residents",
            "cost": 3000000,
            "citizens": 50000,
            "policies": ["infrastructure_modernization_2025"]
        },
        {
            "agent": "health",
            "node": "decision_router",
            "decision": "approved",
            "rationale": "Mobile health clinic for rural areas serving 25,000 people",
            "cost": 1500000,
            "citizens": 25000,
            "policies": ["rural_health_initiative_2025"]
        },
        {
            "agent": "engineering",
            "node": "decision_router",
            "decision": "approved",
            "rationale": "Bridge construction to connect isolated communities",
            "cost": 5000000,
            "citizens": 15000,
            "policies": ["connectivity_mandate_2025"]
        }
    ]
    
    for d in decisions:
        logger.log_decision(
            agent_type=d["agent"],
            node_name=d["node"],
            decision=d["decision"],
            context={"public_record": True},
            rationale=d["rationale"],
            confidence=0.85,
            cost_impact=d["cost"],
            affected_citizens=d["citizens"],
            policy_references=d["policies"]
        )
    
    print("\n[PUBLIC TRANSPARENCY QUERY]")
    print("Citizen asks: 'What projects are being done for rural areas?'")
    
    results = logger.search_decisions(
        query="rural areas projects health infrastructure",
        n_results=5
    )
    
    print(f"\nPublic Results ({len(results)} found):")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"\n{i}. {meta['agent_type'].upper()} DEPARTMENT")
        print(f"   Decision: {meta['decision']}")
        print(f"   Details: {meta['rationale']}")
        print(f"   Cost: Rs.{meta['cost_impact']:,.0f}")
        print(f"   Citizens Benefiting: {meta['affected_citizens']:,}")
        print(f"   Date: {meta['timestamp'][:10]}")
    
    logger.close()


if __name__ == "__main__":
    print("="*70)
    print("TRANSPARENCY LOGGING SYSTEM - TESTS")
    print("="*70)
    
    # Run pytest tests
    print("\n1. Running automated tests...")
    pytest.main([__file__, "-v", "--tb=short"])
    
    # Run integration example
    print("\n2. Running integration example...")
    test_integration_example()
    
    # Run public query example
    print("\n3. Running public transparency query...")
    test_public_transparency_query()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
