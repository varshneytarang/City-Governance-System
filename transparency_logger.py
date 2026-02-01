"""
Transparency Logging Node with RAG Vector Database

This node logs all essential decisions, actions, and rationale
from all department agents to a vector database for:
1. Public transparency
2. Semantic search and retrieval
3. Audit trails
4. Policy analysis
5. Historical decision context

Uses ChromaDB for vector storage with embedding-based search.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not installed. Run: pip install chromadb")

# Embedding imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("sentence-transformers not installed. Run: pip install sentence-transformers")

logger = logging.getLogger(__name__)


class TransparencyLogger:
    """
    Centralized logging node with vector database integration
    for public transparency and RAG capabilities.
    """
    
    def __init__(
        self,
        collection_name: str = "governance_decisions",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize transparency logger with vector database
        
        Args:
            collection_name: Name of ChromaDB collection
            persist_directory: Where to store vector DB
            embedding_model: Sentence transformer model for embeddings
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB
        if CHROMADB_AVAILABLE:
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=collection_name)
                logger.info(f"[OK] Connected to existing collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "Governance system transparency logs"}
                )
                logger.info(f"[OK] Created new collection: {collection_name}")
        else:
            self.client = None
            self.collection = None
            logger.warning("ChromaDB not available - logging to console only")
        
        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"[OK] Loaded embedding model: {embedding_model}")
        else:
            self.embedding_model = None
            logger.warning("Embedding model not available")
    
    def log_decision(
        self,
        agent_type: str,
        node_name: str,
        decision: str,
        context: Dict[str, Any],
        rationale: Optional[str] = None,
        confidence: Optional[float] = None,
        cost_impact: Optional[float] = None,
        affected_citizens: Optional[int] = None,
        policy_references: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a decision to vector database for transparency
        
        Args:
            agent_type: Which agent (water, engineering, health, finance, coordination)
            node_name: Which node made the decision
            decision: The actual decision made
            context: Full context of the decision
            rationale: Why this decision was made
            confidence: Confidence score (0-1)
            cost_impact: Estimated cost in rupees
            affected_citizens: Number of citizens impacted
            policy_references: Which policies were considered
            metadata: Additional metadata
        
        Returns:
            log_id: Unique ID for this log entry
        """
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Build comprehensive log entry
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp,
            "agent_type": agent_type,
            "node_name": node_name,
            "decision": decision,
            "context": context,
            "rationale": rationale or "No rationale provided",
            "confidence": confidence,
            "cost_impact": cost_impact,
            "affected_citizens": affected_citizens,
            "policy_references": policy_references or [],
            "metadata": metadata or {}
        }
        
        # Create searchable text for embedding
        searchable_text = self._create_searchable_text(log_entry)
        
        # Log to console for immediate visibility
        logger.info(f"[TRANSPARENCY LOG] {agent_type}.{node_name}: {decision}")
        if rationale:
            logger.info(f"  Rationale: {rationale}")
        if confidence is not None:
            logger.info(f"  Confidence: {confidence:.2%}")
        if cost_impact is not None:
            logger.info(f"  Cost Impact: Rs.{cost_impact:,.0f}")
        if affected_citizens is not None:
            logger.info(f"  Citizens Affected: {affected_citizens:,}")
        
        # Store in vector database
        if self.collection is not None:
            try:
                self.collection.add(
                    ids=[log_id],
                    documents=[searchable_text],
                    metadatas=[{
                        "agent_type": agent_type,
                        "node_name": node_name,
                        "decision": decision,
                        "timestamp": timestamp,
                        "confidence": confidence or 0.0,
                        "cost_impact": cost_impact or 0.0,
                        "affected_citizens": affected_citizens or 0,
                        "rationale": rationale or "",
                        "context_json": json.dumps(context),
                        "policies": json.dumps(policy_references or [])
                    }]
                )
                logger.debug(f"[OK] Stored in vector DB: {log_id}")
            except Exception as e:
                logger.error(f"[ERROR] Failed to store in vector DB: {e}")
        
        return log_id
    
    def log_node_execution(
        self,
        agent_type: str,
        node_name: str,
        state: Dict[str, Any],
        action: str,
        result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a node execution for transparency
        
        Simpler interface for nodes to log their execution.
        """
        # Extract key information from state
        request = state.get("input_event", {})
        confidence = state.get("confidence", None)
        
        # Determine cost impact
        cost_impact = None
        if "estimated_cost" in state:
            cost_impact = state["estimated_cost"]
        elif "cost_estimates" in state:
            cost_impact = state["cost_estimates"].get("total_estimated_cost", 0)
        
        # Build rationale
        rationale_parts = []
        if "rationale" in state:
            rationale_parts.append(state["rationale"])
        if "feasibility_reason" in state:
            rationale_parts.append(f"Feasibility: {state['feasibility_reason']}")
        if "policy_violations" in state and state.get("policy_violations"):
            rationale_parts.append(f"Policy Issues: {', '.join(state['policy_violations'])}")
        
        rationale = " | ".join(rationale_parts) if rationale_parts else None
        
        return self.log_decision(
            agent_type=agent_type,
            node_name=node_name,
            decision=action,
            context={
                "request": request,
                "state_summary": self._summarize_state(state),
                "result": str(result)[:500]  # Limit result size
            },
            rationale=rationale,
            confidence=confidence,
            cost_impact=cost_impact,
            metadata=metadata
        )
    
    def search_decisions(
        self,
        query: str,
        n_results: int = 10,
        filter_agent: Optional[str] = None,
        filter_node: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_cost: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across logged decisions using RAG
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            filter_agent: Filter by agent type
            filter_node: Filter by node name
            min_confidence: Minimum confidence threshold
            max_cost: Maximum cost threshold
        
        Returns:
            List of matching decisions with context
        """
        if self.collection is None:
            logger.warning("Vector DB not available - cannot search")
            return []
        
        # Build filter
        where_filter = {}
        if filter_agent:
            where_filter["agent_type"] = filter_agent
        if filter_node:
            where_filter["node_name"] = filter_node
        
        # Add numeric filters if needed
        where_document_filter = {}
        if min_confidence is not None:
            where_document_filter["confidence"] = {"$gte": min_confidence}
        if max_cost is not None:
            where_document_filter["cost_impact"] = {"$lte": max_cost}
        
        try:
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "log_id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"[SEARCH] Found {len(formatted_results)} results for: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"[ERROR] Search failed: {e}")
            return []
    
    def get_decision_history(
        self,
        agent_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent decision history for transparency reports
        """
        if self.collection is None:
            return []
        
        try:
            # Query all or filtered by agent
            where_filter = {"agent_type": agent_type} if agent_type else None
            
            results = self.collection.get(
                where=where_filter,
                limit=limit
            )
            
            # Format as list
            history = []
            if results and results['ids']:
                for i in range(len(results['ids'])):
                    history.append({
                        "log_id": results['ids'][i],
                        "text": results['documents'][i],
                        "metadata": results['metadatas'][i]
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get history: {e}")
            return []
    
    def generate_transparency_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        agent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate public transparency report
        
        Returns:
            Report with statistics, key decisions, cost analysis
        """
        history = self.get_decision_history(agent_type=agent_type, limit=1000)
        
        # Filter by date if provided
        if start_date or end_date:
            filtered_history = []
            for entry in history:
                timestamp = entry['metadata'].get('timestamp', '')
                if start_date and timestamp < start_date:
                    continue
                if end_date and timestamp > end_date:
                    continue
                filtered_history.append(entry)
            history = filtered_history
        
        # Calculate statistics
        total_decisions = len(history)
        total_cost = sum(float(entry['metadata'].get('cost_impact', 0)) for entry in history)
        avg_confidence = sum(float(entry['metadata'].get('confidence', 0)) for entry in history) / max(total_decisions, 1)
        total_citizens_affected = sum(int(entry['metadata'].get('affected_citizens', 0)) for entry in history)
        
        # Group by agent type
        by_agent = {}
        for entry in history:
            agent = entry['metadata'].get('agent_type', 'unknown')
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(entry)
        
        # Build report
        report = {
            "report_date": datetime.now().isoformat(),
            "period": {
                "start": start_date or "inception",
                "end": end_date or "present"
            },
            "statistics": {
                "total_decisions": total_decisions,
                "total_cost_impact": total_cost,
                "average_confidence": avg_confidence,
                "total_citizens_affected": total_citizens_affected,
                "decisions_by_agent": {agent: len(entries) for agent, entries in by_agent.items()}
            },
            "top_decisions": sorted(
                history,
                key=lambda x: float(x['metadata'].get('cost_impact', 0)),
                reverse=True
            )[:10],
            "recent_decisions": history[:20]
        }
        
        logger.info(f"[REPORT] Generated transparency report: {total_decisions} decisions, Rs.{total_cost:,.0f} impact")
        return report
    
    def _create_searchable_text(self, log_entry: Dict[str, Any]) -> str:
        """Create searchable text from log entry for embeddings"""
        parts = [
            f"Agent: {log_entry['agent_type']}",
            f"Node: {log_entry['node_name']}",
            f"Decision: {log_entry['decision']}",
        ]
        
        if log_entry.get('rationale'):
            parts.append(f"Rationale: {log_entry['rationale']}")
        
        if log_entry.get('context'):
            context_str = json.dumps(log_entry['context'], indent=2)[:500]
            parts.append(f"Context: {context_str}")
        
        if log_entry.get('policy_references'):
            parts.append(f"Policies: {', '.join(log_entry['policy_references'])}")
        
        return " | ".join(parts)
    
    def _summarize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize state for logging (avoid huge objects)"""
        summary = {}
        
        # Key fields to include
        important_fields = [
            "decision", "confidence", "estimated_cost", "priority",
            "location", "feasible", "policy_ok", "escalate",
            "intent", "risk_level", "goal"
        ]
        
        for field in important_fields:
            if field in state:
                value = state[field]
                # Limit string length
                if isinstance(value, str) and len(value) > 200:
                    summary[field] = value[:200] + "..."
                else:
                    summary[field] = value
        
        return summary
    
    def close(self):
        """Persist and close vector database"""
        if self.client and hasattr(self.client, 'persist'):
            try:
                self.client.persist()
                logger.info("[OK] Persisted vector database")
            except:
                pass


# Singleton instance for easy import
_transparency_logger = None

def get_transparency_logger() -> TransparencyLogger:
    """Get singleton transparency logger instance"""
    global _transparency_logger
    if _transparency_logger is None:
        _transparency_logger = TransparencyLogger()
    return _transparency_logger
