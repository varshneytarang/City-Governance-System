import React, { useState, useEffect } from 'react';
import { Plus, Workflow, AlertCircle, CheckCircle, Clock, User, X, Calendar, DollarSign, Users as UsersIcon, Sparkles, Edit, Trash2, Save, Network } from 'lucide-react';
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';

/**
 * Task Orchestration Dashboard
 * 
 * Main dashboard for workflow and task management
 */
export default function TaskOrchestrationDashboard({ department = null }) {
  const [workflows, setWorkflows] = useState([]);
  const [stats, setStats] = useState({
    total_workflows: 0,
    active_workflows: 0,
    total_tasks: 0,
    completed_tasks: 0
  });
  const [loading, setLoading] = useState(true);
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [generatingTasks, setGeneratingTasks] = useState(false);
  const [aiGeneratedTasks, setAiGeneratedTasks] = useState([]);
  const [showTaskPreview, setShowTaskPreview] = useState(false);
  const [editingTaskIndex, setEditingTaskIndex] = useState(null);
  
  // Workflow form state
  const [workflowForm, setWorkflowForm] = useState({
    workflow_name: '',
    workflow_description: '',
    initiated_by_department: department || '',
    priority: 'medium',
    estimated_total_cost: ''
  });
  
  // Task form state
  const [taskForm, setTaskForm] = useState({
    workflow_id: '',
    task_title: '',
    task_description: '',
    assigned_department: department || '',
    assigned_to: '',
    priority: 'medium',
    estimated_duration_hours: '',
    estimated_cost: ''
  });

  useEffect(() => {
    fetchDashboardData();
  }, [department]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch workflows with optional department filter
      const departmentParam = department ? `&department=${department}` : '';
      const workflowsResponse = await fetch(`/api/task-orchestration/workflows?limit=20${departmentParam}`);
      const workflowsData = await workflowsResponse.json();
      setWorkflows(workflowsData);

      // Calculate stats
      const activeWorkflows = workflowsData.filter(w => w.status === 'in_progress').length;
      
      // Fetch all tasks for stats
      const tasksResponse = await fetch('/api/task-orchestration/tasks?limit=200');
      const tasksData = await tasksResponse.json();
      
      const completedTasks = tasksData.filter(t => t.task_status === 'completed').length;

      setStats({
        total_workflows: workflowsData.length,
        active_workflows: activeWorkflows,
        total_tasks: tasksData.length,
        completed_tasks: completedTasks
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-500',
      'pending_approval': 'bg-yellow-500',
      'ready': 'bg-blue-500',
      'in_progress': 'bg-amber-500',
      'completed': 'bg-green-500',
      'blocked': 'bg-red-500',
      'cancelled': 'bg-gray-400'
    };
    return colors[status] || 'bg-gray-500';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const createWorkflow = async (e) => {
    e.preventDefault();
    setCreating(true);
    
    try {
      // Convert form data with proper number handling
      const workflowData = {
        ...workflowForm,
        estimated_total_cost: parseFloat(workflowForm.estimated_total_cost) || 0
      };
      
      const response = await fetch('/api/task-orchestration/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflowData)
      });
      
      if (response.ok) {
        setShowWorkflowModal(false);
        setWorkflowForm({
          workflow_name: '',
          workflow_description: '',
          initiated_by_department: department || '',
          priority: 'medium',
          estimated_total_cost: ''
        });
        fetchDashboardData(); // Refresh data
      } else {
        alert('Failed to create workflow');
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
      alert('Error creating workflow');
    } finally {
      setCreating(false);
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    setCreating(true);
    
    try {
      // Convert form data with proper number handling
      const taskData = {
        ...taskForm,
        estimated_duration_hours: parseFloat(taskForm.estimated_duration_hours) || 0,
        estimated_cost: parseFloat(taskForm.estimated_cost) || 0
      };
      
      const response = await fetch('/api/task-orchestration/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
      });
      
      if (response.ok) {
        setShowTaskModal(false);
        setTaskForm({
          workflow_id: '',
          task_title: '',
          task_description: '',
          assigned_department: department || '',
          assigned_to: '',
          priority: 'medium',
          estimated_duration_hours: '',
          estimated_cost: ''
        });
        fetchDashboardData(); // Refresh data
      } else {
        alert('Failed to create task');
      }
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Error creating task');
    } finally {
      setCreating(false);
    }
  };

  const generateTasksWithAI = async () => {
    setGeneratingTasks(true);
    
    try {
      // Convert form data with proper number handling
      const workflowData = {
        ...workflowForm,
        estimated_total_cost: parseFloat(workflowForm.estimated_total_cost) || 0
      };
      
      const response = await fetch('/api/task-orchestration/workflows/generate-tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflowData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setAiGeneratedTasks(data.tasks || []);
        setShowTaskPreview(true);
      } else {
        alert('Failed to generate tasks with AI');
      }
    } catch (error) {
      console.error('Error generating tasks:', error);
      alert('Error generating tasks with AI');
    } finally {
      setGeneratingTasks(false);
    }
  };

  const createWorkflowWithTasks = async () => {
    setCreating(true);
    
    try {
      // 1. Create workflow with proper number handling
      const workflowData = {
        ...workflowForm,
        estimated_total_cost: parseFloat(workflowForm.estimated_total_cost) || 0
      };
      
      const workflowResponse = await fetch('/api/task-orchestration/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflowData)
      });
      
      if (!workflowResponse.ok) {
        throw new Error('Failed to create workflow');
      }
      
      const workflow = await workflowResponse.json();
      const workflowId = workflow.workflow_id;
      
      // 2. Create all tasks
      const taskPromises = aiGeneratedTasks.map(async (task, index) => {
        const taskData = {
          workflow_id: workflowId,
          task_title: task.task_title,
          task_description: task.task_description,
          assigned_department: task.assigned_department,
          assigned_to: task.assigned_to || '',
          priority: task.priority,
          estimated_duration_hours: parseFloat(task.estimated_duration_hours) || 0,
          estimated_cost: parseFloat(task.estimated_cost) || 0
        };
        
        const taskResponse = await fetch('/api/task-orchestration/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(taskData)
        });
        
        if (taskResponse.ok) {
          const createdTask = await taskResponse.json();
          return { index, taskId: createdTask.task_id, dependsOn: task.depends_on || [] };
        }
        return null;
      });
      
      const createdTasks = await Promise.all(taskPromises);
      
      // 3. Create dependencies
      for (const taskInfo of createdTasks) {
        if (taskInfo && taskInfo.dependsOn.length > 0) {
          for (const depIndex of taskInfo.dependsOn) {
            const dependencyTask = createdTasks[depIndex];
            if (dependencyTask) {
              await fetch('/api/task-orchestration/dependencies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  task_id: taskInfo.taskId,
                  depends_on_task_id: dependencyTask.taskId,
                  dependency_type: 'finish_to_start'
                })
              });
            }
          }
        }
      }
      
      // Reset and refresh
      setShowWorkflowModal(false);
      setShowTaskPreview(false);
      setAiGeneratedTasks([]);
      setWorkflowForm({
        workflow_name: '',
        workflow_description: '',
        initiated_by_department: department || '',
        priority: 'medium',
        estimated_total_cost: ''
      });
      fetchDashboardData();
      
    } catch (error) {
      console.error('Error creating workflow with tasks:', error);
      alert('Error creating workflow with tasks');
    } finally {
      setCreating(false);
    }
  };

  const updateAiTask = (index, field, value) => {
    const updated = [...aiGeneratedTasks];
    updated[index][field] = value;
    setAiGeneratedTasks(updated);
  };

  const removeAiTask = (index) => {
    const updated = aiGeneratedTasks.filter((_, i) => i !== index);
    setAiGeneratedTasks(updated);
  };

  const getTaskGraphData = () => {
    const nodes = aiGeneratedTasks.map((task, index) => ({
      id: `${index}`,
      data: { 
        label: (
          <div className="text-center">
            <div className="font-semibold text-xs">{task.task_title}</div>
            <div className="text-xs text-gray-500">{task.assigned_department}</div>
            <div className="text-xs text-gray-400">{task.estimated_duration_hours}h</div>
          </div>
        )
      },
      position: { 
        x: (index % 3) * 250, 
        y: Math.floor(index / 3) * 150 
      },
      style: {
        background: '#fff',
        border: '2px solid #3b82f6',
        borderRadius: '8px',
        padding: '10px',
        width: 180
      }
    }));

    const edges = [];
    aiGeneratedTasks.forEach((task, index) => {
      if (task.depends_on && task.depends_on.length > 0) {
        task.depends_on.forEach(depIndex => {
          edges.push({
            id: `e${depIndex}-${index}`,
            source: `${depIndex}`,
            target: `${index}`,
            type: 'smoothstep',
            animated: true,
            markerEnd: { type: MarkerType.ArrowClosed },
            style: { stroke: '#3b82f6', strokeWidth: 2 }
          });
        });
      }
    });

    return { nodes, edges };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`${department ? 'max-w-full' : 'max-w-7xl mx-auto'} p-6 space-y-6`}>
      {/* Header */}
      {!department && (
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Task Orchestration</h1>
            <p className="text-gray-500 mt-1">Manage workflows and department tasks</p>
          </div>
          <button 
            onClick={() => setShowWorkflowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Plus size={20} />
            New Workflow
          </button>
        </div>
      )}

      {department && (
        <div className="flex justify-between items-center mb-2">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Department Tasks</h2>
            <p className="text-gray-500 mt-1">Workflows and tasks for {department} department</p>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setShowWorkflowModal(true)}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition"
            >
              <Workflow size={16} />
              New Workflow
            </button>
            <button 
              onClick={() => setShowTaskModal(true)}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition"
            >
              <Plus size={16} />
              New Task
            </button>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Workflows</p>
              <h3 className="text-2xl font-bold mt-1">{stats.total_workflows}</h3>
            </div>
            <Workflow className="text-blue-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Workflows</p>
              <h3 className="text-2xl font-bold mt-1">{stats.active_workflows}</h3>
            </div>
            <Clock className="text-amber-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Tasks</p>
              <h3 className="text-2xl font-bold mt-1">{stats.total_tasks}</h3>
            </div>
            <AlertCircle className="text-gray-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Completed Tasks</p>
              <h3 className="text-2xl font-bold mt-1">{stats.completed_tasks}</h3>
            </div>
            <CheckCircle className="text-green-500" size={32} />
          </div>
        </div>
      </div>

      {/* Workflows List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Recent Workflows</h2>
          <p className="text-sm text-gray-500 mt-1">View and manage active workflows</p>
        </div>
        <div className="p-6">
          <div className="space-y-3">
            {workflows.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Workflow size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">No workflows yet</p>
                <p className="text-sm mt-1">Create your first workflow to get started</p>
              </div>
            ) : (
              workflows.map((workflow) => (
                <div
                  key={workflow.workflow_id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition"
                  onClick={() => window.location.href = `/workflows/${workflow.workflow_id}`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-gray-900">{workflow.workflow_name}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(workflow.status)} text-white`}>
                        {workflow.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {workflow.workflow_description || 'No description'}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <User size={12} />
                        {workflow.created_by}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={12} />
                        Created: {formatDate(workflow.created_at)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {workflow.progress_percentage !== undefined && (
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-700">
                          {workflow.progress_percentage}%
                        </p>
                        <p className="text-xs text-gray-500">Progress</p>
                      </div>
                    )}
                    <button className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition">
                      View Details
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Create Workflow Modal */}
      {showWorkflowModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-2xl font-bold">Create New Workflow</h2>
              <button onClick={() => setShowWorkflowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={createWorkflow} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Workflow Name *
                </label>
                <input
                  type="text"
                  required
                  value={workflowForm.workflow_name}
                  onChange={(e) => setWorkflowForm({...workflowForm, workflow_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Water System Maintenance Q1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={workflowForm.workflow_description}
                  onChange={(e) => setWorkflowForm({...workflowForm, workflow_description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe the workflow objectives..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department *
                  </label>
                  <select
                    required
                    value={workflowForm.initiated_by_department}
                    onChange={(e) => setWorkflowForm({...workflowForm, initiated_by_department: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Department</option>
                    <option value="water">Water</option>
                    <option value="fire">Fire</option>
                    <option value="engineering">Engineering</option>
                    <option value="health">Health</option>
                    <option value="finance">Finance</option>
                    <option value="sanitation">Sanitation</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={workflowForm.priority}
                    onChange={(e) => setWorkflowForm({...workflowForm, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estimated Cost ($)
                </label>
                <input
                  type="number"
                  value={workflowForm.estimated_total_cost}
                  onChange={(e) => setWorkflowForm({...workflowForm, estimated_total_cost: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0"
                />
              </div>
              
              <div className="flex gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowWorkflowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={generateTasksWithAI}
                  disabled={generatingTasks || !workflowForm.workflow_name || !workflowForm.initiated_by_department}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Sparkles size={18} />
                  {generatingTasks ? 'Generating...' : 'Generate Tasks AI'}
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create Workflow'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Task Modal */}
      {showTaskModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-2xl font-bold">Create New Task</h2>
              <button onClick={() => setShowTaskModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={createTask} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Workflow *
                </label>
                <select
                  required
                  value={taskForm.workflow_id}
                  onChange={(e) => setTaskForm({...taskForm, workflow_id: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Workflow</option>
                  {workflows.map(w => (
                    <option key={w.workflow_id} value={w.workflow_id}>
                      {w.workflow_name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task Title *
                </label>
                <input
                  type="text"
                  required
                  value={taskForm.task_title}
                  onChange={(e) => setTaskForm({...taskForm, task_title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Inspect Zone A Pumps"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={taskForm.task_description}
                  onChange={(e) => setTaskForm({...taskForm, task_description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe the task details..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assigned Department *
                  </label>
                  <select
                    required
                    value={taskForm.assigned_department}
                    onChange={(e) => setTaskForm({...taskForm, assigned_department: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Department</option>
                    <option value="water">Water</option>
                    <option value="fire">Fire</option>
                    <option value="engineering">Engineering</option>
                    <option value="health">Health</option>
                    <option value="finance">Finance</option>
                    <option value="sanitation">Sanitation</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={taskForm.priority}
                    onChange={(e) => setTaskForm({...taskForm, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (hours)
                  </label>
                  <input
                    type="number"
                    value={taskForm.estimated_duration_hours}
                    onChange={(e) => setTaskForm({...taskForm, estimated_duration_hours: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Cost ($)
                  </label>
                  <input
                    type="number"
                    value={taskForm.estimated_cost}
                    onChange={(e) => setTaskForm({...taskForm, estimated_cost: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Assigned To
                </label>
                <input
                  type="text"
                  value={taskForm.assigned_to}
                  onChange={(e) => setTaskForm({...taskForm, assigned_to: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Employee name or ID"
                />
              </div>
              
              <div className="flex gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowTaskModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* AI Task Preview Modal */}
      {showTaskPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl w-full h-[90vh] flex flex-col">
            <div className="flex justify-between items-center p-6 border-b">
              <div>
                <h2 className="text-2xl font-bold">AI Generated Tasks Preview</h2>
                <p className="text-sm text-gray-500 mt-1">Review and edit tasks before creating workflow</p>
              </div>
              <button 
                onClick={() => setShowTaskPreview(false)} 
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
              {/* Graph Visualization */}
              <div className="flex-1 p-4 border-b md:border-b-0 md:border-r">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Network size={20} />
                  Task Dependency Graph
                </h3>
                <div className="h-[300px] md:h-full border rounded-lg bg-gray-50">
                  <ReactFlow
                    nodes={getTaskGraphData().nodes}
                    edges={getTaskGraphData().edges}
                    fitView
                    minZoom={0.5}
                    maxZoom={1.5}
                  >
                    <Background />
                    <Controls />
                  </ReactFlow>
                </div>
              </div>
              
              {/* Task List with Editing */}
              <div className="w-full md:w-96 flex flex-col">
                <div className="p-4 border-b bg-gray-50">
                  <h3 className="font-semibold flex items-center justify-between">
                    <span>Tasks ({aiGeneratedTasks.length})</span>
                    <span className="text-sm text-gray-500">
                      Total: ${aiGeneratedTasks.reduce((sum, t) => sum + (t.estimated_cost || 0), 0).toFixed(2)}
                    </span>
                  </h3>
                </div>
                
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {aiGeneratedTasks.map((task, index) => (
                    <div key={index} className="border rounded-lg p-3 bg-white">
                      {editingTaskIndex === index ? (
                        // Edit Mode
                        <div className="space-y-2">
                          <input
                            type="text"
                            value={task.task_title}
                            onChange={(e) => updateAiTask(index, 'task_title', e.target.value)}
                            className="w-full px-2 py-1 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                            placeholder="Task title"
                          />
                          <textarea
                            value={task.task_description}
                            onChange={(e) => updateAiTask(index, 'task_description', e.target.value)}
                            rows={2}
                            className="w-full px-2 py-1 text-sm border rounded focus:ring-2 focus:ring-blue-500"
                            placeholder="Description"
                          />
                          <div className="grid grid-cols-2 gap-2">
                            <input
                              type="number"
                              value={task.estimated_duration_hours}
                              onChange={(e) => updateAiTask(index, 'estimated_duration_hours', parseFloat(e.target.value))}
                              className="px-2 py-1 text-sm border rounded"
                              placeholder="Hours"
                            />
                            <input
                              type="number"
                              value={task.estimated_cost}
                              onChange={(e) => updateAiTask(index, 'estimated_cost', parseFloat(e.target.value))}
                              className="px-2 py-1 text-sm border rounded"
                              placeholder="Cost $"
                            />
                          </div>
                          <select
                            value={task.priority}
                            onChange={(e) => updateAiTask(index, 'priority', e.target.value)}
                            className="w-full px-2 py-1 text-sm border rounded"
                          >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="critical">Critical</option>
                          </select>
                          <select
                            value={task.assigned_department}
                            onChange={(e) => updateAiTask(index, 'assigned_department', e.target.value)}
                            className="w-full px-2 py-1 text-sm border rounded"
                          >
                            <option value="water">Water</option>
                            <option value="fire">Fire</option>
                            <option value="engineering">Engineering</option>
                            <option value="health">Health</option>
                            <option value="finance">Finance</option>
                            <option value="sanitation">Sanitation</option>
                          </select>
                          <button
                            onClick={() => setEditingTaskIndex(null)}
                            className="w-full px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 flex items-center justify-center gap-1"
                          >
                            <Save size={14} />
                            Save
                          </button>
                        </div>
                      ) : (
                        // View Mode
                        <div>
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <h4 className="font-medium text-sm">{index + 1}. {task.task_title}</h4>
                              <p className="text-xs text-gray-600 mt-1">{task.task_description}</p>
                            </div>
                            <div className="flex gap-1 ml-2">
                              <button
                                onClick={() => setEditingTaskIndex(index)}
                                className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                                title="Edit task"
                              >
                                <Edit size={14} />
                              </button>
                              <button
                                onClick={() => removeAiTask(index)}
                                className="p-1 text-red-600 hover:bg-red-50 rounded"
                                title="Remove task"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </div>
                          
                          <div className="flex flex-wrap gap-2 text-xs">
                            <span className={`px-2 py-0.5 rounded ${
                              task.priority === 'critical' ? 'bg-red-100 text-red-700' :
                              task.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                              task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {task.priority}
                            </span>
                            <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded capitalize">
                              {task.assigned_department}
                            </span>
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                              {task.estimated_duration_hours}h
                            </span>
                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded">
                              ${task.estimated_cost}
                            </span>
                            {task.depends_on && task.depends_on.length > 0 && (
                              <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded">
                                Depends: {task.depends_on.map(d => d + 1).join(', ')}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Footer Actions */}
            <div className="p-6 border-t bg-gray-50 flex gap-3">
              <button
                onClick={() => setShowTaskPreview(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-white transition"
              >
                Cancel
              </button>
              <button
                onClick={createWorkflowWithTasks}
                disabled={creating || aiGeneratedTasks.length === 0}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Sparkles size={18} />
                {creating ? 'Creating Workflow...' : `Create Workflow with ${aiGeneratedTasks.length} Tasks`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
