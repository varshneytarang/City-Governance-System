import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Trash2, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home, MessageSquare,
  Users, Recycle, AlertCircle, Phone, MapPinned, Leaf, Droplets,
  TrendingDown, Truck, Award, Timer, Target, Package, Wind, TreePine
} from 'lucide-react'
import AgentChatBot from './AgentChatBot'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const SanitationAgentPage = () => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [chatHistory, setChatHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [selectedZone, setSelectedZone] = useState(null)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])
  
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/agents/sanitation/history?limit=10`)
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
      label: 'Collection Rate', 
      value: '96%', 
      trend: '+3%',
      trendUp: true,
      icon: Trash2,
      color: '#10b981',
      sparkline: [92, 93, 94, 94, 95, 95, 96],
      subtitle: 'On-time pickups'
    },
    { 
      label: 'Recycling Rate', 
      value: '68%', 
      trend: '+5%',
      trendUp: true,
      icon: Recycle,
      color: '#14b8a6',
      sparkline: [60, 62, 64, 65, 66, 67, 68],
      subtitle: 'Material recovery'
    },
    { 
      label: 'Active Trucks', 
      value: '42', 
      target: 45,
      trend: '93%',
      trendUp: true,
      icon: Truck,
      color: '#06b6d4',
      sparkline: [38, 39, 40, 41, 41, 42, 42],
      subtitle: '3 in maintenance'
    },
    { 
      label: 'Daily Tonnage', 
      value: '285', 
      trend: '+12',
      trendUp: false,
      icon: Package,
      color: '#0ea5e9',
      sparkline: [268, 270, 275, 278, 280, 283, 285],
      subtitle: 'Tons collected today'
    },
  ]

  const sanitationZones = [
    { 
      id: 1,
      name: 'North District',
      location: 'Residential Area',
      status: 'active',
      trucks: 12,
      available: 10,
      collectionRate: 97,
      crew: { onDuty: 36, total: 48 },
      routes: { completed: 18, total: 24 },
      recyclables: 42,
      coordinates: { lat: 40.7589, lng: -73.9851 },
      alerts: ['2 Trucks Active']
    },
    { 
      id: 2,
      name: 'South District',
      location: 'Commercial Zone',
      status: 'completed',
      trucks: 10,
      available: 10,
      collectionRate: 98,
      crew: { onDuty: 30, total: 40 },
      routes: { completed: 20, total: 20 },
      recyclables: 56,
      coordinates: { lat: 40.7489, lng: -73.9851 },
      alerts: []
    },
    { 
      id: 3,
      name: 'East Zone',
      location: 'Mixed Use',
      status: 'active',
      trucks: 11,
      available: 9,
      collectionRate: 95,
      crew: { onDuty: 33, total: 44 },
      routes: { completed: 15, total: 22 },
      recyclables: 38,
      coordinates: { lat: 40.7589, lng: -73.9751 },
      alerts: ['Peak Collection Hours']
    },
    { 
      id: 4,
      name: 'West District',
      location: 'Industrial Area',
      status: 'ready',
      trucks: 9,
      available: 9,
      collectionRate: 94,
      crew: { onDuty: 27, total: 36 },
      routes: { completed: 12, total: 18 },
      recyclables: 64,
      coordinates: { lat: 40.7589, lng: -73.9951 },
      alerts: []
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
            <span className="text-xs text-gray-500">{value}/{max}</span>
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

  return (
    <>
      <div className={`min-h-screen relative overflow-hidden bg-gradient-to-br from-green-50 via-cyan-50 to-blue-50 transition-all duration-300 ${
        showChat && !isChatMinimized ? 'ml-[420px]' : 'ml-0'
      }`}>
        {/* Animated recycle pattern watermark */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 1200 800">
            <motion.circle
              cx="300" cy="200" r="80"
              stroke="#10b981"
              strokeWidth="4"
              fill="none"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
            />
            <motion.circle
              cx="900" cy="600" r="100"
              stroke="#06b6d4"
              strokeWidth="4"
              fill="none"
              initial={{ scale: 1, opacity: 0 }}
              animate={{ scale: 0.8, opacity: 1 }}
              transition={{ duration: 2, repeat: Infinity, repeatType: "reverse", delay: 1 }}
            />
          </svg>
        </div>

        {showChat && (
          <div className="fixed left-0 top-0 bottom-0 z-40">
            <AgentChatBot
              agentType="sanitation"
              agentName="Sanitation Services"
              agentColor="#10b981"
              onClose={() => setShowChat(false)}
              isMinimized={isChatMinimized}
              onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
            />
          </div>
        )}

        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="sticky top-0 z-30 backdrop-blur-xl bg-white/70 border-b border-green-200/50 shadow-lg"
        >
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.button
                  onClick={() => navigate('/')}
                  className="p-2 rounded-xl bg-gradient-to-br from-green-500 to-cyan-500 text-white hover:shadow-lg transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={20} />
                </motion.button>
                <div>
                  <div className="flex items-center gap-3">
                    <Recycle className="text-green-600" size={28} />
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-cyan-600 bg-clip-text text-transparent">
                      Sanitation Services
                    </h1>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Waste Collection & Recycling Management</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur border border-green-200">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-gray-700">Operations Active</span>
                </div>

                {!showChat && (
                  <motion.button
                    onClick={() => setShowChat(true)}
                    className="p-2 rounded-xl bg-green-500 text-white hover:bg-green-600 transition-all"
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
                  <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
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

          {/* Collection Zones Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl"
              >
                <div className="bg-gradient-to-r from-green-500 to-cyan-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold mb-1">Collection Zones</h2>
                      <p className="text-green-100 text-sm">Real-time operations status</p>
                    </div>
                    <MapPin size={32} className="opacity-80" />
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {sanitationZones.map((zone, index) => (
                    <motion.div
                      key={zone.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="group relative"
                    >
                      <div className="backdrop-blur-sm bg-white/60 border border-white/80 rounded-2xl p-5 hover:bg-white/90 hover:shadow-lg transition-all cursor-pointer"
                        onClick={() => setSelectedZone(zone.id === selectedZone ? null : zone.id)}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-bold text-gray-900">{zone.name}</h3>
                              {zone.alerts.length > 0 && (
                                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
                                  <Truck size={12} />
                                  {zone.alerts[0]}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <MapPinned size={14} />
                              <span>{zone.location}</span>
                            </div>
                          </div>

                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            zone.status === 'active' ? 'bg-green-100 text-green-700 border border-green-300' :
                            zone.status === 'completed' ? 'bg-blue-100 text-blue-700 border border-blue-300' :
                            'bg-gray-100 text-gray-700 border border-gray-300'
                          }`}>
                            {zone.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <div className="flex items-center justify-center">
                            <RadialGauge 
                              value={zone.routes.completed} 
                              max={zone.routes.total} 
                              size={90}
                              color={zone.routes.completed === zone.routes.total ? '#10b981' : '#06b6d4'}
                              label="Routes Complete"
                            />
                          </div>

                          <div className="col-span-2 grid grid-cols-2 gap-3">
                            <div className="bg-green-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Users size={16} className="text-green-600" />
                                <p className="text-xs font-medium text-gray-600">Crew</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{zone.crew.onDuty}</p>
                            </div>

                            <div className="bg-cyan-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Recycle size={16} className="text-cyan-600" />
                                <p className="text-xs font-medium text-gray-600">Recycling</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{zone.recyclables}%</p>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 flex-wrap">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500 text-white text-sm font-medium hover:bg-green-600 transition-colors"
                          >
                            <Phone size={14} />
                            Contact
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-cyan-500 text-white text-sm font-medium hover:bg-cyan-600 transition-colors"
                          >
                            <MapPin size={14} />
                            Track
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors"
                          >
                            <Activity size={14} />
                            Details
                          </motion.button>
                        </div>

                        <AnimatePresence>
                          {selectedZone === zone.id && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="mt-4 pt-4 border-t border-gray-200"
                            >
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Fleet Status</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Total Trucks:</span>
                                      <span className="font-semibold">{zone.trucks}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Available:</span>
                                      <span className="font-semibold text-green-600">{zone.available}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">In Service:</span>
                                      <span className="font-semibold">{zone.trucks - zone.available}</span>
                                    </div>
                                  </div>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Performance</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Collection Rate:</span>
                                      <span className="font-semibold text-green-600">{zone.collectionRate}%</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Total Crew:</span>
                                      <span className="font-semibold">{zone.crew.total}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Recycling Rate:</span>
                                      <span className="font-semibold text-cyan-600">{zone.recyclables}%</span>
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
                <div className="bg-gradient-to-r from-cyan-500 to-green-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold mb-1">Recent Activity</h2>
                      <p className="text-cyan-100 text-sm">Department operations</p>
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
                        className="backdrop-blur-sm bg-white/80 border border-green-200 rounded-2xl p-4 hover:bg-white hover:shadow-md transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-green-500 to-cyan-500 text-white">
                            <Recycle size={20} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            {item.summary ? (
                              <div className="text-sm text-gray-900 mb-2 whitespace-pre-line leading-relaxed">
                                {item.summary}
                              </div>
                            ) : (
                              <p className="text-sm text-gray-900 mb-2 line-clamp-2">
                                Sanitation service query processed
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

          {/* Environmental Analytics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 text-white">
                  <Target size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Today's Progress</h3>
                  <p className="text-xs text-gray-600">Collection targets</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Waste Collected</span>
                  <span className="text-xl font-bold text-green-600">285 tons</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Recycled Materials</span>
                  <span className="text-xl font-bold text-cyan-600">194 tons</span>
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-xl">
                  <p className="text-xs text-green-800">
                    <span className="font-semibold">Goal:</span> 300 tons daily target - 95% achieved
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
                <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 text-white">
                  <Recycle size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Recycling Goal</h3>
                  <p className="text-xs text-gray-600">Monthly achievement</p>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <RadialGauge 
                  value={68} 
                  max={75} 
                  size={140}
                  color="#06b6d4"
                  label="Target: 75%"
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
                  <Leaf size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Environmental Impact</h3>
                  <p className="text-xs text-gray-600">Carbon reduction</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">CO₂ Saved</span>
                  <div className="flex items-center gap-2">
                    <TreePine size={16} className="text-green-600" />
                    <span className="text-sm font-semibold text-green-600">1,240 kg</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Waste Diverted</span>
                  <div className="flex items-center gap-2">
                    <Droplets size={16} className="text-cyan-600" />
                    <span className="text-sm font-semibold text-cyan-600">92%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Clean Streets</span>
                  <div className="flex items-center gap-2">
                    <Wind size={16} className="text-blue-600" />
                    <span className="text-sm font-semibold text-blue-600">98.5%</span>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-emerald-50 rounded-xl">
                  <p className="text-xs text-emerald-800 font-semibold">
                    Sustainability goals exceeded this month!
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

export default SanitationAgentPage
