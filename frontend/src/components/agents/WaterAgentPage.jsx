import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Droplets, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home, MessageSquare,
  CloudRain, Sun, Cloud, Thermometer, Wind, AlertCircle, Wrench, Users,
  BarChart3, TrendingDown, Zap, Shield, ArrowUp, ArrowDown, Radio
} from 'lucide-react'
import AgentChatBot from './AgentChatBot'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const WaterAgentPage = () => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [chatHistory, setChatHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  
  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])
  
  // Fetch chat history from API
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/agents/water/history?limit=10`)
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
  
  // Extract query summary from request
  const getQuerySummary = (request) => {
    if (!request) return 'Query processed'
    
    // Try to get the actual query text
    if (request.query) return request.query
    if (request.description) return request.description
    if (request.message) return request.message
    
    // Fallback to request type
    if (request.type) {
      return request.type
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
    }
    
    return 'Query processed'
  }

  // Hero KPI Stats with trends
  const heroStats = [
    { 
      label: 'Active Repairs', 
      value: '12', 
      icon: Wrench, 
      color: '#FF9F1C',
      trend: '+3',
      trendUp: true,
      sparkline: [5, 8, 6, 9, 7, 10, 12]
    },
    { 
      label: 'Water Pressure', 
      value: '98%', 
      icon: Activity, 
      color: '#0077B6',
      trend: 'Normal',
      trendUp: true,
      sparkline: [95, 96, 97, 98, 97, 98, 98]
    },
    { 
      label: 'Water Quality', 
      value: '94/100', 
      icon: Shield, 
      color: '#2D6A4F',
      trend: '+2',
      trendUp: true,
      sparkline: [88, 90, 91, 92, 93, 93, 94]
    },
    { 
      label: 'Daily Consumption', 
      value: '2.4M', 
      unit: 'Gallons',
      icon: Droplets, 
      color: '#0077B6',
      trend: '-0.3M',
      trendUp: false,
      sparkline: [2.8, 2.7, 2.6, 2.5, 2.5, 2.4, 2.4]
    },
  ]
  
  const stats = [
    { label: 'Active Pipelines', value: '487', icon: Activity, color: '#3b82f6' },
    { label: 'Daily Consumption', value: '2.4M L', icon: TrendingUp, color: '#14b8a6' },
    { label: 'Quality Tests', value: '156', icon: CheckCircle, color: '#10b981' },
    { label: 'Response Time', value: '1.2s', icon: Clock, color: '#f59e0b' },
  ]

  // Live Activity Feed
  const liveActivities = [
    { id: 1, message: 'Team A reached Leak Site #08', time: '2 min ago', type: 'location', icon: MapPin },
    { id: 2, message: 'Pressure restored in Sector 7', time: '5 min ago', type: 'success', icon: CheckCircle },
    { id: 3, message: 'Quality test initiated - Zone B', time: '12 min ago', type: 'info', icon: Activity },
    { id: 4, message: 'Maintenance crew dispatched', time: '18 min ago', type: 'warning', icon: Wrench },
    { id: 5, message: 'Tank level optimized - North', time: '25 min ago', type: 'success', icon: TrendingUp },
  ]

  // Weather Data
  const weather = {
    temp: 24,
    condition: 'Partly Cloudy',
    humidity: 65,
    precipitation: '20%',
    icon: Cloud
  }

  const zones = [
    { name: 'North Zone', status: 'optimal', consumption: '650K L', quality: 98, pressure: 95, tankLevel: 87, coordinates: { lat: 40.7589, lng: -73.9851 } },
    { name: 'South Zone', status: 'optimal', consumption: '720K L', quality: 97, pressure: 93, tankLevel: 92, coordinates: { lat: 40.7489, lng: -73.9851 } },
    { name: 'East Zone', status: 'good', consumption: '580K L', quality: 96, pressure: 91, tankLevel: 78, coordinates: { lat: 40.7589, lng: -73.9751 } },
    { name: 'West Zone', status: 'maintenance', consumption: '450K L', quality: 99, pressure: 88, tankLevel: 65, coordinates: { lat: 40.7589, lng: -73.9951 } },
  ]

  // Circular Gauge Component
  const CircularGauge = ({ value, label, color, size = 120 }) => {
    const circumference = 2 * Math.PI * 45
    const strokeDashoffset = circumference - (value / 100) * circumference

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
              stroke="#E5E7EB"
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
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold" style={{ color }}>{value}%</span>
            <span className="text-xs text-gray-500 mt-1">{label}</span>
          </div>
        </div>
      </div>
    )
  }

  // Sparkline Component
  const Sparkline = ({ data, color, height = 40 }) => {
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min || 1
    const width = 80
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width
      const y = height - ((value - min) / range) * height
      return `${x},${y}`
    }).join(' ')

    return (
      <svg width={width} height={height} className="overflow-visible">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {data.map((value, index) => {
          const x = (index / (data.length - 1)) * width
          const y = height - ((value - min) / range) * height
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="2"
              fill={color}
              opacity={index === data.length - 1 ? 1 : 0.5}
            />
          )
        })}
      </svg>
    )
  }

  // Status Badge Component
  const StatusBadge = ({ status }) => {
    const statusConfig = {
      completed: { color: 'bg-green-100 text-green-700 border-green-200', icon: CheckCircle, label: 'Completed' },
      'in-progress': { color: 'bg-orange-100 text-orange-700 border-orange-200', icon: Radio, label: 'In Progress' },
      active: { color: 'bg-blue-100 text-blue-700 border-blue-200', icon: Activity, label: 'Active' },
      optimal: { color: 'bg-green-100 text-green-700 border-green-200', icon: CheckCircle, label: 'Optimal' },
      good: { color: 'bg-blue-100 text-blue-700 border-blue-200', icon: CheckCircle, label: 'Good' },
      maintenance: { color: 'bg-orange-100 text-orange-700 border-orange-200', icon: Wrench, label: 'Maintenance' },
    }

    const config = statusConfig[status] || statusConfig.active
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${config.color}`}>
        <Icon size={12} />
        {config.label}
      </span>
    )
  }

  return (
    <div className={`min-h-screen relative overflow-hidden transition-all duration-300 ${
      showChat && !isChatMinimized ? 'ml-[420px]' : 'ml-0'
    }`}>
      {/* Animated Water-themed Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-100 -z-10" />
      
      {/* Subtle Wave Pattern Overlay */}
      <div className="fixed inset-0 opacity-[0.03] -z-10" 
        style={{ 
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 30c10 0 10-10 20-10s10 10 20 10 10-10 20-10 10 10 20 10v10c-10 0-10 10-20 10s-10-10-20-10-10 10-20 10S10 40 0 40V30z' fill='%230077B6' fill-rule='evenodd'/%3E%3C/svg%3E")`,
          backgroundSize: '60px 60px'
        }}
      />

      {/* Chatbot Sidebar */}
      {showChat && (
        <div className="fixed left-0 top-0 bottom-0 z-40">
          <AgentChatBot
            agentType="water"
            agentName="Water Management"
            agentColor="#0077B6"
            onClose={() => setShowChat(false)}
            isMinimized={isChatMinimized}
            onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
          />
        </div>
      )}

      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${showChat && !isChatMinimized ? 'ml-[380px]' : isChatMinimized ? 'ml-12' : 'ml-0'}`}>
        {/* Floating Chat Toggle Button */}
        {(!showChat || isChatMinimized) && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            onClick={() => {
              setShowChat(true)
              if (isChatMinimized) {
                setIsChatMinimized(false)
              }
            }}
            className="fixed left-4 bottom-4 z-50 w-14 h-14 rounded-full text-white shadow-lg hover:shadow-xl transition-all flex items-center justify-center hover:scale-110"
            style={{ background: 'linear-gradient(135deg, #0077B6 0%, #00B4D8 100%)' }}
            title="Open Chat"
          >
            <MessageSquare size={24} />
          </motion.button>
        )}

        {/* Header with Glassmorphism */}
        <header className="backdrop-blur-md bg-white/70 border-b border-white/20 sticky top-0 z-30 shadow-lg">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.button 
                  onClick={() => navigate('/')}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:from-blue-600 hover:to-cyan-600 transition-all flex items-center gap-2 shadow-md"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={18} />
                  <span className="text-sm font-semibold">Home</span>
                </motion.button>
                <div className="h-8 w-px bg-gradient-to-b from-transparent via-blue-300 to-transparent" />
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 via-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/40 relative">
                    <Droplets size={26} className="text-white" />
                    <div className="absolute inset-0 rounded-2xl bg-white/20 backdrop-blur-xl" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                      Water Management
                    </h1>
                    <p className="text-sm text-gray-600 font-medium">Smart Infrastructure & Distribution Control</p>
                  </div>
                </div>
              </div>
              
              {/* Weather Widget */}
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-6"
              >
                <div className="backdrop-blur-md bg-white/60 rounded-2xl px-4 py-3 border border-white/40 shadow-lg">
                  <div className="flex items-center gap-3">
                    <Cloud size={24} className="text-blue-500" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold text-gray-800">{weather.temp}°C</span>
                        <span className="text-xs text-gray-600">{weather.condition}</span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-600 mt-1">
                        <span className="flex items-center gap-1">
                          <Droplets size={12} />
                          {weather.humidity}%
                        </span>
                        <span className="flex items-center gap-1">
                          <CloudRain size={12} />
                          {weather.precipitation}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse shadow-lg shadow-green-500/50" />
                  <span className="text-sm font-semibold text-green-600">System Online</span>
                </div>
              </motion.div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Hero KPI Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {heroStats.map((stat, index) => {
              const Icon = stat.icon
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, type: "spring", stiffness: 100 }}
                  className="relative backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/40 shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden group hover:-translate-y-1"
                >
                  {/* Background Gradient Orb */}
                  <div 
                    className="absolute -top-10 -right-10 w-32 h-32 rounded-full opacity-10 blur-2xl transition-all duration-500 group-hover:scale-150"
                    style={{ background: stat.color }}
                  />
                  
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <div 
                        className="p-3 rounded-2xl shadow-lg"
                        style={{ 
                          background: `linear-gradient(135deg, ${stat.color}15 0%, ${stat.color}30 100%)`,
                        }}
                      >
                        <Icon size={28} style={{ color: stat.color }} />
                      </div>
                      <div className="text-right">
                        <div className={`flex items-center gap-1 text-sm font-semibold ${stat.trendUp ? 'text-green-600' : 'text-orange-600'}`}>
                          {stat.trendUp ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                          {stat.trend}
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <p className="text-gray-600 text-sm font-medium mb-1">{stat.label}</p>
                        <div className="flex items-baseline gap-2">
                          <p className="text-4xl font-bold text-gray-900">{stat.value}</p>
                          {stat.unit && <span className="text-sm text-gray-500">{stat.unit}</span>}
                        </div>
                      </div>
                      
                      {/* Sparkline */}
                      <div className="pt-2">
                        <Sparkline data={stat.sparkline} color={stat.color} height={35} />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            {/* Interactive Map Section */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/40 shadow-xl h-full"
              >
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold mb-1">City Water Network</h2>
                      <p className="text-blue-100 text-sm">Real-time distribution monitoring</p>
                    </div>
                    <MapPin size={32} className="opacity-80" />
                  </div>
                </div>
                
                {/* Map Placeholder with Pins */}
                <div className="relative h-[400px] bg-gradient-to-br from-blue-100 to-cyan-100 overflow-hidden">
                  {/* Simulated Map Grid */}
                  <div className="absolute inset-0 opacity-20">
                    {[...Array(10)].map((_, i) => (
                      <div key={`h-${i}`} className="absolute w-full h-px bg-blue-300" style={{ top: `${i * 10}%` }} />
                    ))}
                    {[...Array(10)].map((_, i) => (
                      <div key={`v-${i}`} className="absolute h-full w-px bg-blue-300" style={{ left: `${i * 10}%` }} />
                    ))}
                  </div>
                  
                  {/* Zone Markers */}
                  {zones.map((zone, index) => {
                    const positions = [
                      { top: '20%', left: '30%' },
                      { top: '65%', left: '25%' },
                      { top: '35%', left: '70%' },
                      { top: '70%', left: '65%' }
                    ]
                    const pos = positions[index]
                    
                    return (
                      <motion.div
                        key={zone.name}
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.7 + index * 0.1, type: "spring" }}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
                        style={{ top: pos.top, left: pos.left }}
                      >
                        {/* Pulse Ring */}
                        <div className={`absolute inset-0 rounded-full animate-ping ${
                          zone.status === 'optimal' ? 'bg-green-400' :
                          zone.status === 'good' ? 'bg-blue-400' :
                          'bg-orange-400'
                        }`} style={{ animationDuration: '3s' }} />
                        
                        {/* Pin */}
                        <div className={`relative w-12 h-12 rounded-full flex items-center justify-center shadow-xl ${
                          zone.status === 'optimal' ? 'bg-green-500' :
                          zone.status === 'good' ? 'bg-blue-500' :
                          'bg-orange-500'
                        }`}>
                          <Droplets size={20} className="text-white" />
                        </div>
                        
                        {/* Tooltip */}
                        <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-all pointer-events-none z-10">
                          <div className="backdrop-blur-md bg-white/90 rounded-xl p-3 shadow-2xl border border-white/60 whitespace-nowrap">
                            <p className="font-bold text-gray-900 text-sm">{zone.name}</p>
                            <p className="text-xs text-gray-600 mt-1">Quality: {zone.quality}%</p>
                            <p className="text-xs text-gray-600">Pressure: {zone.pressure}%</p>
                          </div>
                        </div>
                      </motion.div>
                    )
                  })}
                  
                  {/* Legend */}
                  <div className="absolute bottom-4 right-4 backdrop-blur-md bg-white/80 rounded-xl p-4 shadow-lg border border-white/60">
                    <p className="text-xs font-bold text-gray-700 mb-2">Status Legend</p>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-xs">
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                        <span className="text-gray-600">Optimal</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                        <span className="text-gray-600">Good</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <div className="w-3 h-3 rounded-full bg-orange-500" />
                        <span className="text-gray-600">Maintenance</span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Live Activity Feed */}
            <div>
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/40 shadow-xl h-full"
              >
                <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold mb-1">Live Activity</h2>
                      <p className="text-cyan-100 text-sm">Real-time updates</p>
                    </div>
                    <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
                  </div>
                </div>
                
                <div className="p-4 space-y-3 max-h-[400px] overflow-y-auto">
                  <AnimatePresence>
                    {liveActivities.map((activity, index) => {
                      const Icon = activity.icon
                      return (
                        <motion.div
                          key={activity.id}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -20 }}
                          transition={{ delay: index * 0.1 }}
                          className="relative pl-6 pb-4 border-l-2 border-blue-200 last:border-0"
                        >
                          {/* Timeline Dot */}
                          <div className={`absolute left-0 top-1 -translate-x-1/2 w-4 h-4 rounded-full ${
                            activity.type === 'success' ? 'bg-green-500' :
                            activity.type === 'warning' ? 'bg-orange-500' :
                            activity.type === 'location' ? 'bg-blue-500' :
                            'bg-cyan-500'
                          } shadow-lg`}>
                            <div className="absolute inset-0 rounded-full animate-ping opacity-75" />
                          </div>
                          
                          <div className="backdrop-blur-sm bg-white/60 rounded-xl p-3 border border-white/60 hover:bg-white/80 transition-all">
                            <div className="flex items-start gap-2">
                              <Icon size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm text-gray-900 font-medium leading-tight">{activity.message}</p>
                                <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )
                    })}
                  </AnimatePresence>
                </div>
              </motion.div>
            </div>
          </div>

          {/* Circular Gauges Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="backdrop-blur-md bg-white/70 rounded-3xl p-8 border border-white/40 shadow-xl mb-8"
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">System Performance</h2>
                <p className="text-gray-600 text-sm">Real-time operational metrics</p>
              </div>
              <BarChart3 size={28} className="text-blue-500" />
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <CircularGauge value={94} label="Efficiency" color="#0077B6" />
              <CircularGauge value={87} label="Coverage" color="#2D6A4F" />
              <CircularGauge value={91} label="Optimization" color="#8B5CF6" />
              <CircularGauge value={78} label="Tank Levels" color="#FF9F1C" />
            </div>
          </motion.div>
          {/* Enhanced Zone Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {zones.map((zone, index) => (
              <motion.div
                key={zone.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.9 + index * 0.1, type: "spring" }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/40 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
                        <MapPin size={24} className="text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">{zone.name}</h3>
                        <p className="text-sm text-gray-600">Distribution Zone</p>
                      </div>
                    </div>
                    <StatusBadge status={zone.status} />
                  </div>
                  
                  {/* Metrics Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="backdrop-blur-sm bg-blue-50/50 rounded-2xl p-4 border border-blue-100">
                      <div className="flex items-center gap-2 mb-2">
                        <Droplets size={16} className="text-blue-600" />
                        <p className="text-xs text-gray-600 font-medium">Consumption</p>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">{zone.consumption}</p>
                    </div>
                    
                    <div className="backdrop-blur-sm bg-green-50/50 rounded-2xl p-4 border border-green-100">
                      <div className="flex items-center gap-2 mb-2">
                        <Shield size={16} className="text-green-600" />
                        <p className="text-xs text-gray-600 font-medium">Quality</p>
                      </div>
                      <p className="text-2xl font-bold text-gray-900">{zone.quality}%</p>
                    </div>
                  </div>
                  
                  {/* Progress Bars */}
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="text-gray-600 font-medium flex items-center gap-1">
                          <Activity size={12} />
                          Pressure Level
                        </span>
                        <span className="font-bold text-blue-600">{zone.pressure}%</span>
                      </div>
                      <div className="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div 
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${zone.pressure}%` }}
                          transition={{ delay: 1.2 + index * 0.1, duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="text-gray-600 font-medium flex items-center gap-1">
                          <TrendingUp size={12} />
                          Tank Level
                        </span>
                        <span className={`font-bold ${zone.tankLevel > 75 ? 'text-green-600' : zone.tankLevel > 50 ? 'text-orange-600' : 'text-red-600'}`}>
                          {zone.tankLevel}%
                        </span>
                      </div>
                      <div className="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div 
                          className={`h-full rounded-full ${
                            zone.tankLevel > 75 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                            zone.tankLevel > 50 ? 'bg-gradient-to-r from-orange-500 to-amber-500' :
                            'bg-gradient-to-r from-red-500 to-rose-500'
                          }`}
                          initial={{ width: 0 }}
                          animate={{ width: `${zone.tankLevel}%` }}
                          transition={{ delay: 1.3 + index * 0.1, duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Recent Actions with Enhanced Badges */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3 }}
            className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/40 shadow-xl"
          >
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-1">Recent Activity</h2>
                  <p className="text-purple-100 text-sm">Chat history with Water Agent</p>
                </div>
                <Clock size={28} className="opacity-80" />
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-3">
                {loadingHistory ? (
                  <div className="text-center py-8">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto mb-4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
                    </div>
                    <p className="text-gray-500 text-sm mt-4">Loading history...</p>
                  </div>
                ) : chatHistory.length === 0 ? (
                  <div className="text-center py-8">
                    <MessageSquare size={48} className="mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500 font-medium">No recent activity</p>
                    <p className="text-gray-400 text-sm mt-1">Start a conversation in the chat!</p>
                  </div>
                ) : (
                  chatHistory.slice(0, 5).map((item, index) => (
                    <motion.div
                      key={item.id || index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1.4 + index * 0.1 }}
                      className="backdrop-blur-sm bg-white/60 border border-white/60 rounded-2xl p-4 hover:bg-white/80 hover:border-blue-200 transition-all"
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-blue-100 text-blue-600">
                          <MessageSquare size={20} />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          {item.summary ? (
                            <div className="text-sm text-gray-900 mb-2 whitespace-pre-line">
                              {item.summary}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-900 font-medium mb-2 line-clamp-2">
                              {getQuerySummary(item.request)}
                            </p>
                          )}
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500 flex items-center gap-1">
                              <Clock size={11} />
                              {getRelativeTime(item.created_at)}
                            </span>
                            <span className="px-2 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200">
                              Completed
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default WaterAgentPage
