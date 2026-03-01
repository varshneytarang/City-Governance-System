import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import AgentConstellationInteractive from './AgentConstellationInteractive'
import { 
  FileText, DollarSign, Users, Shield, Database, BarChart3, 
  Bell, Calendar, Clock, CheckCircle, AlertCircle, TrendingUp,
  Home, Settings, ArrowUp, ArrowDown
} from 'lucide-react'

const Dashboard = ({ reducedMotion = false }) => {
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-100 relative">
      {/* Subtle decorative elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-40">
        <div className="absolute top-20 right-20 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-80 h-80 bg-indigo-200/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 w-72 h-72 bg-slate-200/20 rounded-full blur-3xl" />
      </div>

      {/* Subtle grid pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02]">
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgb(148 163 184) 1px, transparent 0)',
            backgroundSize: '48px 48px'
          }}
        />
      </div>

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm sticky top-0 z-50 relative">
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative">
          {kpis.map((kpi, index) => (
            <motion.div
              key={kpi.label}
              variants={fadeIn}
              initial="hidden"
              animate="visible"
              transition={{ delay: index * 0.05 }}
              className="bg-white/90 backdrop-blur-sm rounded-lg border border-gray-200 shadow-sm hover:shadow-lg hover:border-blue-200 transition-all"
            >
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2.5 rounded-lg ${kpi.bgColor} ring-2 ring-white shadow-sm`}>
                    <kpi.icon className={`${kpi.color}`} size={20} />
                  </div>
                  <div className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${
                    kpi.change > 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                  }`}>
                    {kpi.change > 0 ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                    {Math.abs(kpi.change)}%
                  </div>
                </div>
                <div className="text-xs text-gray-600 font-medium mb-1">{kpi.label}</div>
                <div className="text-2xl font-bold text-gray-900">{kpi.value}</div>
              </div>
              
              {/* Subtle accent line */}
              <div className={`h-1 ${kpi.bgColor}`} />
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
            className="lg:col-span-2 bg-white/90 backdrop-blur-sm rounded-lg border border-gray-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-purple-50/50 to-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Agent Network</h2>
                  <p className="text-sm text-gray-600">Real-time coordination monitoring</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full shadow-sm">
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
            className="bg-white/90 backdrop-blur-sm rounded-lg border border-gray-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-blue-50/50 to-white">
              <h2 className="text-lg font-bold text-gray-900">Recent Decisions</h2>
              <p className="text-sm text-gray-600">Latest approvals & reviews</p>
            </div>
            
            <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
              {recentDecisions.map((decision, index) => (
                <motion.div
                  key={decision.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="relative group"
                >
                  {/* Timeline dot and line */}
                  <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-200 via-blue-300 to-blue-200" />
                  <div className={`absolute left-[-3px] top-6 w-2.5 h-2.5 rounded-full ${
                    decision.status === 'Approved' ? 'bg-green-500' :
                    decision.status === 'Pending' ? 'bg-amber-500' : 'bg-blue-500'
                  } ring-4 ring-white`} />
                  
                  {/* Card content */}
                  <div className="ml-6 p-4 rounded-lg bg-gradient-to-br from-white to-slate-50 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all cursor-pointer">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                          {decision.title}
                        </h3>
                        <div className="flex items-center gap-2 text-xs text-gray-600">
                          <span className="font-medium">{decision.department}</span>
                          <span>•</span>
                          <span>{decision.time}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          decision.status === 'Approved' 
                            ? 'bg-green-100 text-green-700 border border-green-200' 
                            : decision.status === 'Pending'
                            ? 'bg-amber-100 text-amber-700 border border-amber-200'
                            : 'bg-blue-100 text-blue-700 border border-blue-200'
                        }`}>
                          {decision.status}
                        </span>
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          decision.priority === 'High' 
                            ? 'bg-red-100 text-red-700 border border-red-200' 
                            : decision.priority === 'Medium'
                            ? 'bg-orange-100 text-orange-700 border border-orange-200'
                            : 'bg-gray-100 text-gray-700 border border-gray-200'
                        }`}>
                          {decision.priority}
                        </span>
                      </div>
                      
                      {/* Visual indicator */}
                      <div className="flex items-center gap-1">
                        {[...Array(decision.priority === 'High' ? 3 : decision.priority === 'Medium' ? 2 : 1)].map((_, i) => (
                          <div key={i} className={`w-1 h-4 rounded-full ${
                            decision.priority === 'High' ? 'bg-red-400' :
                            decision.priority === 'Medium' ? 'bg-orange-400' : 'bg-gray-400'
                          }`} />
                        ))}
                      </div>
                    </div>
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
            className="bg-white/90 backdrop-blur-sm rounded-lg border border-gray-200 shadow-sm"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-indigo-50/50 to-white">
              <h2 className="text-lg font-bold text-gray-900">Department Performance</h2>
              <p className="text-sm text-gray-600">Request resolution metrics</p>
            </div>
            
            <div className="p-5">
              <div className="grid grid-cols-2 gap-4">
                {departments.map((dept, index) => {
                  const percentage = Math.round((dept.resolved / dept.requests) * 100)
                  const circumference = 2 * Math.PI * 36
                  const strokeDashoffset = circumference - (percentage / 100) * circumference
                  
                  return (
                    <motion.div
                      key={dept.name}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.35 + index * 0.05 }}
                      className="relative p-4 rounded-xl bg-gradient-to-br from-white to-slate-50 border border-gray-100 hover:border-indigo-200 hover:shadow-md transition-all group"
                    >
                      <div className="flex items-center gap-4">
                        {/* Circular Progress */}
                        <div className="relative flex-shrink-0">
                          <svg className="transform -rotate-90" width="80" height="80">
                            {/* Background circle */}
                            <circle
                              cx="40"
                              cy="40"
                              r="36"
                              stroke="rgb(226 232 240)"
                              strokeWidth="6"
                              fill="none"
                            />
                            {/* Progress circle */}
                            <motion.circle
                              cx="40"
                              cy="40"
                              r="36"
                              stroke="url(#gradient-${dept.name})"
                              strokeWidth="6"
                              fill="none"
                              strokeLinecap="round"
                              initial={{ strokeDashoffset: circumference }}
                              animate={{ strokeDashoffset }}
                              transition={{ duration: 1, delay: 0.4 + index * 0.05, ease: "easeOut" }}
                              style={{
                                strokeDasharray: circumference,
                              }}
                            />
                            <defs>
                              <linearGradient id={`gradient-${dept.name}`} x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor={
                                  percentage >= 95 ? '#10b981' : 
                                  percentage >= 90 ? '#3b82f6' : '#f59e0b'
                                } />
                                <stop offset="100%" stopColor={
                                  percentage >= 95 ? '#059669' : 
                                  percentage >= 90 ? '#2563eb' : '#d97706'
                                } />
                              </linearGradient>
                            </defs>
                          </svg>
                          
                          {/* Center percentage */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-lg font-bold text-gray-900">{percentage}%</span>
                          </div>
                        </div>
                        
                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
                            {dept.name}
                          </h3>
                          <div className="space-y-1.5 text-xs">
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600">Resolved</span>
                              <span className="font-semibold text-green-600">{dept.resolved}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600">Pending</span>
                              <span className="font-semibold text-amber-600">{dept.pending}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600">Total</span>
                              <span className="font-semibold text-gray-900">{dept.requests}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Status indicator */}
                      <div className={`absolute top-3 right-3 w-2 h-2 rounded-full ${
                        percentage >= 95 ? 'bg-green-500' :
                        percentage >= 90 ? 'bg-blue-500' : 'bg-amber-500'
                      } animate-pulse`} />
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </motion.div>

          {/* System Health */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.35 }}
            className="bg-white/90 backdrop-blur-sm rounded-lg border border-gray-200 shadow-sm"
          >
            <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-green-50/50 to-white">
              <h2 className="text-lg font-bold text-gray-900">System Health</h2>
              <p className="text-sm text-gray-600">Infrastructure status</p>
            </div>
            
            <div className="p-5 space-y-3">
              {systemMetrics.map((metric, index) => {
                const radius = 24
                const circumference = 2 * Math.PI * radius
                const strokeDashoffset = circumference - (metric.value / 100) * circumference
                
                return (
                  <motion.div
                    key={metric.label}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className="relative p-4 rounded-xl bg-gradient-to-r from-white to-slate-50 border border-gray-100 hover:border-green-200 hover:shadow-md transition-all group"
                  >
                    <div className="flex items-center gap-4">
                      {/* Circular indicator */}
                      <div className="relative flex-shrink-0">
                        <svg className="transform -rotate-90" width="56" height="56">
                          {/* Background circle */}
                          <circle
                            cx="28"
                            cy="28"
                            r={radius}
                            stroke="rgb(226 232 240)"
                            strokeWidth="4"
                            fill="none"
                          />
                          {/* Progress circle */}
                          <motion.circle
                            cx="28"
                            cy="28"
                            r={radius}
                            stroke={metric.value >= 95 ? '#10b981' : metric.value >= 85 ? '#3b82f6' : '#f59e0b'}
                            strokeWidth="4"
                            fill="none"
                            strokeLinecap="round"
                            initial={{ strokeDashoffset: circumference }}
                            animate={{ strokeDashoffset }}
                            transition={{ duration: 1, delay: 0.45 + index * 0.05, ease: "easeOut" }}
                            style={{
                              strokeDasharray: circumference,
                            }}
                          />
                        </svg>
                        
                        {/* Center icon */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Database size={20} className={
                            metric.value >= 95 ? 'text-green-500' : 
                            metric.value >= 85 ? 'text-blue-500' : 'text-amber-500'
                          } />
                        </div>
                      </div>
                      
                      {/* Info */}
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-semibold text-gray-900">{metric.label}</span>
                          <span className="text-lg font-bold text-gray-900">{metric.value}%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                            metric.value >= 95 ? 'bg-green-100 text-green-700' :
                            metric.value >= 85 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'
                          }`}>
                            {metric.status}
                          </span>
                          
                          {/* Mini chart/sparkline */}
                          <div className="flex items-end gap-0.5 h-5">
                            {[65, 72, 68, 75, 80, 85, metric.value].map((val, i) => (
                              <motion.div
                                key={i}
                                className={metric.value >= 95 ? 'bg-green-400' : metric.value >= 85 ? 'bg-blue-400' : 'bg-amber-400'}
                                initial={{ height: 0 }}
                                animate={{ height: `${(val / 100) * 100}%` }}
                                transition={{ duration: 0.5, delay: 0.5 + index * 0.05 + i * 0.05 }}
                                style={{ width: '3px', borderRadius: '2px' }}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
              
              {/* Budget Utilization Summary */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="relative p-4 rounded-xl bg-gradient-to-br from-emerald-50 to-white border border-emerald-100"
                >
                  <div className="flex items-center gap-4">
                    {/* Large circular progress */}
                    <div className="relative flex-shrink-0">
                      <svg className="transform -rotate-90" width="80" height="80">
                        <circle
                          cx="40"
                          cy="40"
                          r="36"
                          stroke="rgb(209 250 229)"
                          strokeWidth="6"
                          fill="none"
                        />
                        <motion.circle
                          cx="40"
                          cy="40"
                          r="36"
                          stroke="url(#gradient-budget)"
                          strokeWidth="6"
                          fill="none"
                          strokeLinecap="round"
                          initial={{ strokeDashoffset: 2 * Math.PI * 36 }}
                          animate={{ strokeDashoffset: 2 * Math.PI * 36 - (91.7 / 100) * 2 * Math.PI * 36 }}
                          transition={{ duration: 1.2, delay: 0.65, ease: "easeOut" }}
                          style={{
                            strokeDasharray: 2 * Math.PI * 36,
                          }}
                        />
                        <defs>
                          <linearGradient id="gradient-budget" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#10b981" />
                            <stop offset="100%" stopColor="#059669" />
                          </linearGradient>
                        </defs>
                      </svg>
                      
                      <div className="absolute inset-0 flex items-center justify-center">
                        <DollarSign size={28} className="text-emerald-600" />
                      </div>
                    </div>
                    
                    {/* Budget info */}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-bold text-gray-900">Budget Utilization</span>
                        <span className="text-2xl font-bold text-emerald-600">91.7%</span>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">Across all departments (FY 2026)</p>
                      
                      {/* Department budget mini-indicators */}
                      <div className="flex items-center gap-1">
                        {departments.map((dept) => (
                          <div
                            key={dept.name}
                            className="relative group/dept"
                            style={{ flex: dept.budget }}
                          >
                            <div 
                              className="h-1.5 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full transition-all group-hover/dept:h-2"
                              title={`${dept.name}: ${dept.budget}%`}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
