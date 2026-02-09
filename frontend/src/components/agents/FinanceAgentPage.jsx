import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  DollarSign, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home, MessageSquare,
  Users, CreditCard, AlertCircle, Phone, PieChart, Wallet, Landmark,
  TrendingDown, Receipt, Award, FileText, Target, BarChart3, Coins, LineChart
} from 'lucide-react'
import AgentChatBot from './AgentChatBot'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const FinanceAgentPage = () => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [chatHistory, setChatHistory] = useState([])
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState(null)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])
  
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/agents/finance/history?limit=10`)
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
      label: 'Annual Budget', 
      value: '$45.2M', 
      trend: '+2.1M',
      trendUp: true,
      icon: Landmark,
      color: '#3b82f6',
      sparkline: [42.5, 43.0, 43.5, 44.0, 44.3, 44.8, 45.2],
      subtitle: 'Current fiscal year'
    },
    { 
      label: 'Expenses MTD', 
      value: '$3.8M', 
      trend: '-5%',
      trendUp: true,
      icon: Receipt,
      color: '#8b5cf6',
      sparkline: [4.2, 4.1, 4.0, 3.9, 3.85, 3.82, 3.8],
      subtitle: 'Under budget target'
    },
    { 
      label: 'Revenue Collected', 
      value: '$42.1M', 
      target: 45.2,
      trend: '93%',
      trendUp: true,
      icon: Coins,
      color: '#f59e0b',
      sparkline: [35, 37, 38.5, 39.8, 40.5, 41.2, 42.1],
      subtitle: 'Tax & fees collected'
    },
    { 
      label: 'Budget Efficiency', 
      value: '94%', 
      trend: '+3%',
      trendUp: true,
      icon: PieChart,
      color: '#10b981',
      sparkline: [88, 89, 91, 92, 92, 93, 94],
      subtitle: 'Optimal allocation'
    },
  ]

  const budgetCategories = [
    { 
      id: 1,
      name: 'Infrastructure',
      icon: Landmark,
      allocated: 15800000,
      spent: 12600000,
      remaining: 3200000,
      percentage: 79.7,
      status: 'on-track',
      projects: 24,
      color: '#3b82f6',
      trend: '+2.1%',
      forecast: 'Under budget',
      breakdown: { 
        labor: 7200000, 
        materials: 4800000, 
        equipment: 600000 
      }
    },
    { 
      id: 2,
      name: 'Public Services',
      icon: Users,
      allocated: 12500000,
      spent: 11900000,
      remaining: 600000,
      percentage: 95.2,
      status: 'caution',
      projects: 18,
      color: '#8b5cf6',
      trend: '+5.7%',
      forecast: 'Monitoring required',
      breakdown: { 
        salaries: 8400000, 
        operations: 2900000, 
        supplies: 600000 
      }
    },
    { 
      id: 3,
      name: 'Emergency Services',
      icon: CreditCard,
      allocated: 9200000,
      spent: 7100000,
      remaining: 2100000,
      percentage: 77.2,
      status: 'on-track',
      projects: 12,
      color: '#f59e0b',
      trend: '-1.3%',
      forecast: 'Ahead of schedule',
      breakdown: { 
        personnel: 5200000, 
        equipment: 1500000, 
        training: 400000 
      }
    },
    { 
      id: 4,
      name: 'Administration',
      icon: FileText,
      allocated: 7700000,
      spent: 6400000,
      remaining: 1300000,
      percentage: 83.1,
      status: 'on-track',
      projects: 8,
      color: '#10b981',
      trend: '-2.8%',
      forecast: 'Within target',
      breakdown: { 
        payroll: 4800000, 
        technology: 1200000, 
        facilities: 400000 
      }
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
            <span className="text-xs text-gray-500">${(value/1000000).toFixed(1)}M</span>
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
      <div className={`min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 transition-all duration-300 ${
        showChat && !isChatMinimized ? 'ml-[420px]' : 'ml-0'
      }`}>
        {/* Animated financial pattern watermark */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none">
          <svg className="w-full h-full" viewBox="0 0 1200 800">
            <motion.path
              d="M100,400 L300,350 L500,380 L700,320 L900,360 L1100,310"
              stroke="#3b82f6"
              strokeWidth="4"
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
              agentType="finance"
              agentName="Finance Department"
              agentColor="#3b82f6"
              onClose={() => setShowChat(false)}
              isMinimized={isChatMinimized}
              onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
            />
          </div>
        )}

        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="sticky top-0 z-30 backdrop-blur-xl bg-white/70 border-b border-blue-200/50 shadow-lg"
        >
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.button
                  onClick={() => navigate('/')}
                  className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 text-white hover:shadow-lg transition-all"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Home size={20} />
                </motion.button>
                <div>
                  <div className="flex items-center gap-3">
                    <DollarSign className="text-blue-600" size={28} />
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                      Finance Department
                    </h1>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Budget Management & Financial Operations</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/80 backdrop-blur border border-blue-200">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-gray-700">Fiscal Health: Good</span>
                </div>

                {!showChat && (
                  <motion.button
                    onClick={() => setShowChat(true)}
                    className="p-2 rounded-xl bg-blue-500 text-white hover:bg-blue-600 transition-all"
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
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  
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

          {/* Budget Categories Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="backdrop-blur-md bg-white/70 rounded-3xl overflow-hidden border border-white/60 shadow-xl"
              >
                <div className="bg-gradient-to-r from-blue-500 to-indigo-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold mb-1">Budget Allocation</h2>
                      <p className="text-blue-100 text-sm">Departmental spending & forecasts</p>
                    </div>
                    <BarChart3 size={32} className="opacity-80" />
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  {budgetCategories.map((category, index) => (
                    <motion.div
                      key={category.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="group relative"
                    >
                      <div className="backdrop-blur-sm bg-white/60 border border-white/80 rounded-2xl p-5 hover:bg-white/90 hover:shadow-lg transition-all cursor-pointer"
                        onClick={() => setSelectedCategory(category.id === selectedCategory ? null : category.id)}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <div className="p-2 rounded-xl" style={{ 
                                background: `linear-gradient(135deg, ${category.color}20, ${category.color}40)` 
                              }}>
                                <category.icon size={20} style={{ color: category.color }} />
                              </div>
                              <h3 className="text-lg font-bold text-gray-900">{category.name}</h3>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-600">
                              <span>Allocated: {formatCurrency(category.allocated)}</span>
                              <span>•</span>
                              <span>Spent: {formatCurrency(category.spent)}</span>
                            </div>
                          </div>

                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            category.status === 'on-track' ? 'bg-green-100 text-green-700 border border-green-300' :
                            category.status === 'caution' ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' :
                            'bg-red-100 text-red-700 border border-red-300'
                          }`}>
                            {category.forecast}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <div className="flex items-center justify-center">
                            <RadialGauge 
                              value={category.spent} 
                              max={category.allocated} 
                              size={90}
                              color={category.percentage > 90 ? '#f59e0b' : category.color}
                              label="Budget Used"
                            />
                          </div>

                          <div className="col-span-2 grid grid-cols-2 gap-3">
                            <div className="bg-blue-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <Wallet size={16} className="text-blue-600" />
                                <p className="text-xs font-medium text-gray-600">Remaining</p>
                              </div>
                              <p className="text-xl font-bold text-gray-900">{formatCurrency(category.remaining)}</p>
                            </div>

                            <div className="bg-purple-50 rounded-xl p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <FileText size={16} className="text-purple-600" />
                                <p className="text-xs font-medium text-gray-600">Projects</p>
                              </div>
                              <p className="text-xl font-bold text-gray-900">{category.projects}</p>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 flex-wrap">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors"
                          >
                            <BarChart3 size={14} />
                            View Report
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-500 text-white text-sm font-medium hover:bg-indigo-600 transition-colors"
                          >
                            <Receipt size={14} />
                            Transactions
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-purple-500 text-white text-sm font-medium hover:bg-purple-600 transition-colors"
                          >
                            <LineChart size={14} />
                            Forecast
                          </motion.button>
                        </div>

                        <AnimatePresence>
                          {selectedCategory === category.id && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="mt-4 pt-4 border-t border-gray-200"
                            >
                              <div className="grid grid-cols-3 gap-4">
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Labor Costs</p>
                                  <p className="text-lg font-bold text-gray-900">
                                    {formatCurrency(category.breakdown.labor)}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Materials/Operations</p>
                                  <p className="text-lg font-bold text-gray-900">
                                    {formatCurrency(category.breakdown.materials || category.breakdown.operations)}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs font-medium text-gray-600 mb-2">Equipment/Other</p>
                                  <p className="text-lg font-bold text-gray-900">
                                    {formatCurrency(category.breakdown.equipment || category.breakdown.supplies || category.breakdown.training || category.breakdown.technology || category.breakdown.facilities)}
                                  </p>
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
                <div className="bg-gradient-to-r from-indigo-500 to-blue-500 p-6 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold mb-1">Recent Activity</h2>
                      <p className="text-indigo-100 text-sm">Financial queries</p>
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
                        className="backdrop-blur-sm bg-white/80 border border-blue-200 rounded-2xl p-4 hover:bg-white hover:shadow-md transition-all"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-blue-500 to-indigo-500 text-white">
                            <DollarSign size={20} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            {item.summary ? (
                              <div className="text-sm text-gray-900 mb-2 whitespace-pre-line leading-relaxed">
                                {item.summary}
                              </div>
                            ) : (
                              <p className="text-sm text-gray-900 mb-2 line-clamp-2">
                                Financial query processed
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

          {/* Financial Analytics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="backdrop-blur-md bg-white/70 rounded-3xl p-6 border border-white/60 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 text-white">
                  <Target size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Quarterly Goals</h3>
                  <p className="text-xs text-gray-600">Budget targets</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Revenue Collection</span>
                  <span className="text-xl font-bold text-blue-600">93%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Budget Efficiency</span>
                  <span className="text-xl font-bold text-green-600">94%</span>
                </div>
                <div className="mt-4 p-3 bg-blue-50 rounded-xl">
                  <p className="text-xs text-blue-800">
                    <span className="font-semibold">Status:</span> On track to meet all quarterly targets
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
                <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 text-white">
                  <Coins size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Cash Flow</h3>
                  <p className="text-xs text-gray-600">Monthly trends</p>
                </div>
              </div>
              <div className="flex items-center justify-center">
                <RadialGauge 
                  value={42.1} 
                  max={45.2} 
                  size={140}
                  color="#f59e0b"
                  label="Revenue vs Budget"
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
                <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 text-white">
                  <Award size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Fiscal Performance</h3>
                  <p className="text-xs text-gray-600">Rating metrics</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Credit Rating</span>
                  <span className="text-lg font-semibold text-green-600">AA+</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Audit Score</span>
                  <span className="text-lg font-semibold text-green-600">98/100</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Compliance</span>
                  <span className="text-lg font-semibold text-green-600">100%</span>
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-xl">
                  <p className="text-xs text-green-800 font-semibold">
                    Excellent fiscal health - Above industry standard
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

export default FinanceAgentPage
