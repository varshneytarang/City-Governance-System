"""
Knowledge Graph Generator

Creates visual representations of workflow dependencies and relationships.
Generates graph data for frontend visualization (D3.js/React Flow).
"""

import logging
import json
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from datetime import datetime

from .database import get_queries, TaskQueries
from .workflow_engine import get_workflow_engine

logger = logging.getLogger(__name__)


class KnowledgeGraphGenerator:
    """
    Generates knowledge graphs for workflows
    """
    
    def __init__(self):
        self.queries: TaskQueries = get_queries()
        self.engine = get_workflow_engine()
        logger.info("✓ Knowledge Graph Generator initialized")
    
    # ==================== GRAPH GENERATION ====================
    
    def generate_workflow_graph(
        self,
        workflow_id: str,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete knowledge graph for a workflow
        
        Returns:
            {
                "workflow_id": "...",
                "nodes": [...],
                "edges": [...],
                "metadata": {...}
            }
        """
        logger.info(f"Generating knowledge graph for workflow {workflow_id}")
        
        # Get workflow and tasks
        workflow = self.queries.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        tasks = self.queries.get_workflow_tasks(workflow_id)
        
        # Build nodes
        nodes = self._build_nodes(tasks, workflow)
        
        # Build edges (dependencies)
        edges = self._build_edges(workflow_id, tasks)
        
        # Calculate metadata
        metadata = {}
        if include_metadata:
            metadata = self._calculate_metadata(workflow, tasks, nodes, edges)
        
        graph_data = {
            "workflow_id": workflow_id,
            "workflow_name": workflow['workflow_name'],
            "nodes": nodes,
            "edges": edges,
            "metadata": metadata,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        self._save_graph_to_db(workflow_id, nodes, edges)
        
        logger.info(f"✓ Generated graph: {len(nodes)} nodes, {len(edges)} edges")
        return graph_data
    
    def _build_nodes(
        self,
        tasks: List[Dict[str, Any]],
        workflow: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build graph nodes from tasks"""
        nodes = []
        
        for task in tasks:
            node = {
                "id": str(task['task_id']),
                "type": "task",
                "label": task['task_title'],
                "data": {
                    "task_id": str(task['task_id']),
                    "title": task['task_title'],
                    "description": task.get('task_description', ''),
                    "department": task['assigned_department'],
                    "status": task['task_status'],
                    "priority": task['priority'],
                    "assigned_to": task.get('assigned_to'),
                    "progress_percentage": task.get('progress_percentage', 0),
                    "estimated_duration": task.get('estimated_duration_hours', 0),
                    "actual_duration": self._calculate_actual_duration(task),
                    "estimated_cost": task.get('estimated_cost', 0),
                    "actual_cost": task.get('actual_cost', 0),
                    "started_at": task.get('started_at').isoformat() if task.get('started_at') else None,
                    "completed_at": task.get('completed_at').isoformat() if task.get('completed_at') else None,
                    "deadline": task.get('deadline').isoformat() if task.get('deadline') else None
                },
                "position": self._calculate_node_position(task, tasks),  # For layout
                "style": self._get_node_style(task)
            }
            nodes.append(node)
        
        return nodes
    
    def _build_edges(
        self,
        workflow_id: str,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build graph edges from dependencies"""
        edges = []
        task_ids = [str(t['task_id']) for t in tasks]
        
        for task in tasks:
            task_id = str(task['task_id'])
            dependencies = self.queries.get_task_dependencies(task_id)
            
            for dep in dependencies:
                depends_on_id = str(dep['depends_on_task_id'])
                
                # Only include edges between tasks in this workflow
                if depends_on_id not in task_ids:
                    continue
                
                edge = {
                    "id": f"{depends_on_id}->{task_id}",
                    "source": depends_on_id,
                    "target": task_id,
                    "type": dep.get('dependency_type', 'finish_to_start'),
                    "data": {
                        "dependency_type": dep.get('dependency_type', 'finish_to_start'),
                        "description": dep.get('dependency_description', ''),
                        "is_mandatory": dep.get('is_mandatory', True),
                        "created_at": dep.get('created_at').isoformat() if dep.get('created_at') else None
                    },
                    "style": self._get_edge_style(dep)
                }
                edges.append(edge)
        
        return edges
    
    def _calculate_node_position(
        self,
        task: Dict[str, Any],
        all_tasks: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate initial node position for layout"""
        # Use sequence number for vertical positioning
        sequence = task.get('task_sequence', 0)
        
        # Group by department for horizontal positioning
        department = task['assigned_department']
        departments = list(set(t['assigned_department'] for t in all_tasks))
        dept_index = departments.index(department) if department in departments else 0
        
        return {
            "x": dept_index * 300,  # Spread departments horizontally
            "y": sequence * 150     # Stack by sequence vertically
        }
    
    def _get_node_style(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get visual style for node based on status"""
        status = task['task_status']
        priority = task['priority']
        
        # Status colors
        status_colors = {
            "pending": "#94a3b8",      # slate-400
            "ready": "#3b82f6",        # blue-500
            "in_progress": "#f59e0b",  # amber-500
            "completed": "#10b981",    # green-500
            "blocked": "#ef4444",      # red-500
            "failed": "#dc2626",       # red-600
            "cancelled": "#6b7280"     # gray-500
        }
        
        # Priority border widths
        priority_widths = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
            "emergency": 5
        }
        
        return {
            "backgroundColor": status_colors.get(status, "#9ca3af"),
            "borderColor": "#1e293b",
            "borderWidth": priority_widths.get(priority, 2),
            "borderRadius": "8px",
            "padding": "12px",
            "minWidth": "200px",
            "color": "#ffffff" if status in ["in_progress", "completed", "blocked", "failed"] else "#1f2937"
        }
    
    def _get_edge_style(self, dependency: Dict[str, Any]) -> Dict[str, Any]:
        """Get visual style for edge based on dependency type"""
        dep_type = dependency.get('dependency_type', 'finish_to_start')
        is_mandatory = dependency.get('is_mandatory', True)
        
        # Edge styles by type
        type_styles = {
            "finish_to_start": {"strokeDasharray": "0", "strokeWidth": 2},
            "start_to_start": {"strokeDasharray": "5,5", "strokeWidth": 2},
            "finish_to_finish": {"strokeDasharray": "10,5", "strokeWidth": 2},
            "start_to_finish": {"strokeDasharray": "2,2", "strokeWidth": 2}
        }
        
        style = type_styles.get(dep_type, {"strokeDasharray": "0", "strokeWidth": 2})
        
        # Optional dependencies are lighter
        if not is_mandatory:
            style["opacity"] = 0.5
            style["strokeDasharray"] = "3,3"
        
        return style
    
    def _calculate_actual_duration(self, task: Dict[str, Any]) -> Optional[float]:
        """Calculate actual duration in hours"""
        if task.get('started_at') and task.get('completed_at'):
            delta = task['completed_at'] - task['started_at']
            return round(delta.total_seconds() / 3600, 2)
        return None
    
    def _calculate_metadata(
        self,
        workflow: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate graph metadata and statistics"""
        
        # Task status distribution
        status_dist = defaultdict(int)
        for task in tasks:
            status_dist[task['task_status']] += 1
        
        # Department distribution
        dept_dist = defaultdict(int)
        for task in tasks:
            dept_dist[task['assigned_department']] += 1
        
        # Priority distribution
        priority_dist = defaultdict(int)
        for task in tasks:
            priority_dist[task['priority']] += 1
        
        # Calculate progress
        total_tasks = len(tasks)
        completed_tasks = status_dist.get('completed', 0)
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate costs
        estimated_cost = sum(t.get('estimated_cost', 0) for t in tasks)
        actual_cost = sum(t.get('actual_cost', 0) for t in tasks)
        
        # Detect bottlenecks (tasks with many dependencies)
        task_dep_counts = defaultdict(int)
        for edge in edges:
            task_dep_counts[edge['target']] += 1
        
        bottlenecks = [
            {"task_id": task_id, "dependency_count": count}
            for task_id, count in task_dep_counts.items()
            if count >= 3  # Tasks with 3+ dependencies
        ]
        
        # Critical path info (from workflow engine)
        try:
            dep_analysis = self.engine.resolve_dependencies(workflow['workflow_id'])
            critical_path = dep_analysis.get('critical_path', [])
        except:
            critical_path = []
        
        return {
            "total_tasks": total_tasks,
            "total_edges": len(edges),
            "status_distribution": dict(status_dist),
            "department_distribution": dict(dept_dist),
            "priority_distribution": dict(priority_dist),
            "progress_percentage": round(progress, 2),
            "estimated_total_cost": estimated_cost,
            "actual_total_cost": actual_cost,
            "cost_variance": actual_cost - estimated_cost,
            "critical_path_length": len(critical_path),
            "bottlenecks": bottlenecks,
            "graph_complexity": {
                "nodes": len(nodes),
                "edges": len(edges),
                "density": (len(edges) / (len(nodes) * (len(nodes) - 1))) if len(nodes) > 1 else 0
            }
        }
    
    def _save_graph_to_db(
        self,
        workflow_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ):
        """Save or update graph nodes and edges in database"""
        from .database import get_db
        db = get_db()
        
        try:
            # Save nodes
            for node in nodes:
                query = """
                    INSERT INTO knowledge_graph_nodes 
                    (workflow_id, task_id, node_type, node_data, position, style)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (workflow_id, task_id)
                    DO UPDATE SET
                        node_data = EXCLUDED.node_data,
                        position = EXCLUDED.position,
                        style = EXCLUDED.style,
                        updated_at = CURRENT_TIMESTAMP
                """
                db.execute_query(
                    query,
                    (
                        workflow_id,
                        node['id'],
                        node['type'],
                        json.dumps(node['data']),
                        json.dumps(node['position']),
                        json.dumps(node['style'])
                    ),
                    fetch_all=False
                )
            
            # Save edges
            for edge in edges:
                query = """
                    INSERT INTO knowledge_graph_edges 
                    (workflow_id, source_task_id, target_task_id, edge_type, edge_data, style)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (workflow_id, source_task_id, target_task_id)
                    DO UPDATE SET
                        edge_data = EXCLUDED.edge_data,
                        style = EXCLUDED.style,
                        updated_at = CURRENT_TIMESTAMP
                """
                db.execute_query(
                    query,
                    (
                        workflow_id,
                        edge['source'],
                        edge['target'],
                        edge['type'],
                        json.dumps(edge['data']),
                        json.dumps(edge['style'])
                    ),
                    fetch_all=False
                )
            
            logger.info(f"✓ Saved graph to database: {len(nodes)} nodes, {len(edges)} edges")
        
        except Exception as e:
            logger.error(f"Failed to save graph to database: {e}")
    
    # ==================== GRAPH RETRIEVAL ====================
    
    def get_workflow_graph(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored graph from database"""
        from .database import get_db
        db = get_db()
        
        # Get nodes
        nodes_query = """
            SELECT task_id, node_type, node_data, position, style, updated_at
            FROM knowledge_graph_nodes
            WHERE workflow_id = %s
            ORDER BY task_id
        """
        nodes_result = db.execute_query(nodes_query, (workflow_id,))
        
        # Get edges
        edges_query = """
            SELECT source_task_id, target_task_id, edge_type, edge_data, style
            FROM knowledge_graph_edges
            WHERE workflow_id = %s
            ORDER BY source_task_id, target_task_id
        """
        edges_result = db.execute_query(edges_query, (workflow_id,))
        
        if not nodes_result:
            return None
        
        # Build graph data
        nodes = []
        for row in nodes_result:
            nodes.append({
                "id": str(row['task_id']),
                "type": row['node_type'],
                "data": row['node_data'] if isinstance(row['node_data'], dict) else json.loads(row['node_data']),
                "position": row['position'] if isinstance(row['position'], dict) else json.loads(row['position']),
                "style": row['style'] if isinstance(row['style'], dict) else json.loads(row['style'])
            })
        
        edges = []
        for row in edges_result:
            edges.append({
                "id": f"{row['source_task_id']}->{row['target_task_id']}",
                "source": str(row['source_task_id']),
                "target": str(row['target_task_id']),
                "type": row['edge_type'],
                "data": row['edge_data'] if isinstance(row['edge_data'], dict) else json.loads(row['edge_data']),
                "style": row['style'] if isinstance(row['style'], dict) else json.loads(row['style'])
            })
        
        workflow = self.queries.get_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow['workflow_name'] if workflow else "Unknown",
            "nodes": nodes,
            "edges": edges,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    # ==================== GRAPH ANALYSIS ====================
    
    def analyze_graph_structure(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze graph structure and provide insights"""
        graph = self.get_workflow_graph(workflow_id)
        
        if not graph:
            graph = self.generate_workflow_graph(workflow_id)
        
        nodes = graph['nodes']
        edges = graph['edges']
        
        # Build adjacency lists
        incoming = defaultdict(list)
        outgoing = defaultdict(list)
        
        for edge in edges:
            outgoing[edge['source']].append(edge['target'])
            incoming[edge['target']].append(edge['source'])
        
        # Find start nodes (no incoming edges)
        start_nodes = [n['id'] for n in nodes if n['id'] not in incoming]
        
        # Find end nodes (no outgoing edges)
        end_nodes = [n['id'] for n in nodes if n['id'] not in outgoing]
        
        # Find hub nodes (many connections)
        hub_nodes = []
        for node in nodes:
            node_id = node['id']
            total_connections = len(incoming[node_id]) + len(outgoing[node_id])
            if total_connections >= 4:
                hub_nodes.append({
                    "task_id": node_id,
                    "label": node['label'],
                    "incoming": len(incoming[node_id]),
                    "outgoing": len(outgoing[node_id]),
                    "total": total_connections
                })
        
        # Calculate graph depth (longest path)
        max_depth = self._calculate_graph_depth(nodes, edges)
        
        return {
            "workflow_id": workflow_id,
            "structure": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "start_nodes": start_nodes,
                "end_nodes": end_nodes,
                "max_depth": max_depth
            },
            "centrality": {
                "hub_nodes": hub_nodes
            },
            "insights": self._generate_insights(nodes, edges, start_nodes, end_nodes, hub_nodes)
        }
    
    def _calculate_graph_depth(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> int:
        """Calculate maximum depth of graph (longest path)"""
        # Build adjacency list
        graph = defaultdict(list)
        for edge in edges:
            graph[edge['source']].append(edge['target'])
        
        # Find nodes with no incoming edges (start nodes)
        has_incoming = {edge['target'] for edge in edges}
        start_nodes = [n['id'] for n in nodes if n['id'] not in has_incoming]
        
        if not start_nodes:
            return 0
        
        # BFS to find maximum depth
        from collections import deque
        
        max_depth = 0
        for start in start_nodes:
            queue = deque([(start, 0)])
            visited = set()
            
            while queue:
                node, depth = queue.popleft()
                
                if node in visited:
                    continue
                visited.add(node)
                
                max_depth = max(max_depth, depth)
                
                for neighbor in graph[node]:
                    queue.append((neighbor, depth + 1))
        
        return max_depth
    
    def _generate_insights(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        start_nodes: List[str],
        end_nodes: List[str],
        hub_nodes: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate human-readable insights about the graph"""
        insights = []
        
        # Complexity insights
        if len(nodes) > 20:
            insights.append(f"Large workflow with {len(nodes)} tasks - consider breaking into sub-workflows")
        
        if len(edges) / len(nodes) > 2:
            insights.append("High dependency density - tasks are highly interconnected")
        
        # Start/end node insights
        if len(start_nodes) > 3:
            insights.append(f"{len(start_nodes)} parallel entry points - workflow can start with multiple tasks simultaneously")
        
        if len(end_nodes) > 3:
            insights.append(f"{len(end_nodes)} parallel completion points - workflow has multiple independent endpoints")
        
        # Hub node insights
        if hub_nodes:
            insights.append(f"{len(hub_nodes)} bottleneck tasks identified - these are critical coordination points")
        
        # Status insights
        blocked_count = sum(1 for n in nodes if n['data']['status'] == 'blocked')
        if blocked_count > 0:
            insights.append(f"⚠️  {blocked_count} tasks currently blocked - review dependencies")
        
        return insights


# Singleton instance
_kg_generator = None


def get_kg_generator() -> KnowledgeGraphGenerator:
    """Get knowledge graph generator singleton"""
    global _kg_generator
    if _kg_generator is None:
        _kg_generator = KnowledgeGraphGenerator()
    return _kg_generator
