import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import AgentConstellationInteractive from './AgentConstellationInteractive'
import { 
  FileText, DollarSign, Users, Shield, Database, BarChart3, 
  Bell, Calendar, Clock, CheckCircle, AlertCircle, TrendingUp,
  Home, Settings, ArrowUp, ArrowDown, Zap, Activity, Target,
  Filter, ChevronDown, Play, Plus, X, Maximize2
} from 'lucide-react'

const Dashboard = ({ reducedMotion = false }) => {
  const navigate = useNavigate()
  const [currentTime, setCurrentTime] = useState(new Date())
  const [selectedDepartment, setSelectedDepartment] = useState('all')
  const [activeTab, setActiveTab] = useState('overview')
  const [showFilters, setShowFilters] = useState(false)
  const [expandedSection, setExpandedSection] = useState(null)

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
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
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
    <div className="min-h-screen bg-gradient-to-br from-neutral-offWhite via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div 
          className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-gov-blue/15 to-professional-indigo/15 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div 
          className="absolute top-1/3 -left-40 w-80 h-80 bg-gradient-to-br from-professional-indigo/15 to-professional-teal/15 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />
        <motion.div 
          className="absolute bottom-20 right-1/4 w-72 h-72 bg-gradient-to-br from-accent-gold/10 to-gov-blue/15 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        />
      </div>

      {/* Animated grid pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03]">
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgb(59 130 246) 1px, transparent 0)',
            backgroundSize: '48px 48px'
          }}
        />
      </div>

      {/* Header */}
      <header className="backdrop-blur-xl bg-white/90 border-b border-gov-blue/20 shadow-lg sticky top-0 z-50">
        <div className="max-w-[1800px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center gap-4">
              <motion.button 
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-gov-blue to-professional-indigo text-white rounded-xl hover:from-gov-darkBlue hover:to-professional-indigo transition-all shadow-lg shadow-gov-blue/30"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Home size={18} />
                <span className="text-sm font-semibold">Home</span>
              </motion.button>
              
              <div className="h-10 w-px bg-gradient-to-b from-transparent via-gov-blue/30 to-transparent" />
              
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-gov-navy via-gov-blue to-professional-indigo bg-clip-text text-transparent">
                  City Governance Dashboard
                </h1>
                <p className="text-xs text-gray-600 mt-0.5 font-medium">
                  Multi-Agent Coordination System
                </p>
              </div>
            </div>
            
            {/* Right Section */}
            <div className="flex items-center gap-6">
              {/* Date & Time */}
              <div className="text-right bg-gradient-to-br from-blue-50 to-indigo-50 px-4 py-2 rounded-xl border border-gov-blue/30">
                <div className="text-sm font-bold bg-gradient-to-r from-gov-blue to-professional-indigo bg-clip-text text-transparent">
                  {formatTime(currentTime)}
                </div>
                <div className="text-xs text-gray-600 font-medium">{formatDate(currentTime)}</div>
              </div>
              
              <div className="h-10 w-px bg-gradient-to-b from-transparent via-gov-blue/30 to-transparent" />
              
              {/* Notifications */}
              <motion.button 
                className="relative p-3 bg-gradient-to-br from-accent-gold/20 to-accent-lightGold/30 text-accent-gold hover:from-accent-gold/30 hover:to-accent-lightGold/40 rounded-xl transition-all shadow-md"
                whileHover={{ scale: 1.1, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <Bell size={20} />
                <motion.span 
                  className="absolute -top-1 -right-1 px-2 py-0.5 bg-gradient-to-r from-accent-gold to-accent-bronze text-white text-xs font-bold rounded-full shadow-lg"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  5
                </motion.span>
              </motion.button>
              
              {/* Settings */}
              <motion.button 
                className="p-3 bg-gradient-to-br from-blue-100 to-indigo-100 text-gov-blue hover:from-blue-200 hover:to-indigo-200 rounded-xl transition-all shadow-md"
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <Settings size={20} />
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-[1800px] mx-auto px-6 py-8 space-y-8">
        {/* Quick Actions Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between gap-4 flex-wrap"
        >
          {/* Tab Navigation */}
          <div className="flex items-center gap-2 backdrop-blur-xl bg-white/90 rounded-2xl p-2 border border-gov-blue/30 shadow-lg">
            {['overview', 'analytics', 'operations'].map((tab) => (
              <motion.button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2.5 rounded-xl font-bold text-sm capitalize transition-all ${
                  activeTab === tab
                    ? 'bg-gradient-to-r from-gov-blue to-professional-indigo text-white shadow-lg'
                    : 'text-gray-600 hover:text-gov-navy hover:bg-gray-100'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {tab}
              </motion.button>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-gov-blue to-professional-indigo text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-shadow"
            >
              <Filter size={18} />
              Filters
              <ChevronDown size={16} className={`transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.05, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-professional-green to-professional-teal text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-shadow"
            >
              <Plus size={18} />
              New Request
            </motion.button>
          </div>
        </motion.div>

        {/* Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="backdrop-blur-xl bg-white/90 rounded-2xl border border-gov-blue/30 shadow-xl overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold bg-gradient-to-r from-gov-navy to-gov-blue bg-clip-text text-transparent">
                    Filter Dashboard
                  </h3>
                  <button onClick={() => setShowFilters(false)} className="text-gray-500 hover:text-gray-700">
                    <X size={20} />
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  {['all', ...departments.map(d => d.name.toLowerCase())].map((dept) => (
                    <motion.button
                      key={dept}
                      onClick={() => setSelectedDepartment(dept)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`px-4 py-2 rounded-xl font-bold text-sm capitalize transition-all ${
                        selectedDepartment === dept
                          ? 'bg-gradient-to-r from-gov-blue to-professional-indigo text-white shadow-lg'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {dept}
                    </motion.button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {kpis.map((kpi, index) => {
            const gradients = [
              'from-gov-blue via-professional-indigo to-professional-indigo',
              'from-professional-green via-professional-teal to-professional-teal',
              'from-accent-gold via-accent-bronze to-accent-bronze',
              'from-gov-blue via-professional-indigo to-professional-purple'
            ]
            const shadowColors = [
              'shadow-gov-blue/30',
              'shadow-professional-green/30',
              'shadow-accent-gold/30',
              'shadow-professional-indigo/30'
            ]
            
            return (
              <motion.div
                key={kpi.label}
                variants={fadeIn}
                initial="hidden"
                animate="visible"
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="group"
              >
                <div className={`relative backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-xl ${shadowColors[index]} hover:shadow-2xl transition-all overflow-hidden`}>
                  {/* Gradient overlay */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${gradients[index]} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  
                  {/* Top accent bar */}
                  <div className={`h-1.5 bg-gradient-to-r ${gradients[index]}`} />
                  
                  <div className="p-6 relative">
                    <div className="flex items-start justify-between mb-4">
                      <motion.div 
                        className={`p-3.5 rounded-2xl bg-gradient-to-br ${gradients[index]} shadow-lg`}
                        whileHover={{ rotate: 360, scale: 1.1 }}
                        transition={{ duration: 0.6 }}
                      >
                        <kpi.icon className="text-white" size={24} />
                      </motion.div>
                      <motion.div 
                        className={`flex items-center gap-1.5 text-sm font-bold px-3 py-1.5 rounded-full ${
                          kpi.change > 0 
                            ? 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border border-green-200' 
                            : 'bg-gradient-to-r from-red-100 to-rose-100 text-red-700 border border-red-200'
                        } shadow-md`}
                        whileHover={{ scale: 1.1 }}
                      >
                        {kpi.change > 0 ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                        {Math.abs(kpi.change)}%
                      </motion.div>
                    </div>
                    <div className="text-sm text-gray-600 font-semibold mb-2">{kpi.label}</div>
                    <div className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                      {kpi.value}
                    </div>
                    
                    {/* Mini sparkline effect */}
                    <div className="flex items-end gap-1 mt-4 h-8">
                      {[40, 55, 48, 62, 70, 65, 80].map((height, i) => (
                        <motion.div
                          key={i}
                          className={`flex-1 bg-gradient-to-t ${gradients[index]} rounded-t-full opacity-20 group-hover:opacity-40`}
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ duration: 0.5, delay: 0.1 + index * 0.1 + i * 0.05 }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Tab-based Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Main Content Grid - Asymmetric Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Column - Agent Network (8 cols) */}
                <motion.div
                  variants={fadeIn}
                  initial="hidden"
                  animate="visible"
                  transition={{ delay: 0.2 }}
                  className="lg:col-span-8 backdrop-blur-xl bg-white/90 rounded-2xl border border-white shadow-2xl shadow-gov-blue/20 overflow-hidden"
                >
                  {/* Top accent bar */}
                  <div className="h-1.5 bg-gradient-to-r from-gov-blue via-professional-indigo to-professional-teal" />
                  
                  <div className="p-6 border-b border-blue-100 bg-gradient-to-r from-blue-50/80 via-indigo-50/50 to-blue-50/30">
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="text-xl font-bold bg-gradient-to-r from-gov-navy via-gov-blue to-professional-indigo bg-clip-text text-transparent">
                          Agent Network
                        </h2>
                        <p className="text-sm text-gray-600 font-medium">Real-time coordination monitoring</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <motion.div 
                          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full shadow-lg shadow-green-500/30"
                          whileHover={{ scale: 1.05 }}
                          transition={{ duration: 0.2 }}
                        >
                          <motion.div 
                            className="w-2.5 h-2.5 bg-white rounded-full"
                            animate={{ scale: [1, 1.3, 1] }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                          />
                          <span className="text-sm font-bold text-white">All Agents Active</span>
                        </motion.div>
                        <motion.button
                          whileHover={{ scale: 1.1, rotate: 180 }}
                          className="p-2 bg-white/50 rounded-lg hover:bg-white transition-colors"
                        >
                          <Maximize2 size={18} className="text-indigo-600" />
                        </motion.button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Agent Constellation - Enhanced background */}
                  <div style={{ 
                    height: '600px', 
                    background: 'linear-gradient(135deg, #f8fafc 0%, #eef2ff 25%, #f5f3ff 50%, #fdf4ff 75%, #f8fafc 100%)'
                  }}>
                    <AgentConstellationInteractive reducedMotion={reducedMotion} />
                  </div>
                </motion.div>

                {/* Right Column - Activity Feed & Stats (4 cols) */}
                <div className="lg:col-span-4 space-y-6">
                  {/* Real-time Activity Feed */}
                  <motion.div
                    variants={fadeIn}
                    initial="hidden"
                    animate="visible"
                    transition={{ delay: 0.25 }}
                    className="backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-2xl shadow-blue-500/20 overflow-hidden"
                  >
                    {/* Top accent bar */}
                    <div className="h-1.5 bg-gradient-to-r from-gov-blue via-professional-indigo to-professional-teal" />
                    
                    <div className="p-6 border-b border-blue-100 bg-gradient-to-r from-blue-50/80 via-indigo-50/50 to-blue-50/30">
                      <div className="flex items-center justify-between">
                        <div>
                          <h2 className="text-lg font-bold bg-gradient-to-r from-gov-navy via-gov-blue to-professional-teal bg-clip-text text-transparent">
                            Live Activity
                          </h2>
                          <p className="text-xs text-gray-600 font-medium">Real-time system events</p>
                        </div>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                          <Activity size={20} className="text-gov-blue" />
                        </motion.div>
                      </div>
                    </div>
                    
                    <div className="p-5 space-y-3 max-h-[350px] overflow-y-auto">
                      {recentDecisions.slice(0, 5).map((decision, index) => (
                        <motion.div
                          key={decision.id}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.3 + index * 0.05 }}
                          whileHover={{ x: 4, scale: 1.02 }}
                          className="relative group cursor-pointer"
                        >
                          {/* Timeline dot and line */}
                          <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-300 via-indigo-400 to-blue-300 rounded-full" />
                          <motion.div 
                            className={`absolute left-[-3px] top-4 w-3 h-3 rounded-full ${
                              decision.status === 'Approved' ? 'bg-gradient-to-br from-green-400 to-emerald-600' :
                              decision.status === 'Pending' ? 'bg-gradient-to-br from-amber-400 to-orange-600' : 
                              'bg-gradient-to-br from-blue-400 to-cyan-600'
                            } ring-4 ring-white shadow-lg`}
                            whileHover={{ scale: 1.3 }}
                          />
                          
                          {/* Card content */}
                          <div className="ml-7 p-3 rounded-xl bg-gradient-to-br from-white via-blue-50/30 to-cyan-50/20 border border-blue-100 hover:border-cyan-300 hover:shadow-lg transition-all">
                            <div className="flex items-start justify-between mb-1.5">
                              <h3 className="text-xs font-bold text-gray-900 leading-tight group-hover:bg-gradient-to-r group-hover:from-gov-blue group-hover:to-professional-indigo group-hover:bg-clip-text group-hover:text-transparent transition-all">
                                {decision.title}
                              </h3>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] text-gray-600 font-medium">{decision.time}</span>
                              <motion.span 
                                className={`text-[10px] px-2 py-0.5 rounded-full font-bold shadow-sm ${
                                  decision.status === 'Approved' 
                                    ? 'bg-gradient-to-r from-green-100 to-green-100 text-green-700 border border-green-300' 
                                    : decision.status === 'Pending'
                                    ? 'bg-gradient-to-r from-yellow-100 to-yellow-100 text-yellow-700 border border-yellow-300'
                                    : 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border border-blue-300'
                                }`}
                                whileHover={{ scale: 1.1 }}
                              >
                                {decision.status}
                              </motion.span>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Quick Stats Card */}
                  <motion.div
                    variants={fadeIn}
                    initial="hidden"
                    animate="visible"
                    transition={{ delay: 0.3 }}
                    className="backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-2xl shadow-indigo-500/20 overflow-hidden"
                  >
                    <div className="h-1.5 bg-gradient-to-r from-gov-blue via-professional-indigo to-gov-blue" />
                    <div className="p-5">
                      <h3 className="text-sm font-bold bg-gradient-to-r from-gov-navy to-professional-indigo bg-clip-text text-transparent mb-4">
                        Quick Stats
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl">
                          <div className="flex items-center gap-2">
                            <Zap size={16} className="text-blue-600" />
                            <span className="text-xs font-bold text-gray-700">Pending</span>
                          </div>
                          <span className="text-lg font-bold text-blue-600">156</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                          <div className="flex items-center gap-2">
                            <Target size={16} className="text-green-600" />
                            <span className="text-xs font-bold text-gray-700">On Track</span>
                          </div>
                          <span className="text-lg font-bold text-green-600">2,691</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-gradient-to-r from-yellow-50 to-yellow-50 rounded-xl">
                          <div className="flex items-center gap-2">
                            <AlertCircle size={16} className="text-yellow-600" />
                            <span className="text-xs font-bold text-gray-700">Attention</span>
                          </div>
                          <span className="text-lg font-bold text-yellow-600">24</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-2xl p-12 text-center"
            >
              <BarChart3 size={64} className="mx-auto text-indigo-500 mb-4" />
              <h3 className="text-2xl font-bold bg-gradient-to-r from-gov-navy to-professional-indigo bg-clip-text text-transparent mb-2">
                Analytics View
              </h3>
              <p className="text-gray-600">Detailed analytics and reporting coming soon...</p>
            </motion.div>
          )}

          {activeTab === 'operations' && (
            <motion.div
              key="operations"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-2xl p-12 text-center"
            >
              <Settings size={64} className="mx-auto text-gov-blue mb-4" />
              <h3 className="text-2xl font-bold bg-gradient-to-r from-gov-navy to-professional-indigo bg-clip-text text-transparent mb-2">
                Operations View
              </h3>
              <p className="text-gray-600">Operational controls and management coming soon...</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Department Performance & System Health - Only show in overview */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Department Performance */}
            <motion.div
              variants={fadeIn}
              initial="hidden"
              animate="visible"
              transition={{ delay: 0.3 }}
              className="backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-2xl shadow-indigo-500/20"
            >
              {/* Top accent bar */}
              <div className="h-1.5 bg-gradient-to-r from-gov-blue via-professional-indigo to-professional-teal" />
            
            <div className="p-6 border-b border-indigo-100 bg-gradient-to-r from-indigo-50/80 via-blue-50/50 to-indigo-50/30">
              <h2 className="text-xl font-bold bg-gradient-to-r from-gov-navy via-gov-blue to-professional-indigo bg-clip-text text-transparent">
                Department Performance
              </h2>
              <p className="text-sm text-gray-600 font-medium">Request resolution metrics</p>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-2 gap-5">
                {departments.map((dept, index) => {
                  const percentage = Math.round((dept.resolved / dept.requests) * 100)
                  const circumference = 2 * Math.PI * 36
                  const strokeDashoffset = circumference - (percentage / 100) * circumference
                  
                  const deptGradients = {
                    'Health': { from: '#10b981', to: '#14b8a6' }, // green to teal
                    'Water': { from: '#3b82f6', to: '#6366f1' }, // blue to indigo
                    'Sanitation': { from: '#10b981', to: '#14b8a6' }, // green to teal
                    'Fire': { from: '#3b82f6', to: '#6366f1' }, // blue to indigo
                    'Engineering': { from: '#6366f1', to: '#3b82f6' }, // indigo to blue
                    'Finance': { from: '#d4af37', to: '#d4af37' } // gold
                  }
                  
                  const gradient = deptGradients[dept.name] || { from: '#6366f1', to: '#8b5cf6' }
                  
                  return (
                    <motion.div
                      key={dept.name}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.35 + index * 0.05 }}
                      whileHover={{ scale: 1.05, y: -4 }}
                      className="relative p-5 rounded-2xl bg-gradient-to-br from-white via-indigo-50/30 to-blue-50/30 border border-indigo-100 hover:border-blue-300 hover:shadow-xl hover:shadow-gov-blue/20 transition-all group cursor-pointer"
                    >
                      <div className="flex items-center gap-4">
                        {/* Circular Progress */}
                        <div className="relative flex-shrink-0">
                          <svg className="transform -rotate-90" width="80" height="80">
                            {/* Background circle with gradient */}
                            <circle
                              cx="40"
                              cy="40"
                              r="36"
                              stroke="rgb(226 232 240)"
                              strokeWidth="7"
                              fill="none"
                            />
                            {/* Progress circle */}
                            <motion.circle
                              cx="40"
                              cy="40"
                              r="36"
                              stroke="url(#gradient-${dept.name})"
                              strokeWidth="7"
                              fill="none"
                              strokeLinecap="round"
                              initial={{ strokeDashoffset: circumference }}
                              animate={{ strokeDashoffset }}
                              transition={{ duration: 1, delay: 0.4 + index * 0.05, ease: "easeOut" }}
                              style={{
                                strokeDasharray: circumference,
                                filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                              }}
                            />
                            <defs>
                              <linearGradient id={`gradient-${dept.name}`} x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor={gradient.from} />
                                <stop offset="100%" stopColor={gradient.to} />
                              </linearGradient>
                            </defs>
                          </svg>
                          
                          {/* Center percentage */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                              {percentage}%
                            </span>
                          </div>
                        </div>
                        
                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-bold text-gray-900 mb-2.5 group-hover:bg-gradient-to-r group-hover:from-gov-blue group-hover:to-professional-indigo group-hover:bg-clip-text group-hover:text-transparent transition-all">
                            {dept.name}
                          </h3>
                          <div className="space-y-2 text-xs">
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600 font-medium">Resolved</span>
                              <motion.span 
                                className="font-bold text-green-600 px-2 py-0.5 bg-green-50 rounded-full border border-green-200"
                                whileHover={{ scale: 1.1 }}
                              >
                                {dept.resolved}
                              </motion.span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600 font-medium">Pending</span>
                              <motion.span 
                                className="font-bold text-amber-600 px-2 py-0.5 bg-amber-50 rounded-full border border-amber-200"
                                whileHover={{ scale: 1.1 }}
                              >
                                {dept.pending}
                              </motion.span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-600 font-medium">Total</span>
                              <motion.span 
                                className="font-bold text-gray-900 px-2 py-0.5 bg-gray-50 rounded-full border border-gray-200"
                                whileHover={{ scale: 1.1 }}
                              >
                                {dept.requests}
                              </motion.span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Status indicator with gradient */}
                      <motion.div 
                        className={`absolute top-4 right-4 w-2.5 h-2.5 rounded-full shadow-lg`}
                        style={{
                          background: `linear-gradient(135deg, ${gradient.from}, ${gradient.to})`
                        }}
                        animate={{ scale: [1, 1.3, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
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
            className="backdrop-blur-xl bg-white/80 rounded-2xl border border-white shadow-2xl shadow-green-500/20"
          >
            {/* Top accent bar */}
            <div className="h-1.5 bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500" />
            
            <div className="p-6 border-b border-green-100 bg-gradient-to-r from-green-50/80 via-emerald-50/50 to-teal-50/30">
              <h2 className="text-xl font-bold bg-gradient-to-r from-green-700 via-emerald-700 to-teal-700 bg-clip-text text-transparent">
                System Health
              </h2>
              <p className="text-sm text-gray-600 font-medium">Infrastructure status</p>
            </div>
            
            <div className="p-6 space-y-4">
              {systemMetrics.map((metric, index) => {
                const radius = 24
                const circumference = 2 * Math.PI * radius
                const strokeDashoffset = circumference - (metric.value / 100) * circumference
                
                const getGradient = (value) => {
                  if (value >= 95) return { from: '#10b981', to: '#14b8a6', bg: 'from-professional-green to-professional-teal' }
                  if (value >= 85) return { from: '#3b82f6', to: '#6366f1', bg: 'from-gov-blue to-professional-indigo' }
                  return { from: '#d4af37', to: '#cd7f32', bg: 'from-accent-gold to-accent-bronze' }
                }
                
                const gradient = getGradient(metric.value)
                
                return (
                  <motion.div
                    key={metric.label}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    whileHover={{ x: 4, scale: 1.02 }}
                    className="relative p-5 rounded-2xl bg-gradient-to-r from-white via-green-50/30 to-emerald-50/20 border border-green-100 hover:border-emerald-300 hover:shadow-xl hover:shadow-emerald-500/20 transition-all group cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      {/* Circular indicator */}
                      <div className="relative flex-shrink-0">
                        <svg className="transform -rotate-90" width="60" height="60">
                          {/* Background circle */}
                          <circle
                            cx="30"
                            cy="30"
                            r={radius}
                            stroke="rgb(226 232 240)"
                            strokeWidth="5"
                            fill="none"
                          />
                          {/* Progress circle */}
                          <motion.circle
                            cx="30"
                            cy="30"
                            r={radius}
                            stroke={`url(#system-gradient-${index})`}
                            strokeWidth="5"
                            fill="none"
                            strokeLinecap="round"
                            initial={{ strokeDashoffset: circumference }}
                            animate={{ strokeDashoffset }}
                            transition={{ duration: 1, delay: 0.45 + index * 0.05, ease: "easeOut" }}
                            style={{
                              strokeDasharray: circumference,
                              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                            }}
                          />
                          <defs>
                            <linearGradient id={`system-gradient-${index}`} x1="0%" y1="0%" x2="100%" y2="100%">
                              <stop offset="0%" stopColor={gradient.from} />
                              <stop offset="100%" stopColor={gradient.to} />
                            </linearGradient>
                          </defs>
                        </svg>
                        
                        {/* Center icon */}
                        <motion.div 
                          className="absolute inset-0 flex items-center justify-center"
                          whileHover={{ rotate: 360 }}
                          transition={{ duration: 0.6 }}
                        >
                          <div className={`p-2 rounded-full bg-gradient-to-br ${gradient.bg} shadow-lg`}>
                            <Database size={18} className="text-white" />
                          </div>
                        </motion.div>
                      </div>
                      
                      {/* Info */}
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-bold text-gray-900 group-hover:bg-gradient-to-r group-hover:from-green-600 group-hover:to-emerald-600 group-hover:bg-clip-text group-hover:text-transparent transition-all">
                            {metric.label}
                          </span>
                          <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                            {metric.value}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <motion.span 
                            className={`text-xs font-bold px-3 py-1 rounded-full shadow-md border ${
                              metric.value >= 95 ? 'bg-gradient-to-r from-green-100 to-green-100 text-green-700 border-green-300' :
                              metric.value >= 85 ? 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 border-blue-300' : 
                              'bg-gradient-to-r from-yellow-100 to-yellow-100 text-yellow-700 border-yellow-300'
                            }`}
                            whileHover={{ scale: 1.1 }}
                          >
                            {metric.status}
                          </motion.span>
                          
                          {/* Mini chart/sparkline */}
                          <div className="flex items-end gap-1 h-5">
                            {[65, 72, 68, 75, 80, 85, metric.value].map((val, i) => (
                              <motion.div
                                key={i}
                                className={`rounded-t-full ${
                                  metric.value >= 95 ? 'bg-gradient-to-t from-professional-green to-professional-teal' : 
                                  metric.value >= 85 ? 'bg-gradient-to-t from-gov-blue to-professional-indigo' : 
                                  'bg-gradient-to-t from-accent-gold to-accent-bronze'
                                }`}
                                initial={{ height: 0 }}
                                animate={{ height: `${(val / 100) * 100}%` }}
                                transition={{ duration: 0.5, delay: 0.5 + index * 0.05 + i * 0.05 }}
                                style={{ width: '3px' }}
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
              <div className="mt-6 pt-5 border-t-2 border-gradient-to-r from-green-200 via-emerald-200 to-teal-200">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  whileHover={{ scale: 1.02, y: -2 }}
                  className="relative p-6 rounded-2xl bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 border-2 border-emerald-200 shadow-xl shadow-emerald-500/20 cursor-pointer overflow-hidden"
                >
                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-teal-500/5" />
                  
                  <div className="flex items-center gap-5 relative">
                    {/* Large circular progress */}
                    <div className="relative flex-shrink-0">
                      <svg className="transform -rotate-90" width="90" height="90">
                        <circle
                          cx="45"
                          cy="45"
                          r="38"
                          stroke="rgb(209 250 229)"
                          strokeWidth="7"
                          fill="none"
                        />
                        <motion.circle
                          cx="45"
                          cy="45"
                          r="38"
                          stroke="url(#gradient-budget)"
                          strokeWidth="7"
                          fill="none"
                          strokeLinecap="round"
                          initial={{ strokeDashoffset: 2 * Math.PI * 38 }}
                          animate={{ strokeDashoffset: 2 * Math.PI * 38 - (91.7 / 100) * 2 * Math.PI * 38 }}
                          transition={{ duration: 1.2, delay: 0.65, ease: "easeOut" }}
                          style={{
                            strokeDasharray: 2 * Math.PI * 38,
                            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                          }}
                        />
                        <defs>
                          <linearGradient id="gradient-budget" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#10b981" />
                            <stop offset="50%" stopColor="#059669" />
                            <stop offset="100%" stopColor="#14b8a6" />
                          </linearGradient>
                        </defs>
                      </svg>
                      
                      <motion.div 
                        className="absolute inset-0 flex items-center justify-center"
                        whileHover={{ rotate: [0, -10, 10, -10, 0] }}
                        transition={{ duration: 0.5 }}
                      >
                        <div className="p-3 rounded-full bg-gradient-to-br from-professional-green to-professional-teal shadow-lg">
                          <DollarSign size={28} className="text-white" strokeWidth={2.5} />
                        </div>
                      </motion.div>
                    </div>
                    
                    {/* Budget info */}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-base font-bold bg-gradient-to-r from-gov-navy to-gov-blue bg-clip-text text-transparent">
                          Budget Utilization
                        </span>
                        <span className="text-3xl font-bold bg-gradient-to-r from-professional-green to-professional-teal bg-clip-text text-transparent">
                          91.7%
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 font-medium mb-3">
                        Across all departments (FY 2026)
                      </p>
                      
                      {/* Department budget mini-indicators */}
                      <div className="flex items-center gap-1.5">
                        {departments.map((dept, idx) => {
                          const deptColors = [
                            'from-professional-green to-professional-teal',
                            'from-gov-blue to-professional-indigo',
                            'from-professional-teal to-professional-green',
                            'from-gov-blue to-professional-indigo',
                            'from-professional-indigo to-gov-blue',
                            'from-accent-gold to-accent-bronze'
                          ]
                          return (
                            <motion.div
                              key={dept.name}
                              className="relative group/dept"
                              style={{ flex: dept.budget }}
                              whileHover={{ scale: 1.05 }}
                            >
                              <motion.div 
                                className={`h-2 bg-gradient-to-r ${deptColors[idx]} rounded-full shadow-md`}
                                initial={{ scaleX: 0 }}
                                animate={{ scaleX: 1 }}
                                transition={{ duration: 0.6, delay: 0.7 + idx * 0.05 }}
                                title={`${dept.name}: ${dept.budget}%`}
                              />
                              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover/dept:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                                {dept.name}: {dept.budget}%
                              </div>
                            </motion.div>
                          )
                        })}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
