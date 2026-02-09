import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Heart, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home, MessageSquare,
  Users, Shield, AlertCircle, Phone, ArrowRight, Bed, Syringe, 
  Stethoscope, Pill, Thermometer, Plus, Bell, Calendar, Target,
  TrendingDown, Zap, ChevronRight, ExternalLink
} from 'lucide-react'
import AgentChatBot from './AgentChatBot'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const HealthAgentPage = () => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [chatHistory, setChatHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [selectedFacility, setSelectedFacility] = useState(null)

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])
  
  // Fetch chat history from API
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/agents/health/history?limit=10`)
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
    
    // Refresh history every 30 seconds
    const interval = setInterval(fetchHistory, 30000)
    return () => clearInterval(interval)
  }, [])
  
  // Format relative time
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

  // Building2 icon component (for clinics) - MUST be defined before kpiMetrics
  const Building2 = ({ size = 24, ...props }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M3 21h18"></path>
      <path d="M9 8h1"></path>
      <path d="M9 12h1"></path>
      <path d="M9 16h1"></path>
      <path d="M14 8h1"></path>
      <path d="M14 12h1"></path>
      <path d="M14 16h1"></path>
      <path d="M6 3v18"></path>
      <path d="M18 3v18"></path>
      <path d="M6 3h12"></path>
    </svg>
  )

  // Enhanced KPI metrics with trends and sparklines
  const kpiMetrics = [
    { 
      label: 'Active Clinics', 
      value: '18', 
      trend: '+2',
      trendUp: true,
      icon: Building2,
      color: '#ec4899',
      sparkline: [15, 16, 16, 17, 17, 18, 18],
      subtitle: 'All operational'
    },
    { 
      label: 'Daily Patients', 
      value: '1,247', 
      projected: '1,450',
      trend: '+12%',
      trendUp: true,
      icon: Users,
      color: '#14b8a6',
      sparkline: [980, 1050, 1120, 1180, 1210, 1247, 1280],
      subtitle: 'Expected: 1.45K by EOD'
    },
    { 
      label: 'Vaccinations Today', 
      value: '456', 
      target: 500,
      trend: '91%',
      trendUp: true,
      icon: Syringe,
      color: '#10b981',
      sparkline: [380, 400, 420, 440, 450, 456, 470],
      subtitle: 'Target: 500'
    },
    { 
      label: 'Bed Availability', 
      value: '78%', 
      trend: '-3%',
      trendUp: false,
      icon: Bed,
      color: '#f59e0b',
      sparkline: [85, 84, 82, 81, 80, 79, 78],
      subtitle: '156 beds available'
    },
  ]

  // Health facilities with enhanced data
  const healthFacilities = [
    { 
      id: 1,
      name: 'North Health Center', 
      location: 'North District',
      status: 'operational', 
      capacity: 145, 
      occupied: 119,
      utilization: 82,
      beds: { total: 145, occupied: 119, available: 26 },
      staff: { doctors: 12, nurses: 28, support: 15 },
      services: ['Primary Care', 'Pediatrics', 'Dental'],
      phone: '+1-555-0201',
      coordinates: { lat: 40.7589, lng: -73.9851 },
      alerts: []
    },
    { 
      id: 2,
      name: 'South Clinic', 
      location: 'South District',
      status: 'operational', 
      capacity: 98, 
      occupied: 64,
      utilization: 65,
      beds: { total: 98, occupied: 64, available: 34 },
      staff: { doctors: 8, nurses: 18, support: 10 },
      services: ['Primary Care', 'Mental Health'],
      phone: '+1-555-0202',
      coordinates: { lat: 40.7489, lng: -73.9851 },
      alerts: []
    },
    { 
      id: 3,
      name: 'East Medical Unit', 
      location: 'East Zone',
      status: 'busy', 
      capacity: 120, 
      occupied: 113,
      utilization: 94,
      beds: { total: 120, occupied: 113, available: 7 },
      staff: { doctors: 10, nurses: 22, support: 12 },
      services: ['Primary Care', 'Emergency', 'Lab'],
      phone: '+1-555-0203',
      coordinates: { lat: 40.7589, lng: -73.9751 },
      alerts: ['Near Capacity']
    },
    { 
      id: 4,
      name: 'West Health Hub', 
      location: 'Westside',
      status: 'operational', 
      capacity: 87, 
      occupied: 62,
      utilization: 71,
      beds: { total: 87, occupied: 62, available: 25 },
      staff: { doctors: 7, nurses: 16, support: 9 },
      services: ['Primary Care', 'Chronic Care'],
      phone: '+1-555-0204',
      coordinates: { lat: 40.7589, lng: -73.9951 },
      alerts: []
    },
  ]

  // Sparkline component
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

  // Radial Gauge Component
  const RadialGauge = ({ value, max = 100, size = 120, color, label }) => {
    const percentage = (value / max) * 100
    const circumference = 2 * Math.PI * 45
    const strokeDashoffset = circumference - (percentage / 100) * circumference

    return (
      <div className="flex flex-col items-center">
        <div className="relative" style={{ width: size, height: size }}>
          <svg className="transform -rotate-90" width={size} height={size}>
            {/* Background circle */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r="45"
              fill="none"
              stroke="#F3F4F6"
              strokeWidth="8"
            />
            {/* Progress circle */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r="45"
              fill="none"
              stroke={color}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
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

  // Priority Badge Component
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
      {/* Medical-themed gradient background */}
      <div className={`min-h-screen relative overflow-hidden bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50 transition-all duration-300 ${
        showChat && !isChatMinimized ? 'ml-[420px]' : 'ml-0'
      }`}>
        {/* Animated DNA/Heartbeat watermark */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 1200 800">
            <motion.path
              d="M0,400 Q300,300 600,400 T1200,400"
              stroke="#ec4899"
              strokeWidth="3"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.path
              d="M0,350 Q300,450 600,350 T1200,350"
              stroke="#14b8a6"
              strokeWidth="2"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
            />
          </svg>
        </div>

        {/* Chatbot Sidebar */}
        {showChat && (
          <div className="fixed left-0 top-0 bottom-0 z-40">
            <AgentChatBot
              agentType="health"
              agentName="Health & Wellness"
              agentColor="#ec4899"
              onClose={() => setShowChat(false)}
              isMinimized={isChatMinimized}
              onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
            />
          </div>
        )}

        {/* Header with glassmorphism */}
        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="sticky top-0 z-30 backdrop-blur-xl bg-white/70 border-b border-pink-200/50 shadow-lg"
        >
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.button
                  onClick={() => navigate('/')}
                  className="p-2 rounded-xl bg-gradient-to-br from-pink-500 to-purple-500 text-white hover:shadow-lg transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={20} />
                </motion.button>
                <div>
                  <div className="flex items-center gap-3">
                    <Heart className="text-pink-600" size={28} />
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                      Health & Wellness Department
                    </h1>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Public Health Services & Medical Care</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                {/* Live Status Indicator */}
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur border border-pink-200">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-gray-700">All Systems Operational</span>
                </div>

                {!showChat && (
                  <motion.button
                    onClick={() => setShowChat(true)}
                    className="p-2 rounded-xl bg-pink-500 text-white hover:bg-pink-600 transition-all"
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

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
          {/* KPI Cards with Sparklines */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpiMetrics.map((metric, index) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="group relative"
              >
                {/* Glassmorphism card */}
                <div className="relative backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden">
                  {/* Gradient overlay on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
                  <div className="relative z-10">
                    {/* Icon and Trend */}
                    <div className="flex items-start justify-between mb-4">
                      <div className={`p-3 rounded-2xl bg-gradient-to-br`} style={{ 
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

                    {/* Value */}
                    <div className="mb-2">
                      <h3 className="text-3xl font-bold text-gray-900">{metric.value}</h3>
                      <p className="text-sm text-gray-600 mt-1">{metric.label}</p>
                    </div>

                    {/* Subtitle */}
                    <p className="text-xs text-gray-500 mb-3">{metric.subtitle}</p>

                    {/* Sparkline */}
                    <div className="mt-4">
                      <Sparkline data={metric.sparkline} color={metric.color} height={32} />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Main Grid: Facilities Map/List + Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Health Facilities - 2 columns */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl"
              >
                <div className="bg-gradient-to-r from-pink-500 to-purple-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold mb-1">Health Facilities Network</h2>
                      <p className="text-pink-100 text-sm">Real-time facility status & capacity</p>
                    </div>
                    <Building2 size={32} className="opacity-80" />
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {healthFacilities.map((facility, index) => (
                    <motion.div
                      key={facility.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="group relative"
                    >
                      <div className="backdrop-blur-sm bg-white/60 border border-white/80 rounded-2xl p-5 hover:bg-white/90 hover:shadow-lg transition-all cursor-pointer"
                        onClick={() => setSelectedFacility(facility.id === selectedFacility ? null : facility.id)}
                      >
                        {/* Facility Header */}
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-bold text-gray-900">{facility.name}</h3>
                              {facility.alerts.length > 0 && (
                                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 text-red-700 text-xs font-semibold">
                                  <Bell size={12} />
                                  {facility.alerts[0]}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <MapPin size={14} />
                              <span>{facility.location}</span>
                            </div>
                          </div>

                          {/* Status Badge */}
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            facility.status === 'busy' ? 'bg-red-100 text-red-700 border border-red-300' :
                            'bg-green-100 text-green-700 border border-green-300'
                          }`}>
                            {facility.status}
                          </span>
                        </div>

                        {/* Capacity Visualization */}
                        <div className="grid grid-cols-3 gap-4 mb-4">
                          {/* Radial Gauge */}
                          <div className="flex items-center justify-center">
                            <RadialGauge 
                              value={facility.beds.occupied} 
                              max={facility.beds.total} 
                              size={90}
                              color={facility.utilization > 90 ? '#ef4444' : facility.utilization > 75 ? '#f59e0b' : '#10b981'}
                              label="Occupancy"
                            />
                          </div>

                          {/* Stats */}
                          <div className="col-span-2 grid grid-cols-2 gap-3">
                            <div className="bg-blue-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Bed size={16} className="text-blue-600" />
                                <p className="text-xs font-medium text-gray-600">Available</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">{facility.beds.available}</p>
                            </div>

                            <div className="bg-purple-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Users size={16} className="text-purple-600" />
                                <p className="text-xs font-medium text-gray-600">Staff</p>
                              </div>
                              <p className="text-2xl font-bold text-gray-900">
                                {facility.staff.doctors + facility.staff.nurses}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="flex items-center gap-2 flex-wrap">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-pink-500 text-white text-sm font-medium hover:bg-pink-600 transition-colors"
                          >
                            <Phone size={14} />
                            Contact
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-purple-500 text-white text-sm font-medium hover:bg-purple-600 transition-colors"
                          >
                            <Calendar size={14} />
                            Schedule
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors"
                          >
                            <ExternalLink size={14} />
                            Details
                          </motion.button>
                        </div>

                        {/* Expandable Details */}
                        <AnimatePresence>
                          {selectedFacility === facility.id && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="mt-4 pt-4 border-t border-gray-200"
                            >
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Services</p>
                                  <div className="flex flex-wrap gap-1">
                                    {facility.services.map((service, i) => (
                                      <span key={i} className="px-2 py-1 rounded-full bg-pink-100 text-pink-700 text-xs">
                                        {service}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Staff Breakdown</p>
                                  <div className="space-y-1 text-xs">
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Doctors:</span>
                                      <span className="font-semibold">{facility.staff.doctors}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Nurses:</span>
                                      <span className="font-semibold">{facility.staff.nurses}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Support:</span>
                                      <span className="font-semibold">{facility.staff.support}</span>
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

            {/* Recent Activity - 1 column */}
            <div>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl h-full"
              >
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold mb-1">Recent Activity</h2>
                      <p className="text-purple-100 text-sm">Chat history with Health Agent</p>
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
                        className="backdrop-blur-sm bg-white/80 border border-pink-200 rounded-2xl p-4 hover:bg-white hover:shadow-md transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-pink-500 to-purple-500 text-white">
                            <Heart size={20} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            {item.summary ? (
                              <div className="text-sm text-gray-900 mb-2 whitespace-pre-line leading-relaxed">
                                {item.summary}
                              </div>
                            ) : (
                              <p className="text-sm text-gray-900 mb-2 line-clamp-2">
                                Health query processed
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

          {/* Analytics Dashboard Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Predictive Analysis */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
                  <Target size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Today's Forecast</h3>
                  <p className="text-xs text-gray-600">AI-powered prediction</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Expected Patients</span>
                  <span className="text-xl font-bold text-blue-600">1,450</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Peak Hour</span>
                  <span className="text-xl font-bold text-purple-600">2-4 PM</span>
                </div>
                <div className="mt-4 p-3 bg-blue-50 rounded-xl">
                  <p className="text-xs text-blue-800">
                    <span className="font-semibold">Recommendation:</span> Schedule additional staff for afternoon shift
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Vaccination Progress */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 text-white">
                  <Syringe size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Vaccination Goal</h3>
                  <p className="text-xs text-gray-600">Daily target progress</p>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <RadialGauge 
                  value={456} 
                  max={500} 
                  size={140}
                  color="#10b981"
                  label="91% Complete"
                />
              </div>
            </motion.div>

            {/* System Health */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 text-white">
                  <Shield size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">System Health</h3>
                  <p className="text-xs text-gray-600">Network status</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">EMR System</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm font-semibold text-green-600">Online</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Lab Integration</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm font-semibold text-green-600">Connected</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Pharmacy Link</span>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-sm font-semibold text-green-600">Active</span>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-xl">
                  <p className="text-xs text-green-800 font-semibold">
                    All systems operational - 99.8% uptime
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

export default HealthAgentPage
