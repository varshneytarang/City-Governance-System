import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Flame, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home, MessageSquare,
  Users, Shield, AlertCircle, Phone, Bell, Thermometer, Siren,
  TrendingDown, Radio, Truck, Award, Timer, Target, BadgeAlert, Zap
} from 'lucide-react'
import AgentChatBot from './AgentChatBot'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const FireAgentPage = () => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [chatHistory, setChatHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [selectedStation, setSelectedStation] = useState(null)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])
  
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/agents/fire/history?limit=10`)
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
      label: 'Active Units', 
      value: '24', 
      trend: '+2',
      trendUp: true,
      icon: Truck,
      color: '#f97316',
      sparkline: [20, 21, 22, 22, 23, 23, 24],
      subtitle: 'All stations ready'
    },
    { 
      label: 'Avg Response Time', 
      value: '3.2m', 
      trend: '-0.3m',
      trendUp: true,
      icon: Timer,
      color: '#14b8a6',
      sparkline: [4.2, 4.0, 3.8, 3.6, 3.5, 3.3, 3.2],
      subtitle: 'Under 4min target'
    },
    { 
      label: 'Drills Completed', 
      value: '89', 
      target: 100,
      trend: '89%',
      trendUp: true,
      icon: Award,
      color: '#10b981',
      sparkline: [72, 76, 80, 83, 86, 88, 89],
      subtitle: 'Monthly target: 100'
    },
    { 
      label: 'Equipment Ready', 
      value: '98%', 
      trend: '+2%',
      trendUp: true,
      icon: Shield,
      color: '#f59e0b',
      sparkline: [94, 95, 96, 96, 97, 97, 98],
      subtitle: '2 units in maintenance'
    },
  ]

  const fireStations = [
    { 
      id: 1,
      name: 'North Station',
      location: 'North District',
      status: 'ready',
      units: 8,
      available: 8,
      responseRate: 97,
      personnel: { onDuty: 24, total: 32 },
      equipment: { trucks: 4, ambulances: 2, specialized: 2 },
      recentDrills: 15,
      coordinates: { lat: 40.7589, lng: -73.9851 },
      alerts: []
    },
    { 
      id: 2,
      name: 'South Station',
      location: 'South District',
      status: 'ready',
      units: 6,
      available: 6,
      responseRate: 95,
      personnel: { onDuty: 18, total: 24 },
      equipment: { trucks: 3, ambulances: 2, specialized: 1 },
      recentDrills: 12,
      coordinates: { lat: 40.7489, lng: -73.9851 },
      alerts: []
    },
    { 
      id: 3,
      name: 'East Station',
      location: 'East Zone',
      status: 'active',
      units: 5,
      available: 3,
      responseRate: 98,
      personnel: { onDuty: 20, total: 28 },
      equipment: { trucks: 3, ambulances: 1, specialized: 1 },
      recentDrills: 18,
      coordinates: { lat: 40.7589, lng: -73.9751 },
      alerts: ['2 Units Deployed']
    },
    { 
      id: 4,
      name: 'West Station',
      location: 'Westside',
      status: 'ready',
      units: 5,
      available: 5,
      responseRate: 96,
      personnel: { onDuty: 16, total: 20 },
      equipment: { trucks: 2, ambulances: 2, specialized: 1 },
      recentDrills: 14,
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
      <div className={`min-h-screen relative overflow-hidden bg-gradient-to-br from-orange-50 via-red-50 to-yellow-50 transition-all duration-300 ${
        showChat && !isChatMinimized ? 'ml-[420px]' : 'ml-0'
      }`}>
        {/* Animated flame/alert pattern watermark */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 1200 800">
            <motion.path
              d="M600,100 Q550,200 600,300 T600,500 Q550,600 600,700"
              stroke="#f97316"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
          </svg>
        </div>

        {showChat && (
          <div className="fixed left-0 top-0 bottom-0 z-40">
            <AgentChatBot
              agentType="fire"
              agentName="Fire & Emergency"
              agentColor="#f97316"
              onClose={() => setShowChat(false)}
              isMinimized={isChatMinimized}
              onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
            />
          </div>
        )}

        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="sticky top-0 z-30 backdrop-blur-xl bg-white/70 border-b border-orange-200/50 shadow-lg"
        >
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.button
                  onClick={() => navigate('/')}
                  className="p-2 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 text-white hover:shadow-lg transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={20} />
                </motion.button>
                <div>
                  <div className="flex items-center gap-3">
                    <Flame className="text-orange-600" size={28} />
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                      Fire & Emergency Services
                    </h1>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Emergency Response & Fire Prevention</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur border border-orange-200">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-gray-700">All Stations Ready</span>
                </div>

                {!showChat && (
                  <motion.button
                    onClick={() => setShowChat(true)}
                    className="p-2 rounded-xl bg-orange-500 text-white hover:bg-orange-600 transition-all"
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
                  <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-red-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
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

          {/* Fire Stations Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl"
              >
                <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold mb-1">Fire Station Network</h2>
                      <p className="text-orange-100 text-sm">Real-time readiness status</p>
                    </div>
                    <Siren size={32} className="opacity-80" />
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {fireStations.map((station, index) => (
                    <motion.div
                      key={station.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="group relative"
                    >
                      <div className="backdrop-blur-sm bg-white/60 border border-white/80 rounded-2xl p-5 hover:bg-white/90 hover:shadow-lg transition-all cursor-pointer"
                        onClick={() => setSelectedStation(station.id === selectedStation ? null : station.id)}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-bold text-gray-900">{station.name}</h3>
                              {station.alerts.length > 0 && (
                                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-orange-100 text-orange-700 text-xs font-semibold">
                                  <Radio size={12} />
                                  {station.alerts[0]}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <MapPin size={14} />
                              <span>{station.location}</span>
                            </div>
                          </div>

                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            station.status === 'active' ? 'bg-orange-100 text-orange-700 border border-orange-300' :
                            'bg-green-100 text-green-700 border border-green-300'
                          }`}>
                            {station.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <div className="flex items-center justify-center">
                            <RadialGauge 
                              value={station.available} 
                              max={station.units} 
                              size={90}
                              color={station.available === station.units ? '#10b981' : '#f59e0b'}
                              label="Units Available"
                            />
                          </div>

                          <div className="col-span-2 grid grid-cols-2 gap-3">
                            <div className="bg-orange-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Users size={16} className="text-orange-600" />
                                <p className="text-xs font-medium text-gray-600">On Duty</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{station.personnel.onDuty}</p>
                            </div>

                            <div className="bg-red-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Truck size={16} className="text-red-600" />
                                <p className="text-xs font-medium text-gray-600">Trucks</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{station.equipment.trucks}</p>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 flex-wrap">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-orange-500 text-white text-sm font-medium hover:bg-orange-600 transition-colors"
                          >
                            <Phone size={14} />
                            Contact
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500 text-white text-sm font-medium hover:bg-red-600 transition-colors"
                          >
                            <BadgeAlert size={14} />
                            Alert
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors"
                          >
                            <Activity size={14} />
                            Status
                          </motion.button>
                        </div>

                        <AnimatePresence>
                          {selectedStation === station.id && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="mt-4 pt-4 border-t border-gray-200"
                            >
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Equipment Details</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Fire Trucks:</span>
                                      <span className="font-semibold">{station.equipment.trucks}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Ambulances:</span>
                                      <span className="font-semibold">{station.equipment.ambulances}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Specialized:</span>
                                      <span className="font-semibold">{station.equipment.specialized}</span>
                                    </div>
                                  </div>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Performance</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Response Rate:</span>
                                      <span className="font-semibold text-green-600">{station.responseRate}%</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Recent Drills:</span>
                                      <span className="font-semibold">{station.recentDrills}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Total Staff:</span>
                                      <span className="font-semibold">{station.personnel.total}</span>
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
                <div className="bg-gradient-to-r from-red-500 to-orange-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold mb-1">Recent Activity</h2>
                      <p className="text-red-100 text-sm">Department operations</p>
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
                        className="backdrop-blur-sm bg-white/80 border border-orange-200 rounded-2xl p-4 hover:bg-white hover:shadow-md transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-orange-500 to-red-500 text-white">
                            <Flame size={20} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            {item.summary ? (
                              <div className="text-sm text-gray-900 mb-2 whitespace-pre-line leading-relaxed">
                                {item.summary}
                              </div>
                            ) : (
                              <p className="text-sm text-gray-900 mb-2 line-clamp-2">
                                Fire department query processed
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

          {/* Emergency Analytics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 text-white">
                  <Target size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Today's Forecast</h3>
                  <p className="text-xs text-gray-600">Response predictions</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Expected Calls</span>
                  <span className="text-xl font-bold text-orange-600">8-12</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Peak Period</span>
                  <span className="text-xl font-bold text-red-600">2-6 PM</span>
                </div>
                <div className="mt-4 p-3 bg-orange-50 rounded-xl">
                  <p className="text-xs text-orange-800">
                    <span className="font-semibold">Alert:</span> High fire risk due to dry conditions
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
                <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 text-white">
                  <Award size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Training Progress</h3>
                  <p className="text-xs text-gray-600">Monthly drill completion</p>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <RadialGauge 
                  value={89} 
                  max={100} 
                  size={140}
                  color="#10b981"
                  label="89% Complete"
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
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
                  <Shield size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">System Status</h3>
                  <p className="text-xs text-gray-600">Network health</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Dispatch System</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm font-semibold text-green-600">Online</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Radio Network</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm font-semibold text-green-600">Active</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">GPS Tracking</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm font-semibold text-green-600">Connected</span>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-xl">
                  <p className="text-xs text-green-800 font-semibold">
                    All systems operational - 99.9% uptime
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

export default FireAgentPage
