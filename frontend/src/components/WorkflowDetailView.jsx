import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  ArrowLeft, Play, CheckCircle, Clock, AlertTriangle, 
  Users, DollarSign, Calendar, Plus, GitBranch, BrainCircuit
} from 'lucide-react';

// Simple UI component replacements
const Card = ({ children, className = '' }) => <div className={`bg-white rounded-lg shadow ${className}`}>{children}</div>;
const CardHeader = ({ children, className = '' }) => <div className={`p-6 border-b ${className}`}>{children}</div>;
const CardTitle = ({ children, className = '' }) => <h2 className={`text-xl font-bold text-gray-900 ${className}`}>{children}</h2>;
const CardDescription = ({ children, className = '' }) => <p className={`text-sm text-gray-500 mt-1 ${className}`}>{children}</p>;
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
const Progress = ({ value, className = '' }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
    <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${value}%` }}></div>
  </div>
);

/**
 * Workflow Detail View
 * 
 * Shows workflow details, tasks, dependencies, and actions
 */
export default function WorkflowDetailView() {
  const { workflowId } = useParams();
  const [workflow, setWorkflow] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState(null);
  const [dependencies, setDependencies] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (workflowId) {
      fetchWorkflowData();
    }
  }, [workflowId]);

  const fetchWorkflowData = async () => {
    try {
      setLoading(true);

      // Fetch workflow details
      const workflowRes = await fetch(`/api/task-orchestration/workflows/${workflowId}`);
      const workflowData = await workflowRes.json();
      setWorkflow(workflowData);

      // Fetch progress
      const progressRes = await fetch(`/api/task-orchestration/workflows/${workflowId}/progress`);
      const progressData = await progressRes.json();
      setProgress(progressData);

      // Fetch tasks
      const tasksRes = await fetch(`/api/task-orchestration/tasks?workflow_id=${workflowId}&limit=200`);
      const tasksData = await tasksRes.json();
      setTasks(tasksData);

      // Fetch dependencies
      const depsRes = await fetch(`/api/task-orchestration/workflows/${workflowId}/dependencies`);
      const depsData = await depsRes.json();
      setDependencies(depsData);

    } catch (error) {
      console.error('Failed to fetch workflow data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startWorkflow = async () => {
    try {
      const response = await fetch(`/api/task-orchestration/workflows/${workflowId}/start`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'started') {
        alert(`Workflow started! ${result.ready_tasks.length} tasks ready to execute.`);
        fetchWorkflowData(); // Refresh
      }
    } catch (error) {
      console.error('Failed to start workflow:', error);
      alert('Failed to start workflow');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'bg-gray-400',
      'ready': 'bg-blue-500',
      'in_progress': 'bg-amber-500',
      'completed': 'bg-green-500',
      'blocked': 'bg-red-500',
      'failed': 'bg-red-600',
      'cancelled': 'bg-gray-500'
    };
    return colors[status] || 'bg-gray-500';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'low': 'text-gray-500',
      'medium': 'text-blue-500',
      'high': 'text-orange-500',
      'critical': 'text-red-500',
      'emergency': 'text-red-700'
    };
    return colors[priority] || 'text-gray-500';
  };

  const formatCurrency = (amount) => {
    if (!amount) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center py-12">
          <AlertTriangle size={48} className="mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-semibold">Workflow Not Found</h2>
          <Button className="mt-4" onClick={() => window.history.back()}>
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => window.history.back()}
        >
          <ArrowLeft size={16} />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900">{workflow.workflow_name}</h1>
            <Badge className={`${getStatusColor(workflow.status)} text-white`}>
              {workflow.status.replace('_', ' ')}
            </Badge>
          </div>
          <p className="text-gray-500 mt-1">{workflow.workflow_description || 'No description'}</p>
        </div>
        <div className="flex gap-2">
          {workflow.status === 'ready' && (
            <Button onClick={startWorkflow} className="flex items-center gap-2">
              <Play size={16} />
              Start Workflow
            </Button>
          )}
          <Button variant="outline" onClick={() => window.location.href = `/workflows/${workflowId}/graph`}>
            <GitBranch size={16} className="mr-2" />
            View Graph
          </Button>
        </div>
      </div>

      {/* Progress Overview */}
      {progress && (
        <Card>
          <CardHeader>
            <CardTitle>Progress Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              <div>
                <p className="text-sm text-gray-500">Total Tasks</p>
                <p className="text-2xl font-bold">{progress.total_tasks}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Completed</p>
                <p className="text-2xl font-bold text-green-600">{progress.completed_tasks}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">In Progress</p>
                <p className="text-2xl font-bold text-amber-600">{progress.in_progress_tasks}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Blocked</p>
                <p className="text-2xl font-bold text-red-600">{progress.blocked_tasks}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Progress</p>
                <p className="text-2xl font-bold">{progress.progress_percentage}%</p>
              </div>
            </div>
            <Progress 
              value={progress.progress_percentage} 
              className="mt-4"
            />
          </CardContent>
        </Card>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <DollarSign className="text-green-500" size={32} />
              <div>
                <p className="text-sm text-gray-500">Estimated Cost</p>
                <p className="text-xl font-bold">
                  {formatCurrency(progress?.estimated_total_cost || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Clock className="text-blue-500" size={32} />
              <div>
                <p className="text-sm text-gray-500">Estimated Duration</p>
                <p className="text-xl font-bold">
                  {progress?.estimated_total_hours || 0} hours
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Users className="text-purple-500" size={32} />
              <div>
                <p className="text-sm text-gray-500">Departments</p>
                <p className="text-xl font-bold">
                  {progress?.departments_involved || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dependency Analysis */}
      {dependencies && dependencies.circular_dependencies?.length > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-700 flex items-center gap-2">
              <AlertTriangle size={20} />
              Circular Dependencies Detected!
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">
              Fix circular dependencies before starting workflow:
            </p>
            <ul className="list-disc list-inside mt-2 text-sm text-red-600">
              {dependencies.circular_dependencies.map((cycle, idx) => (
                <li key={idx}>{cycle.join(' → ')}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Tasks List */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Tasks</CardTitle>
              <CardDescription>All tasks in this workflow</CardDescription>
            </div>
            <Button size="sm" className="flex items-center gap-2">
              <Plus size={16} />
              Add Task
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {tasks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No tasks yet. Add your first task to get started.</p>
              </div>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.task_id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition"
                  onClick={() => window.location.href = `/tasks/${task.task_id}`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-500 font-mono">#{task.task_sequence}</span>
                      <h3 className="font-semibold text-gray-900">{task.task_title}</h3>
                      <Badge className={`${getStatusColor(task.task_status)} text-white text-xs`}>
                        {task.task_status.replace('_', ' ')}
                      </Badge>
                      {task.priority !== 'low' && (
                        <Badge variant="outline" className={`${getPriorityColor(task.priority)} text-xs`}>
                          {task.priority}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Users size={12} />
                        {task.assigned_department}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={12} />
                        {task.estimated_duration_hours}h
                      </span>
                      <span className="flex items-center gap-1">
                        <DollarSign size={12} />
                        {formatCurrency(task.estimated_cost)}
                      </span>
                      {task.deadline && (
                        <span className="flex items-center gap-1">
                          <Calendar size={12} />
                          {new Date(task.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {task.task_status === 'blocked' && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-purple-600"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.location.href = `/tasks/${task.task_id}/contingency`;
                        }}
                      >
                        <BrainCircuit size={14} className="mr-1" />
                        Contingency
                      </Button>
                    )}
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
