import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import AgentConstellationInteractive from './AgentConstellationInteractive'
import { 
  FileText, DollarSign, Users, Shield, Database, BarChart3, 
  Bell, Calendar, Clock, CheckCircle, AlertCircle, TrendingUp,
  Home, Settings, ArrowUp, ArrowDown
} from 'lucide-react'

const DashboardOfficial = ({ reducedMotion = false }) => {
  const navigate = useNavigate()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [selectedDepartment, setSelectedDepartment] = useState('all')

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Subtle fade in animation
  const fadeIn = {
    hidden: { opacity: 0, y: 10 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.4, ease: 'easeOut' }
    }
  }

  // Key Performance Indicators
  const kpis = [
    { 
      label: 'Active Requests', 
      value: '2,847', 
      change: +12.5,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    { 
      label: 'Resolved Today', 
      value: '1,234', 
      change: +8.3,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    { 
      label: 'Avg Response Time', 
      value: '1.2 hrs', 
      change: -15.2,
      icon: Clock,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50'
    },
    { 
      label: 'Compliance Rate', 
      value: '98.4%', 
      change: +2.1,
      icon: Shield,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50'
    },
  ]

  // Department Statistics
  const departments = [
    { name: 'Water', requests: 487, resolved: 452, pending: 35, budget: 92 },
    { name: 'Fire', requests: 256, resolved: 241, pending: 15, budget: 88 },
    { name: 'Health', requests: 623, resolved: 587, pending: 36, budget: 94 },
    { name: 'Engineering', requests: 834, resolved: 789, pending: 45, budget: 91 },
    { name: 'Finance', requests: 412, resolved: 398, pending: 14, budget: 96 },
    { name: 'Sanitation', requests: 235, resolved: 224, pending: 11, budget: 89 },
  ]

  // Recent Decisions/Approvals
  const recentDecisions = [
    { id: 1, title: 'Water Pipeline Repair - Zone 4', department: 'Water', status: 'Approved', time: '10 min ago', priority: 'High' },
    { id: 2, title: 'Health Inspection Schedule', department: 'Health', status: 'Approved', time: '1 hr ago', priority: 'Medium' },
    { id: 3, title: 'Budget Reallocation Q1', department: 'Finance', status: 'Pending', time: '2 hrs ago', priority: 'High' },
    { id: 4, title: 'Fire Safety Drill Plan', department: 'Fire', status: 'Approved', time: '3 hrs ago', priority: 'Low' },
    { id: 5, title: 'Road Maintenance Request', department: 'Engineering', status: 'Under Review', time: '4 hrs ago', priority: 'Medium' },
  ]

  // System Health Metrics
  const systemMetrics = [
    { label: 'Database', value: 98, status: 'Operational', color: 'bg-green-500' },
    { label: 'API Services', value: 100, status: 'Operational', color: 'bg-green-500' },
    { label: 'Agent Network', value: 96, status: 'Operational', color: 'bg-green-500' },
    { label: 'Processing Queue', value: 87, status: 'Normal', color: 'bg-blue-500' },
  ]

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    })
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center gap-4">
              <motion.button 
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Home size={18} />
                <span className="text-sm font-medium">Home</span>
              </motion.button>
              
              <div className="h-8 w-px bg-gray-300" />
              
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  City Governance Dashboard
                </h1>
                <p className="text-xs text-gray-600 mt-0.5">
                  Multi-Agent Coordination System
                </p>
              </div>
            </div>
            
            {/* Right Section */}
            <div className="flex items-center gap-6">
              {/* Date & Time */}
              <div className="text-right">
                <div className="text-sm font-semibold text-gray-900">{formatTime(currentTime)}</div>
                <div className="text-xs text-gray-600">{formatDate(currentTime)}</div>
              </div>
              
              <div className="h-8 w-px bg-gray-300" />
              
              {/* Notifications */}
              <motion.button 
                className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </motion.button>
              
              {/* Settings */}
              <motion.button 
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Settings size={20} />
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-[1800px] mx-auto px-6 py-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpis.map((kpi, index) => (
            <motion.div
              key={kpi.label}
              variants={fadeIn}
              initial="hidden"
              animate="visible"
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2.5 rounded-lg ${kpi.bgColor}`}>
                    <kpi.icon className={`${kpi.color}`} size={20} />
                  </div>
                  <div className={`flex items-center gap-1 text-xs font-semibold ${
                    kpi.change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {kpi.change > 0 ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                    {Math.abs(kpi.change)}%
                  </div>
                </div>
                <div className="text-xs text-gray-600 font-medium mb-1">{kpi.label}</div>
                <div className="text-2xl font-bold text-gray-900">{kpi.value}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent Network - Spans 2 columns */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Agent Network</h2>
                  <p className="text-sm text-gray-600">Real-time coordination monitoring</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs font-semibold text-green-700">All Agents Active</span>
                </div>
              </div>
            </div>
            
            {/* Agent Constellation - Keep animation exactly as is */}
            <div style={{ height: '600px', background: 'linear-gradient(to bottom, #f8fafc, #f1f5f9)' }}>
              <AgentConstellationInteractive reducedMotion={reducedMotion} />
            </div>
          </motion.div>

          {/* Recent Decisions */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.25 }}
            className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
              <h2 className="text-lg font-bold text-gray-900">Recent Decisions</h2>
              <p className="text-sm text-gray-600">Latest approvals & reviews</p>
            </div>
            
            <div className="divide-y divide-gray-100">
              {recentDecisions.map((decision, index) => (
                <motion.div
                  key={decision.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-gray-900 mb-1">{decision.title}</h3>
                      <div className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="font-medium">{decision.department}</span>
                        <span>•</span>
                        <span>{decision.time}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      decision.status === 'Approved' 
                        ? 'bg-green-100 text-green-700 border border-green-200' 
                        : decision.status === 'Pending'
                        ? 'bg-amber-100 text-amber-700 border border-amber-200'
                        : 'bg-blue-100 text-blue-700 border border-blue-200'
                    }`}>
                      {decision.status}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      decision.priority === 'High' 
                        ? 'bg-red-100 text-red-700 border border-red-200' 
                        : decision.priority === 'Medium'
                        ? 'bg-orange-100 text-orange-700 border border-orange-200'
                        : 'bg-gray-100 text-gray-700 border border-gray-200'
                    }`}>
                      {decision.priority}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Department Performance & System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Department Performance */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg border border-gray-200 shadow-sm"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
              <h2 className="text-lg font-bold text-gray-900">Department Performance</h2>
              <p className="text-sm text-gray-600">Request resolution metrics</p>
            </div>
            
            <div className="p-5 space-y-4">
              {departments.map((dept, index) => (
                <motion.div
                  key={dept.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35 + index * 0.05 }}
                  className="space-y-2"
                >
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-gray-900">{dept.name}</span>
                    <div className="flex items-center gap-3 text-xs text-gray-600">
                      <span>{dept.resolved}/{dept.requests} resolved</span>
                      <span className="text-amber-600 font-medium">{dept.pending} pending</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                        initial={{ width: 0 }}
                        animate={{ width: `${(dept.resolved / dept.requests) * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.4 + index * 0.05 }}
                      />
                    </div>
                    <span className="text-xs font-semibold text-gray-700 min-w-[45px]">
                      {Math.round((dept.resolved / dept.requests) * 100)}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* System Health */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.35 }}
            className="bg-white rounded-lg border border-gray-200 shadow-sm"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
              <h2 className="text-lg font-bold text-gray-900">System Health</h2>
              <p className="text-sm text-gray-600">Infrastructure status</p>
            </div>
            
            <div className="p-5 space-y-5">
              {systemMetrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.05 }}
                  className="space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Database size={16} className="text-gray-600" />
                      <span className="text-sm font-semibold text-gray-900">{metric.label}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-600">{metric.status}</span>
                      <span className="text-sm font-bold text-gray-900">{metric.value}%</span>
                    </div>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full ${metric.color}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${metric.value}%` }}
                      transition={{ duration: 0.8, delay: 0.45 + index * 0.05 }}
                    />
                  </div>
                </motion.div>
              ))}
              
              {/* Budget Utilization Summary */}
              <div className="mt-6 pt-5 border-t border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <DollarSign size={16} className="text-gray-600" />
                    <span className="text-sm font-semibold text-gray-900">Budget Utilization</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">91.7%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-emerald-500 to-green-600"
                    initial={{ width: 0 }}
                    animate={{ width: '91.7%' }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                  />
                </div>
                <p className="text-xs text-gray-600 mt-2">Across all departments (FY 2026)</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default DashboardOfficial
