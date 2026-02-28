import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { 
  ArrowLeft, RefreshCw, ZoomIn, ZoomOut, Maximize,
  Info, AlertCircle 
} from 'lucide-react';

// Simple UI component replacements
const Card = ({ children, className = '' }) => <div className={`bg-white rounded-lg shadow ${className}`}>{children}</div>;
const CardHeader = ({ children, className = '' }) => <div className={`p-6 border-b ${className}`}>{children}</div>;
const CardTitle = ({ children, className = '' }) => <h2 className={`text-xl font-bold text-gray-900 ${className}`}>{children}</h2>;
const CardContent = ({ children, className = '' }) => <div className={`p-6 ${className}`}>{children}</div>;
const Badge = ({ children, variant = 'default', className = '' }) => (
  <span className={`px-2 py-1 text-xs rounded-full ${variant === 'outline' ? 'border border-gray-300 bg-white' : ''} ${className}`}>
    {children}
  </span>
);
const Button = ({ children, variant = 'default', size = 'default', className = '', onClick, disabled }) => {
  const baseClasses = 'rounded transition inline-flex items-center justify-center';
  const variantClasses = variant === 'outline' 
    ? 'border border-gray-300 bg-white hover:bg-gray-50 text-gray-700'
    : 'bg-blue-600 hover:bg-blue-700 text-white';
  const sizeClasses = size === 'sm' ? 'px-2 py-1 text-sm' : 'px-4 py-2';
  return (
    <button 
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`} 
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

/**
 * Knowledge Graph Visualization
 * 
 * Interactive workflow dependency graph using React Flow
 */
export default function KnowledgeGraphVisualization() {
  const { workflowId } = useParams();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [graphData, setGraphData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (workflowId) {
      fetchGraphData();
      fetchAnalysis();
    }
  }, [workflowId]);

  const fetchGraphData = async (regenerate = false) => {
    try {
      setLoading(true);
      const url = `/api/task-orchestration/workflows/${workflowId}/graph${regenerate ? '?regenerate=true' : ''}`;
      const response = await fetch(url);
      const data = await response.json();
      
      setGraphData(data);
      
      // Transform nodes for React Flow
      const flowNodes = data.nodes.map((node) => ({
        id: node.id,
        type: 'default',
        data: {
          label: (
            <div className="p-2 text-center min-w-[150px]">
              <div className="font-semibold text-sm">{node.label}</div>
              <div className="text-xs text-gray-500 mt-1">{node.data.department}</div>
              <Badge className={`mt-1 text-xs ${getStatusBadgeColor(node.data.status)}`}>
                {node.data.status}
              </Badge>
            </div>
          ),
          ...node.data
        },
        position: node.position || { x: 0, y: 0 },
        style: {
          ...node.style,
          width: 200,
          borderWidth: 2,
          borderColor: node.style?.borderColor || '#1e293b',
          borderRadius: 8,
          padding: 0
        }
      }));
      
      // Transform edges for React Flow
      const flowEdges = data.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: edge.data?.is_mandatory === false ? false : true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20
        },
        style: {
          ...edge.style,
          stroke: edge.data?.is_mandatory === false ? '#9ca3af' : '#1e293b',
          strokeWidth: 2
        },
        label: edge.type !== 'finish_to_start' ? edge.type.replace('_', ' ') : ''
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (error) {
      console.error('Failed to fetch graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`/api/task-orchestration/workflows/${workflowId}/graph/analysis`);
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
    }
  };

  const getStatusBadgeColor = (status) => {
    const colors = {
      'pending': 'bg-gray-400',
      'ready': 'bg-blue-500',
      'in_progress': 'bg-amber-500',
      'completed': 'bg-green-500',
      'blocked': 'bg-red-500',
      'failed': 'bg-red-600',
      'cancelled': 'bg-gray-500'
    };
    return colors[status] || 'bg-gray-400';
  };

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const handleRegenerateGraph = () => {
    fetchGraphData(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Generating workflow graph...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.history.back()}
            >
              <ArrowLeft size={16} />
            </Button>
            <div>
              <h1 className="text-2xl font-bold">
                {graphData?.workflow_name || 'Workflow Graph'}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                {nodes.length} tasks • {edges.length} dependencies
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerateGraph}
            >
              <RefreshCw size={16} className="mr-2" />
              Regenerate
            </Button>
          </div>
        </div>
      </div>

      {/* Graph Container */}
      <div className="flex-1 flex">
        {/* Main Graph Area */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Background />
            <Controls />
            <MiniMap 
              nodeColor={(node) => {
                const status = node.data.status;
                const colors = {
                  'completed': '#10b981',
                  'in_progress': '#f59e0b',
                  'blocked': '#ef4444',
                  'ready': '#3b82f6',
                  'pending': '#94a3b8'
                };
                return colors[status] || '#9ca3af';
              }}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
          </ReactFlow>
        </div>

        {/* Side Panel */}
        <div className="w-80 bg-white border-l p-4 overflow-y-auto">
          {/* Selected Node Info */}
          {selectedNode ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Task Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Title</p>
                  <p className="font-medium">{selectedNode.data.label}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <Badge className={getStatusBadgeColor(selectedNode.data.status)}>
                    {selectedNode.data.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Department</p>
                  <p className="font-medium">{selectedNode.data.department}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Priority</p>
                  <Badge variant="outline">{selectedNode.data.priority}</Badge>
                </div>
                {selectedNode.data.estimated_duration && (
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-medium">{selectedNode.data.estimated_duration}h</p>
                  </div>
                )}
                {selectedNode.data.estimated_cost && (
                  <div>
                    <p className="text-sm text-gray-500">Estimated Cost</p>
                    <p className="font-medium">
                      ${selectedNode.data.estimated_cost.toLocaleString()}
                    </p>
                  </div>
                )}
                <Button 
                  className="w-full mt-4"
                  onClick={() => window.location.href = `/tasks/${selectedNode.id}`}
                >
                  View Task Details
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Info size={32} className="mx-auto mb-2 text-gray-300" />
              <p className="text-sm">Click on a task to see details</p>
            </div>
          )}

          {/* Graph Analysis */}
          {analysis && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="text-lg">Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-500">Graph Depth</p>
                  <p className="font-bold text-lg">{analysis.structure.max_depth}</p>
                </div>
                <div>
                  <p className="text-gray-500">Start Nodes</p>
                  <p className="font-medium">{analysis.structure.start_nodes.length}</p>
                </div>
                <div>
                  <p className="text-gray-500">End Nodes</p>
                  <p className="font-medium">{analysis.structure.end_nodes.length}</p>
                </div>
                
                {analysis.centrality.hub_nodes.length > 0 && (
                  <div className="pt-3 border-t">
                    <p className="text-gray-500 mb-2">Bottleneck Tasks</p>
                    <div className="space-y-1">
                      {analysis.centrality.hub_nodes.map((hub) => (
                        <div key={hub.task_id} className="text-xs bg-orange-50 p-2 rounded">
                          <p className="font-medium">{hub.label}</p>
                          <p className="text-gray-500">
                            {hub.total} connections
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {analysis.insights && analysis.insights.length > 0 && (
                  <div className="pt-3 border-t">
                    <p className="text-gray-500 mb-2">Insights</p>
                    <div className="space-y-2">
                      {analysis.insights.map((insight, idx) => (
                        <div key={idx} className="text-xs bg-blue-50 p-2 rounded flex gap-2">
                          <Info size={14} className="text-blue-500 flex-shrink-0 mt-0.5" />
                          <p className="text-gray-700">{insight}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Legend */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-lg">Legend</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span>Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-amber-500 rounded"></div>
                <span>In Progress</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span>Ready</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-gray-400 rounded"></div>
                <span>Pending</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span>Blocked/Failed</span>
              </div>
              <div className="border-t pt-2 mt-2">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-8 h-0.5 bg-gray-900"></div>
                  <span>Mandatory</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-0.5 bg-gray-400 dashed"></div>
                  <span>Optional</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
