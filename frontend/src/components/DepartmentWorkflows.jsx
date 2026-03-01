import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Workflow, Plus, Calendar, Clock, Users, TrendingUp, CheckCircle2,
  AlertCircle, Loader2, ChevronRight, Star, ArrowRight, Building2
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const DepartmentWorkflows = ({ department }) => {
  const navigate = useNavigate()
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    fetchWorkflows()
  }, [department])

  const fetchWorkflows = async () => {
    try {
      setLoading(true)
      const response = await fetch(
        `${API_BASE}/api/task-orchestration/workflows/by-department/${department}`
      )
      
      if (!response.ok) {
        throw new Error('Failed to fetch workflows')
      }
      
      const data = await response.json()
      setWorkflows(data.workflows || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching workflows:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-700 border-gray-300',
      'active': 'bg-blue-100 text-blue-700 border-blue-300',
      'in_progress': 'bg-purple-100 text-purple-700 border-purple-300',
      'completed': 'bg-green-100 text-green-700 border-green-300',
      'on_hold': 'bg-yellow-100 text-yellow-700 border-yellow-300',
      'cancelled': 'bg-red-100 text-red-700 border-red-300'
    }
    return colors[status] || colors['draft']
  }

  const getPriorityColor = (priority) => {
    const colors = {
      'low': 'text-gray-500',
      'medium': 'text-blue-500',
      'high': 'text-orange-500',
      'critical': 'text-red-500'
    }
    return colors[priority] || colors['medium']
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  if (loading) {
    return (
      <div className="backdrop-blur-md bg-white/70 rounded-3xl p-8 border border-white/40 shadow-xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-blue-500" size={32} />
          <span className="ml-3 text-gray-600">Loading workflows...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="backdrop-blur-md bg-white/70 rounded-3xl p-8 border border-white/40 shadow-xl">
        <div className="flex items-center gap-3 text-red-600">
          <AlertCircle size={24} />
          <span>Error loading workflows: {error}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="backdrop-blur-md bg-white/70 rounded-3xl p-8 border border-white/40 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-500 shadow-lg">
            <Workflow className="text-white" size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Department Workflows</h2>
            <p className="text-sm text-gray-600">
              {workflows.length} workflow{workflows.length !== 1 ? 's' : ''} involving {department}
            </p>
          </div>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all"
        >
          <Plus size={18} />
          <span className="font-semibold">Create Workflow</span>
        </motion.button>
      </div>

      {/* Workflows Grid */}
      {workflows.length === 0 ? (
        <div className="text-center py-12">
          <Workflow size={48} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">No workflows yet</h3>
          <p className="text-gray-500 mb-4">Create your first workflow to get started</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl shadow-md hover:shadow-lg transition-all"
          >
            <Plus size={20} />
            <span className="font-semibold">Create First Workflow</span>
          </motion.button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {workflows.map((workflow, index) => {
            const involvement = workflow.department_involvement
            const isHighlighted = involvement.is_initiator || involvement.involvement_percentage > 50

            return (
              <motion.div
                key={workflow.workflow_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => navigate(`/workflow/${workflow.workflow_id}`)}
                className={`relative backdrop-blur-md bg-white/80 rounded-2xl p-6 border ${
                  isHighlighted 
                    ? 'border-blue-400 shadow-lg ring-2 ring-blue-200' 
                    : 'border-white/40 shadow-md'
                } hover:shadow-xl transition-all duration-300 cursor-pointer group`}
              >
                {/* Highlight Badge */}
                {isHighlighted && (
                  <div className="absolute -top-3 -right-3 px-3 py-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold rounded-full shadow-lg flex items-center gap-1">
                    <Star size={12} fill="currentColor" />
                    <span>Primary Role</span>
                  </div>
                )}

                {/* Status & Priority */}
                <div className="flex items-start justify-between mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(workflow.status)}`}>
                    {workflow.status.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className={`text-xs font-bold ${getPriorityColor(workflow.priority)}`}>
                    {workflow.priority?.toUpperCase() || 'MEDIUM'}
                  </span>
                </div>

                {/* Workflow Info */}
                <h3 className="text-lg font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">
                  {workflow.workflow_name}
                </h3>
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {workflow.workflow_description}
                </p>

                {/* Involvement Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center gap-2">
                    <Users size={16} className="text-blue-500" />
                    <div>
                      <div className="text-xs text-gray-500">Your Tasks</div>
                      <div className="text-sm font-bold text-gray-800">
                        {involvement.assigned_tasks_count} / {involvement.total_tasks_count}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-purple-500" />
                    <div>
                      <div className="text-xs text-gray-500">Involvement</div>
                      <div className="text-sm font-bold text-gray-800">
                        {involvement.involvement_percentage}%
                      </div>
                    </div>
                  </div>
                </div>

                {/* Department Badge */}
                {involvement.is_initiator && (
                  <div className="flex items-center gap-2 text-xs text-blue-600 mb-3">
                    <Building2 size={14} />
                    <span className="font-semibold">Initiated by your department</span>
                  </div>
                )}

                {/* Dates */}
                <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-200">
                  <div className="flex items-center gap-1">
                    <Calendar size={12} />
                    <span>{formatDate(workflow.planned_start_date)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock size={12} />
                    <span>{formatDate(workflow.planned_end_date)}</span>
                  </div>
                </div>

                {/* Hover Arrow */}
                <motion.div
                  className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity"
                  whileHover={{ x: 5 }}
                >
                  <ArrowRight size={20} className="text-blue-500" />
                </motion.div>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Create Workflow Modal Placeholder */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-3xl p-8 max-w-2xl w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Create New Workflow</h2>
              <p className="text-gray-600 mb-6">
                Navigate to the Task Orchestration Dashboard to create AI-powered workflows
              </p>
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setShowModal(false)
                    window.location.href = '/dashboard'
                  }}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all"
                >
                  Go to Dashboard
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowModal(false)}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-all"
                >
                  Cancel
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default DepartmentWorkflows
