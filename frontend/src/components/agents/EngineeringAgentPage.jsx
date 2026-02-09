import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Wrench, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home, MessageSquare,
  Users, HardHat, AlertCircle, Phone, Building, Hammer, Ruler,
  TrendingDown, Truck, Award, Timer, Target, Construction, Lightbulb, Cog
} from 'lucide-react'
import AgentChatBot from './AgentChatBot'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const EngineeringAgentPage = () => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [chatHistory, setChatHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [selectedProject, setSelectedProject] = useState(null)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])
  
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/agents/engineering/history?limit=10`)
        if (response.ok) {
          const data = await response.json()
          setChatHistory(data.history || [])
        }
      } catch (error) {
        console.error('Failed to fetch chat history:', error)
      } finally {
        setLoadingHistory(false)
      }
    }
    
    fetchHistory()
    const interval = setInterval(fetchHistory, 30000)
    return () => clearInterval(interval)
  }, [])
  
  const getRelativeTime = (timestamp) => {
    const now = new Date()
    const past = new Date(timestamp)
    const diffMs = now - past
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  }

  const kpiMetrics = [
    { 
      label: 'Active Projects', 
      value: '18', 
      trend: '+3',
      trendUp: true,
      icon: Construction,
      color: '#0891b2',
      sparkline: [14, 15, 15, 16, 17, 17, 18],
      subtitle: 'Under construction'
    },
    { 
      label: 'Completion Rate', 
      value: '87%', 
      trend: '+5%',
      trendUp: true,
      icon: CheckCircle,
      color: '#10b981',
      sparkline: [79, 81, 83, 84, 85, 86, 87],
      subtitle: 'On-time delivery'
    },
    { 
      label: 'Safety Score', 
      value: '98', 
      target: 100,
      trend: '98%',
      trendUp: true,
      icon: HardHat,
      color: '#f59e0b',
      sparkline: [94, 95, 96, 97, 97, 98, 98],
      subtitle: 'Zero incidents this month'
    },
    { 
      label: 'Infrastructure Index', 
      value: '92', 
      trend: '+3',
      trendUp: true,
      icon: Building,
      color: '#6366f1',
      sparkline: [86, 87, 88, 89, 90, 91, 92],
      subtitle: 'Overall condition rating'
    },
  ]

  const engineeringProjects = [
    { 
      id: 1,
      name: 'North Bridge Renovation',
      type: 'Infrastructure',
      status: 'in-progress',
      progress: 68,
      budget: 8500000,
      spent: 5780000,
      team: { engineers: 12, workers: 45, total: 57 },
      timeline: { start: '2024-01', end: '2024-12', daysRemaining: 127 },
      color: '#0891b2',
      location: 'North District',
      priority: 'high',
      safety: { incidents: 0, inspections: 24, compliance: 100 },
      milestones: { completed: 8, total: 12 },
      alerts: ['On Schedule']
    },
    { 
      id: 2,
      name: 'Downtown Water Main Upgrade',
      type: 'Utilities',
      status: 'in-progress',
      progress: 42,
      budget: 5200000,
      spent: 2184000,
      team: { engineers: 8, workers: 28, total: 36 },
      timeline: { start: '2024-03', end: '2025-02', daysRemaining: 245 },
      color: '#06b6d4',
      location: 'Downtown',
      priority: 'critical',
      safety: { incidents: 0, inspections: 18, compliance: 100 },
      milestones: { completed: 5, total: 10 },
      alerts: ['Ahead of Schedule']
    },
    { 
      id: 3,
      name: 'East Zone Road Expansion',
      type: 'Transportation',
      status: 'planning',
      progress: 15,
      budget: 12800000,
      spent: 1920000,
      team: { engineers: 15, workers: 0, total: 15 },
      timeline: { start: '2024-06', end: '2025-12', daysRemaining: 458 },
      color: '#10b981',
      location: 'East Zone',
      priority: 'medium',
      safety: { incidents: 0, inspections: 8, compliance: 100 },
      milestones: { completed: 2, total: 15 },
      alerts: []
    },
    { 
      id: 4,
      name: 'South Park Facility',
      type: 'Recreation',
      status: 'in-progress',
      progress: 78,
      budget: 3600000,
      spent: 2808000,
      team: { engineers: 6, workers: 22, total: 28 },
      timeline: { start: '2023-09', end: '2024-04', daysRemaining: 34 },
      color: '#8b5cf6',
      location: 'South Park',
      priority: 'low',
      safety: { incidents: 0, inspections: 32, compliance: 100 },
      milestones: { completed: 11, total: 14 },
      alerts: ['Final Phase']
    },
  ]

  const Sparkline = ({ data, color, height = 40 }) => {
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min || 1
    const width = 100
    const points = data.map((val, i) => {
      const x = (i / (data.length - 1)) * width
      const y = height - ((val - min) / range) * height
      return `${x},${y}`
    }).join(' ')

    return (
      <svg width={width} height={height} className="opacity-60">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    )
  }

  const RadialGauge = ({ value, max = 100, size = 120, color, label }) => {
    const percentage = (value / max) * 100
    const circumference = 2 * Math.PI * 45
    const strokeDashoffset = circumference - (percentage / 100) * circumference

    return (
      <div className="flex flex-col items-center">
        <div className="relative" style={{ width: size, height: size }}>
          <svg className="transform -rotate-90" width={size} height={size}>
            <circle cx={size / 2} cy={size / 2} r="45" fill="none" stroke="#F3F4F6" strokeWidth="8" />
            <circle
              cx={size / 2} cy={size / 2} r="45" fill="none" stroke={color} strokeWidth="8"
              strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-gray-900">{percentage.toFixed(0)}%</span>
            <span className="text-xs text-gray-500">{value.toFixed(0)}/{max}</span>
          </div>
        </div>
        {label && <p className="text-sm text-gray-600 mt-2">{label}</p>}
      </div>
    )
  }

  const PriorityBadge = ({ priority }) => {
    const styles = {
      critical: 'bg-red-100 text-red-700 border-red-300',
      high: 'bg-orange-100 text-orange-700 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
      low: 'bg-green-100 text-green-700 border-green-300',
      completed: 'bg-blue-100 text-blue-700 border-blue-300'
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${styles[priority] || styles.low}`}>
        {priority}
      </span>
    )
  }

  const formatCurrency = (amount) => {
    return `$${(amount / 1000000).toFixed(1)}M`
  }

  return (
    <>
      <div className={`min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-50 via-cyan-50 to-blue-50 transition-all duration-300 ${
        showChat && !isChatMinimized ? 'ml-[420px]' : 'ml-0'
      }`}>
        {/* Animated blueprint/grid pattern watermark */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 1200 800">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#0891b2" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {showChat && (
          <div className="fixed left-0 top-0 bottom-0 z-40">
            <AgentChatBot
              agentType="engineering"
              agentName="Engineering Services"
              agentColor="#0891b2"
              onClose={() => setShowChat(false)}
              isMinimized={isChatMinimized}
              onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
            />
          </div>
        )}

        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="sticky top-0 z-30 backdrop-blur-xl bg-white/70 border-b border-cyan-200/50 shadow-lg"
        >
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.button
                  onClick={() => navigate('/')}
                  className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 text-white hover:shadow-lg transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={20} />
                </motion.button>
                <div>
                  <div className="flex items-center gap-3">
                    <Wrench className="text-cyan-600" size={28} />
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                      Engineering Services
                    </h1>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Infrastructure Development & Project Management</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur border border-cyan-200">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-gray-700">18 Projects Active</span>
                </div>

                {!showChat && (
                  <motion.button
                    onClick={() => setShowChat(true)}
                    className="p-2 rounded-xl bg-cyan-500 text-white hover:bg-cyan-600 transition-all"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <MessageSquare size={20} />
                  </motion.button>
                )}
              </div>
            </div>
          </div>
        </motion.header>

        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpiMetrics.map((metric, index) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="group relative"
              >
                <div className="relative backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-3 rounded-2xl`} style={{ 
                        background: `linear-gradient(135deg, ${metric.color}20, ${metric.color}40)` 
                      }}>
                        <metric.icon size={24} style={{ color: metric.color }} />
                      </div>
                      <div className="flex items-center gap-1">
                        {metric.trendUp ? (
                          <TrendingUp size={16} className="text-green-600" />
                        ) : (
                          <TrendingDown size={16} className="text-orange-600" />
                        )}
                        <span className={`text-sm font-semibold ${metric.trendUp ? 'text-green-600' : 'text-orange-600'}`}>
                          {metric.trend}
                        </span>
                      </div>
                    </div>

                    <div className="mb-2">
                      <h3 className="text-3xl font-bold text-gray-900">{metric.value}</h3>
                      <p className="text-sm text-gray-600 mt-1">{metric.label}</p>
                    </div>

                    <p className="text-xs text-gray-500 mb-3">{metric.subtitle}</p>

                    <div className="mt-4">
                      <Sparkline data={metric.sparkline} color={metric.color} height={32} />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Projects Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl"
              >
                <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold mb-1">Active Projects</h2>
                      <p className="text-cyan-100 text-sm">Infrastructure development status</p>
                    </div>
                    <Construction size={32} className="opacity-80" />
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {engineeringProjects.map((project, index) => (
                    <motion.div
                      key={project.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="group relative"
                    >
                      <div className="backdrop-blur-sm bg-white/60 border border-white/80 rounded-2xl p-5 hover:bg-white/90 hover:shadow-lg transition-all cursor-pointer"
                        onClick={() => setSelectedProject(project.id === selectedProject ? null : project.id)}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-bold text-gray-900">{project.name}</h3>
                              {project.alerts.length > 0 && (
                                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
                                  <CheckCircle size={12} />
                                  {project.alerts[0]}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              <div className="flex items-center gap-1">
                                <MapPin size={14} />
                                <span>{project.location}</span>
                              </div>
                              <span>•</span>
                              <span>{project.type}</span>
                              <span>•</span>
                              <PriorityBadge priority={project.priority} />
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <div className="flex items-center justify-center">
                            <RadialGauge 
                              value={project.progress} 
                              max={100} 
                              size={90}
                              color={project.progress > 80 ? '#10b981' : project.color}
                              label="Progress"
                            />
                          </div>

                          <div className="col-span-2 grid grid-cols-2 gap-3">
                            <div className="bg-cyan-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Users size={16} className="text-cyan-600" />
                                <p className="text-xs font-medium text-gray-600">Team Size</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{project.team.total}</p>
                            </div>

                            <div className="bg-blue-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Timer size={16} className="text-blue-600" />
                                <p className="text-xs font-medium text-gray-600">Days Left</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{project.timeline.daysRemaining}</p>
                            </div>
                          </div>
                        </div>

                        <div className="mb-4">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-xs text-gray-600">Budget: {formatCurrency(project.budget)}</span>
                            <span className="text-xs font-semibold text-gray-700">
                              {formatCurrency(project.spent)} spent ({((project.spent/project.budget)*100).toFixed(0)}%)
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="h-2 rounded-full transition-all duration-500" 
                              style={{ 
                                width: `${(project.spent/project.budget)*100}%`,
                                background: `linear-gradient(90deg, ${project.color}, ${project.color}dd)`
                              }}
                            />
                          </div>
                        </div>

                        <div className="flex items-center gap-2 flex-wrap">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-cyan-500 text-white text-sm font-medium hover:bg-cyan-600 transition-colors"
                          >
                            <Phone size={14} />
                            Contact PM
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors"
                          >
                            <Ruler size={14} />
                            Blueprint
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-500 text-white text-sm font-medium hover:bg-indigo-600 transition-colors"
                          >
                            <Activity size={14} />
                            Reports
                          </motion.button>
                        </div>

                        <AnimatePresence>
                          {selectedProject === project.id && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="mt-4 pt-4 border-t border-gray-200"
                            >
                              <div className="grid grid-cols-3 gap-4">
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Safety Record</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Incidents:</span>
                                      <span className="font-semibold text-green-600">{project.safety.incidents}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Inspections:</span>
                                      <span className="font-semibold">{project.safety.inspections}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Compliance:</span>
                                      <span className="font-semibold text-green-600">{project.safety.compliance}%</span>
                                    </div>
                                  </div>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Team Breakdown</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Engineers:</span>
                                      <span className="font-semibold">{project.team.engineers}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Workers:</span>
                                      <span className="font-semibold">{project.team.workers}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Total:</span>
                                      <span className="font-semibold">{project.team.total}</span>
                                    </div>
                                  </div>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Milestones</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Completed:</span>
                                      <span className="font-semibold text-green-600">{project.milestones.completed}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Total:</span>
                                      <span className="font-semibold">{project.milestones.total}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Progress:</span>
                                      <span className="font-semibold text-cyan-600">
                                        {((project.milestones.completed/project.milestones.total)*100).toFixed(0)}%
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* Recent Activity */}
            <div>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl h-full"
              >
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold mb-1">Recent Activity</h2>
                      <p className="text-blue-100 text-sm">Engineering queries</p>
                    </div>
                    <Activity size={28} className="opacity-80" />
                  </div>
                </div>

                <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
                  {loadingHistory ? (
                    <div className="text-center py-8">
                      <div className="animate-pulse space-y-3">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
                        <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
                      </div>
                      <p className="text-gray-500 text-sm mt-4">Loading activity...</p>
                    </div>
                  ) : chatHistory.length === 0 ? (
                    <div className="text-center py-8">
                      <MessageSquare size={48} className="mx-auto text-gray-300 mb-4" />
                      <p className="text-gray-500 font-medium">No recent activity</p>
                      <p className="text-gray-400 text-sm mt-1">Start a conversation!</p>
                    </div>
                  ) : (
                    chatHistory.slice(0, 5).map((item, index) => (
                      <motion.div
                        key={item.id || index}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.7 + index * 0.1 }}
                        className="backdrop-blur-sm bg-white/80 border border-cyan-200 rounded-2xl p-4 hover:bg-white hover:shadow-md transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-cyan-500 to-blue-500 text-white">
                            <Wrench size={20} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            {item.summary ? (
                              <div className="text-sm text-gray-900 mb-2 whitespace-pre-line leading-relaxed">
                                {item.summary}
                              </div>
                            ) : (
                              <p className="text-sm text-gray-900 mb-2 line-clamp-2">
                                Engineering query processed
                              </p>
                            )}
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500 flex items-center gap-1">
                                <Clock size={11} />
                                {getRelativeTime(item.created_at)}
                              </span>
                              <PriorityBadge priority="completed" />
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              </motion.div>
            </div>
          </div>

          {/* Engineering Analytics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 text-white">
                  <Target size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Quarterly Targets</h3>
                  <p className="text-xs text-gray-600">Completion goals</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Projects Completed</span>
                  <span className="text-xl font-bold text-cyan-600">12/14</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">On-Time Rate</span>
                  <span className="text-xl font-bold text-green-600">87%</span>
                </div>
                <div className="mt-4 p-3 bg-cyan-50 rounded-xl">
                  <p className="text-xs text-cyan-800">
                    <span className="font-semibold">Status:</span> 2 major projects ahead of schedule
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500 to-amber-500 text-white">
                  <HardHat size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Safety Rating</h3>
                  <p className="text-xs text-gray-600">Incident-free performance</p>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <RadialGauge 
                  value={98} 
                  max={100} 
                  size={140}
                  color="#f59e0b"
                  label="Safety Score: 98/100"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-green-500 text-white">
                  <Award size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Quality Metrics</h3>
                  <p className="text-xs text-gray-600">Standards compliance</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Quality Score</span>
                  <span className="text-lg font-semibold text-green-600">A+</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Inspections Passed</span>
                  <span className="text-lg font-semibold text-green-600">100%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Code Compliance</span>
                  <span className="text-lg font-semibold text-green-600">100%</span>
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-xl">
                  <p className="text-xs text-green-800 font-semibold">
                    All projects meet or exceed quality standards
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </>
  )
}

export default EngineeringAgentPage
