import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, Workflow, CheckCircle2, Clock, AlertCircle, XCircle,
  TrendingUp, Users, Calendar, DollarSign, Target, Loader2, ChevronRight,
  PlayCircle, PauseCircle, Link as LinkIcon, AlertTriangle, Building2,
  BarChart3, Activity, Zap, Shield
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const WorkflowDetailPage = () => {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedStatus, setSelectedStatus] = useState('all')

  useEffect(() => {
    fetchWorkflowDetails()
  }, [workflowId])

  const fetchWorkflowDetails = async () => {
    try {
      setLoading(true)
      const response = await fetch(
        `${API_BASE}/api/task-orchestration/workflows/${workflowId}/detailed`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch workflow details')
      }
      
      const result = await response.json()
      setData(result)
      setError(null)
    } catch (err) {
      console.error('Error fetching workflow:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'completed': 'bg-green-500',
      'in_progress': 'bg-blue-500',
      'ready': 'bg-purple-500',
      'pending': 'bg-gray-400',
      'blocked': 'bg-red-500',
      'cancelled': 'bg-gray-600'
    }
    return colors[status] || 'bg-gray-400'
  }

  const getStatusIcon = (status) => {
    const icons = {
      'completed': CheckCircle2,
      'in_progress': PlayCircle,
      'ready': Clock,
      'pending': Clock,
      'blocked': AlertCircle,
      'cancelled': XCircle
    }
    return icons[status] || Clock
  }

  const getPriorityColor = (priority) => {
    const colors = {
      'low': 'text-gray-500 bg-gray-100',
      'medium': 'text-blue-600 bg-blue-100',
      'high': 'text-orange-600 bg-orange-100',
      'critical': 'text-red-600 bg-red-100'
    }
    return colors[priority] || colors['medium']
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin text-blue-500 mx-auto mb-4" size={48} />
          <p className="text-gray-600 text-lg">Loading workflow details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="backdrop-blur-md bg-white/70 rounded-3xl p-8 border border-white/40 shadow-xl max-w-md">
          <AlertCircle className="text-red-500 mx-auto mb-4" size={48} />
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error Loading Workflow</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate(-1)}
            className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl font-semibold"
          >
            Go Back
          </motion.button>
        </div>
      </div>
    )
  }

  if (!data) return null

  const { workflow, progress, tasks, tasks_by_status, stalled_tasks, blocking_departments, department_involvement } = data
  const filteredTasks = selectedStatus === 'all' ? tasks : tasks_by_status[selectedStatus] || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="backdrop-blur-md bg-white/70 border-b border-white/20 sticky top-0 z-30 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05, x: -5 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate(-1)}
                className="p-2 rounded-xl bg-white/60 hover:bg-white/80 transition-all"
              >
                <ArrowLeft size={24} className="text-gray-700" />
              </motion.button>
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-500 shadow-lg">
                  <Workflow className="text-white" size={24} />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">{workflow.workflow_name}</h1>
                  <p className="text-sm text-gray-600">Workflow Details & Progress</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-4 py-2 rounded-full text-sm font-bold ${getStatusColor(workflow.status)} text-white`}>
                {workflow.status.toUpperCase().replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="backdrop-blur-md bg-white/80 rounded-2xl p-6 border border-white/40 shadow-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <Target className="text-blue-500" size={24} />
              <span className="text-3xl font-bold text-gray-800">{progress.completion_percentage}%</span>
            </div>
            <p className="text-sm text-gray-600 font-semibold">Overall Progress</p>
            <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress.completion_percentage}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="backdrop-blur-md bg-white/80 rounded-2xl p-6 border border-white/40 shadow-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <CheckCircle2 className="text-green-500" size={24} />
              <span className="text-3xl font-bold text-gray-800">{progress.completed_tasks}</span>
            </div>
            <p className="text-sm text-gray-600 font-semibold">Completed Tasks</p>
            <p className="text-xs text-gray-500 mt-1">of {progress.total_tasks} total</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="backdrop-blur-md bg-white/80 rounded-2xl p-6 border border-white/40 shadow-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <Activity className="text-blue-500" size={24} />
              <span className="text-3xl font-bold text-gray-800">{progress.in_progress_tasks}</span>
            </div>
            <p className="text-sm text-gray-600 font-semibold">In Progress</p>
            <p className="text-xs text-gray-500 mt-1">Active tasks</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="backdrop-blur-md bg-white/80 rounded-2xl p-6 border border-white/40 shadow-lg"
          >
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="text-red-500" size={24} />
              <span className="text-3xl font-bold text-gray-800">{progress.blocked_tasks}</span>
            </div>
            <p className="text-sm text-gray-600 font-semibold">Blocked Tasks</p>
            <p className="text-xs text-gray-500 mt-1">{progress.tasks_remaining} remaining</p>
          </motion.div>
        </div>

        {/* Stalled Tasks Alert */}
        {stalled_tasks && stalled_tasks.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="backdrop-blur-md bg-red-50/80 border-l-4 border-red-500 rounded-2xl p-6 mb-8 shadow-lg"
          >
            <div className="flex items-start gap-4">
              <AlertTriangle className="text-red-500 flex-shrink-0" size={24} />
              <div className="flex-1">
                <h3 className="text-lg font-bold text-red-800 mb-2">
                  {stalled_tasks.length} Stalled Task{stalled_tasks.length !== 1 ? 's' : ''}
                </h3>
                <div className="space-y-2">
                  {stalled_tasks.map((stalled, idx) => (
                    <div key={idx} className="bg-white/60 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-gray-800">{stalled.task.task_title}</span>
                        <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-semibold">
                          {stalled.department}
                        </span>
                      </div>
                      <p className="text-sm text-red-600 flex items-center gap-2">
                        <AlertCircle size={14} />
                        {stalled.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Blocking Departments */}
        {blocking_departments && blocking_departments.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="backdrop-blur-md bg-white/80 rounded-2xl p-6 border border-white/40 shadow-lg mb-8"
          >
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Shield className="text-orange-500" size={20} />
              Departments Causing Delays
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {blocking_departments.map((item, idx) => (
                <div key={idx} className="bg-orange-50 rounded-xl p-4 border border-orange-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Building2 size={16} className="text-orange-600" />
                      <span className="font-semibold text-gray-800 capitalize">{item.department}</span>
                    </div>
                    <span className="bg-orange-200 text-orange-800 px-3 py-1 rounded-full text-sm font-bold">
                      {item.blocking_count}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">Blocking {item.blocking_count} task{item.blocking_count !== 1 ? 's' : ''}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Department Involvement */}
        {department_involvement && Object.keys(department_involvement).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="backdrop-blur-md bg-white/80 rounded-2xl p-6 border border-white/40 shadow-lg mb-8"
          >
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Users className="text-blue-500" size={20} />
              Department Involvement
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(department_involvement).map(([dept, stats]) => (
                <div key={dept} className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
                  <h4 className="font-bold text-gray-800 mb-3 capitalize flex items-center gap-2">
                    <Building2 size={16} className="text-blue-600" />
                    {dept}
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total:</span>
                      <span className="font-bold text-gray-800">{stats.total_tasks}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-600">Completed:</span>
                      <span className="font-bold text-green-700">{stats.completed || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-blue-600">In Progress:</span>
                      <span className="font-bold text-blue-700">{stats.in_progress || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Pending:</span>
                      <span className="font-bold text-gray-700">{stats.pending || 0}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Task Filter */}
        <div className="flex items-center gap-3 mb-6 overflow-x-auto pb-2">
          {['all', 'completed', 'in_progress', 'ready', 'pending', 'blocked'].map((status) => {
            const count = status === 'all' ? tasks.length : (tasks_by_status[status]?.length || 0)
            return (
              <motion.button
                key={status}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedStatus(status)}
                className={`px-4 py-2 rounded-xl font-semibold text-sm whitespace-nowrap transition-all ${
                  selectedStatus === status
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-md'
                    : 'bg-white/60 text-gray-700 hover:bg-white/80'
                }`}
              >
                {status.replace('_', ' ').toUpperCase()} ({count})
              </motion.button>
            )
          })}
        </div>

        {/* Tasks List */}
        <div className="space-y-4">
          <AnimatePresence mode="wait">
            {filteredTasks.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="backdrop-blur-md bg-white/70 rounded-2xl p-12 text-center border border-white/40"
              >
                <Clock size={48} className="mx-auto text-gray-300 mb-4" />
                <p className="text-gray-600">No tasks in this category</p>
              </motion.div>
            ) : (
              filteredTasks.map((task, index) => {
                const StatusIcon = getStatusIcon(task.status)
                return (
                  <motion.div
                    key={task.task_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.05 }}
                    className={`backdrop-blur-md bg-white/80 rounded-2xl p-6 border shadow-lg hover:shadow-xl transition-all ${
                      task.is_blocked ? 'border-red-300 bg-red-50/50' : 'border-white/40'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-4 flex-1">
                        <div className={`p-3 rounded-xl ${getStatusColor(task.status)} bg-opacity-10`}>
                          <StatusIcon className={`${getStatusColor(task.status).replace('bg-', 'text-')}`} size={24} />
                        </div>
                        <div className="flex-1">
                          <h4 className="text-lg font-bold text-gray-800 mb-1">{task.task_title}</h4>
                          <p className="text-sm text-gray-600 mb-3">{task.task_description}</p>
                          
                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Building2 size={14} />
                              <span className="capitalize font-semibold">{task.assigned_department}</span>
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock size={14} />
                              {task.estimated_duration_hours}h estimated
                            </span>
                            {task.estimated_cost > 0 && (
                              <span className="flex items-center gap-1">
                                <DollarSign size={14} />
                                ${task.estimated_cost.toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getPriorityColor(task.priority)}`}>
                        {task.priority?.toUpperCase() || 'MEDIUM'}
                      </span>
                    </div>

                    {/* Stall Reason */}
                    {task.stall_reason && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 mb-3">
                        <p className="text-sm text-yellow-800 flex items-center gap-2">
                          <AlertTriangle size={14} />
                          <span className="font-semibold">Stall Reason:</span> {task.stall_reason}
                        </p>
                      </div>
                    )}

                    {/* Blocking Dependencies */}
                    {task.blocking_dependencies && task.blocking_dependencies.length > 0 && (
                      <div className="bg-red-50 border border-red-200 rounded-xl p-4 mt-3">
                        <p className="text-sm font-bold text-red-800 mb-2 flex items-center gap-2">
                          <LinkIcon size={14} />
                          Blocked by {task.blocking_dependencies.length} task{task.blocking_dependencies.length !== 1 ? 's' : ''}:
                        </p>
                        <div className="space-y-2">
                          {task.blocking_dependencies.map((dep, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-white/60 rounded-lg p-2">
                              <span className="text-sm text-gray-700">{dep.task_title}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full capitalize">
                                  {dep.department}
                                </span>
                                <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(dep.status)} text-white`}>
                                  {dep.status}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Dates */}
                    {(task.estimated_start_date || task.estimated_end_date) && (
                      <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                        {task.estimated_start_date && (
                          <span className="flex items-center gap-1">
                            <Calendar size={12} />
                            Start: {formatDate(task.estimated_start_date)}
                          </span>
                        )}
                        {task.estimated_end_date && (
                          <span className="flex items-center gap-1">
                            <Calendar size={12} />
                            End: {formatDate(task.estimated_end_date)}
                          </span>
                        )}
                      </div>
                    )}
                  </motion.div>
                )
              })
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

export default WorkflowDetailPage
