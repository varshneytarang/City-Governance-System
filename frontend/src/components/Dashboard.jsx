import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import AgentConstellationInteractive from './AgentConstellationInteractive'
import { Activity, Clock, CheckCircle, AlertTriangle, TrendingUp, Settings, Home } from 'lucide-react'

const Dashboard = ({ reducedMotion = false }) => {
  const navigate = useNavigate()
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h')
  const [hoveredStat, setHoveredStat] = useState(null)

  const stats = [
    { 
      label: 'Active Tasks', 
      value: '2,847', 
      change: '+12%', 
      positive: true, 
      icon: Activity,
      color: '#3b82f6'
    },
    { 
      label: 'Avg Response Time', 
      value: '1.2s', 
      change: '-8%', 
      positive: true, 
      icon: Clock,
      color: '#14b8a6'
    },
    { 
      label: 'Completed Today', 
      value: '1,234', 
      change: '+23%', 
      positive: true, 
      icon: CheckCircle,
      color: '#10b981'
    },
    { 
      label: 'Alerts', 
      value: '3', 
      change: '-45%', 
      positive: true, 
      icon: AlertTriangle,
      color: '#f59e0b'
    },
  ]

  const recentActivity = [
    { id: 1, agent: 'Water', action: 'Pipeline inspection completed', time: '2 min ago', status: 'success' },
    { id: 2, agent: 'Fire', action: 'Emergency drill scheduled', time: '15 min ago', status: 'info' },
    { id: 3, agent: 'Health', action: 'Vaccination drive initiated', time: '1 hour ago', status: 'success' },
    { id: 4, agent: 'Finance', action: 'Budget review pending', time: '2 hours ago', status: 'warning' },
    { id: 5, agent: 'Engineering', action: 'Road repair authorized', time: '3 hours ago', status: 'success' },
  ]

  // Sliding animation variants
  const slideDownVariants = {
    hidden: { opacity: 0, y: -60 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        type: 'spring',
        stiffness: 100,
        damping: 15,
        mass: 0.8
      }
    }
  }

  const slideUpVariants = {
    hidden: { opacity: 0, y: 60 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        type: 'spring',
        stiffness: 100,
        damping: 15,
        mass: 0.8
      }
    }
  }

  const slideLeftVariants = {
    hidden: { opacity: 0, x: -60 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { 
        type: 'spring',
        stiffness: 100,
        damping: 15
      }
    }
  }

  const slideRightVariants = {
    hidden: { opacity: 0, x: 60 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { 
        type: 'spring',
        stiffness: 100,
        damping: 15
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#1e3a5f] to-[#0f172a] relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute bottom-0 left-0 w-[600px] h-[600px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%)',
            filter: 'blur(90px)',
          }}
          animate={{
            x: [0, -40, 0],
            y: [0, -50, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      {/* Header */}
      <motion.header 
        className="border-b border-white/5 bg-[#0a0e1a]/90 backdrop-blur-xl sticky top-0 z-50 shadow-2xl"
        variants={slideDownVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.button 
                onClick={() => navigate('/')}
                className="p-2 rounded-lg bg-gradient-to-br from-[#1e3a5f] to-[#2c5282] text-gray-300 hover:text-white transition-all flex items-center gap-2 border border-white/10 hover:border-[#d4af37]/50"
                title="Back to Home"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <Home size={20} />
                <span className="text-sm font-medium">Home</span>
              </motion.button>
              <div className="h-8 w-px bg-white/10" />
              <div>
                <motion.h1 
                  className="text-2xl font-bold text-white mb-1"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                >
                  Agent Dashboard
                </motion.h1>
                <motion.p 
                  className="text-sm text-gray-400"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
                >
                  Real-time system monitoring & control
                </motion.p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Timeframe selector */}
              <div className="flex gap-2 bg-[#1e3a5f]/30 rounded-lg p-1 border border-white/5">
                {['1h', '24h', '7d', '30d'].map((tf, index) => (
                  <motion.button
                    key={tf}
                    onClick={() => setSelectedTimeframe(tf)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all relative ${
                      selectedTimeframe === tf
                        ? 'text-white'
                        : 'text-gray-400 hover:text-white'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                  >
                    {selectedTimeframe === tf && (
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-[#3b82f6] to-[#2563eb] rounded-md"
                        layoutId="timeframeBackground"
                        style={{ boxShadow: '0 4px 20px rgba(59, 130, 246, 0.5)' }}
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      />
                    )}
                    <span className="relative z-10">{tf}</span>
                  </motion.button>
                ))}
              </div>

              <motion.button 
                className="p-2 rounded-lg bg-gradient-to-br from-[#1e3a5f] to-[#2c5282] text-gray-300 hover:text-white transition-all border border-white/10 hover:border-[#d4af37]/50"
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Settings size={20} />
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="max-w-7xl mx-auto px-6 py-8 relative z-10">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            const isHovered = hoveredStat === index
            return (
              <motion.div
                key={stat.label}
                variants={slideUpVariants}
                initial="hidden"
                animate="visible"
                transition={{ delay: 0.7 + index * 0.1 }}
                onMouseEnter={() => setHoveredStat(index)}
                onMouseLeave={() => setHoveredStat(null)}
                className="bg-gradient-to-br from-[#1e3a5f]/40 to-[#0a0e1a]/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all duration-300 group cursor-pointer relative overflow-hidden"
                whileHover={{ 
                  scale: 1.05, 
                  y: -8,
                  boxShadow: `0 20px 40px ${stat.color}40`,
                }}
              >
                {/* Glow effect on hover */}
                <motion.div
                  className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{
                    background: `radial-gradient(circle at 50% 0%, ${stat.color}15, transparent 70%)`,
                  }}
                />
                
                <div className="flex items-start justify-between mb-4 relative z-10">
                  <motion.div 
                    className="p-3 rounded-xl relative"
                    style={{ 
                      background: `${stat.color}20`,
                      boxShadow: isHovered ? `0 8px 30px ${stat.color}50` : `0 4px 20px ${stat.color}30`
                    }}
                    whileHover={{ rotate: 360, scale: 1.1 }}
                    transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                  >
                    <Icon size={24} style={{ color: stat.color }} />
                  </motion.div>
                  <motion.div
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                      stat.positive ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}
                    whileHover={{ scale: 1.1, y: -2 }}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.8 + index * 0.1, type: 'spring', stiffness: 300 }}
                  >
                    {stat.change}
                  </motion.div>
                </div>
                <div className="relative z-10">
                  <motion.p 
                    className="text-gray-400 text-sm mb-1"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.9 + index * 0.1 }}
                  >
                    {stat.label}
                  </motion.p>
                  <motion.p 
                    className="text-3xl font-bold text-white"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 + index * 0.1, type: 'spring' }}
                  >
                    {stat.value}
                  </motion.p>
                </div>
                
                {/* Trend indicator */}
                <motion.div 
                  className="mt-3 pt-3 border-t border-white/5 flex items-center gap-2 relative z-10"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.1 + index * 0.1 }}
                >
                  <TrendingUp size={14} className="text-green-400" />
                  <span className="text-xs text-gray-500">vs last period</span>
                </motion.div>

                {/* Shimmer effect */}
                {isHovered && (
                  <motion.div
                    className="absolute inset-0 -translate-x-full"
                    style={{
                      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    }}
                    animate={{ x: ['0%', '200%'] }}
                    transition={{ duration: 1.5, ease: 'easeInOut' }}
                  />
                )}
              </motion.div>
            )
          })}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agent Constellation - Takes 2 columns */}
          <div className="lg:col-span-2">
            <motion.div
              variants={slideLeftVariants}
              initial="hidden"
              animate="visible"
              transition={{ delay: 1.2 }}
              className="bg-gradient-to-br from-[#1e3a5f]/40 to-[#0a0e1a]/60 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden hover:border-white/20 transition-all duration-300 shadow-2xl group"
              whileHover={{ scale: 1.01, y: -4 }}
            >
              <div className="p-6 border-b border-white/10 relative overflow-hidden">
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-[#3b82f6]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                  initial={false}
                />
                <motion.h2 
                  className="text-xl font-bold text-white mb-1 relative z-10"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.3 }}
                >
                  Agent Network
                </motion.h2>
                <motion.p 
                  className="text-sm text-gray-400 relative z-10"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.4 }}
                >
                  Live coordination & monitoring
                </motion.p>
              </div>
              
              {/* Constellation - Adjusted for dashboard */}
              <motion.div 
                className="relative" 
                style={{ height: '600px' }}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.5, type: 'spring', stiffness: 100 }}
              >
                <AgentConstellationInteractive reducedMotion={reducedMotion} />
              </motion.div>
            </motion.div>
          </div>

          {/* Recent Activity - Takes 1 column */}
          <div>
            <motion.div
              variants={slideRightVariants}
              initial="hidden"
              animate="visible"
              transition={{ delay: 1.2 }}
              className="bg-gradient-to-br from-[#1e3a5f]/40 to-[#0a0e1a]/60 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden hover:border-white/20 transition-all duration-300 shadow-2xl group"
              whileHover={{ scale: 1.01, y: -4 }}
            >
              <div className="p-6 border-b border-white/10 relative overflow-hidden">
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-[#d4af37]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
                  initial={false}
                />
                <motion.h2 
                  className="text-xl font-bold text-white mb-1 relative z-10"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.3 }}
                >
                  Recent Activity
                </motion.h2>
                <motion.p 
                  className="text-sm text-gray-400 relative z-10"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.4 }}
                >
                  Latest agent actions
                </motion.p>
              </div>
              
              <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
                {recentActivity.map((activity, index) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: 40 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ 
                      delay: 1.5 + index * 0.1,
                      type: 'spring',
                      stiffness: 150,
                      damping: 15
                    }}
                    className="p-4 rounded-xl bg-gradient-to-br from-[#1e3a5f]/30 to-[#0a0e1a]/50 border border-white/5 hover:border-white/20 transition-all group/item cursor-pointer relative overflow-hidden"
                    whileHover={{ 
                      scale: 1.02, 
                      x: 4,
                      boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
                    }}
                  >
                    {/* Hover glow */}
                    <motion.div
                      className="absolute inset-0 opacity-0 group-hover/item:opacity-100 transition-opacity"
                      style={{
                        background: activity.status === 'success' 
                          ? 'radial-gradient(circle at top right, rgba(34, 197, 94, 0.1), transparent 70%)'
                          : activity.status === 'warning'
                          ? 'radial-gradient(circle at top right, rgba(251, 191, 36, 0.1), transparent 70%)'
                          : 'radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent 70%)',
                      }}
                    />
                    
                    <div className="flex items-start justify-between mb-2 relative z-10">
                      <div className="flex items-center gap-2">
                        <motion.div 
                          className={`w-2 h-2 rounded-full ${
                            activity.status === 'success' ? 'bg-green-400' :
                            activity.status === 'warning' ? 'bg-yellow-400' :
                            'bg-blue-400'
                          }`}
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        />
                        <span className="text-sm font-semibold text-white">{activity.agent}</span>
                      </div>
                      <motion.span 
                        className="text-xs text-gray-500"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.6 + index * 0.1 }}
                      >
                        {activity.time}
                      </motion.span>
                    </div>
                    <p className="text-sm text-gray-400 pl-4 relative z-10">{activity.action}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* System Health - Full Width */}
        <motion.div
          variants={slideDownVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 1.8 }}
          className="mt-8 bg-gradient-to-br from-[#1e3a5f]/40 to-[#0a0e1a]/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all duration-300 shadow-2xl group relative overflow-hidden"
          whileHover={{ scale: 1.01, y: -4 }}
        >
          {/* Background glow */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-br from-[#3b82f6]/5 via-transparent to-[#d4af37]/5 opacity-0 group-hover:opacity-100 transition-opacity"
            initial={false}
          />

          <div className="flex items-center justify-between mb-6 relative z-10">
            <div>
              <motion.h2 
                className="text-xl font-bold text-white mb-1"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.9 }}
              >
                System Health
              </motion.h2>
              <motion.p 
                className="text-sm text-gray-400"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 2.0 }}
              >
                Overall performance metrics
              </motion.p>
            </div>
            <motion.div 
              className="flex items-center gap-2"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 2.1, type: 'spring', stiffness: 200 }}
            >
              <motion.div 
                className="w-3 h-3 rounded-full bg-green-400"
                animate={{ 
                  scale: [1, 1.3, 1],
                  opacity: [1, 0.7, 1]
                }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <span className="text-sm font-medium text-green-400">All Systems Operational</span>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
            {[
              { label: 'CPU Usage', value: 42, color: 'from-blue-500 to-blue-600', delay: 2.2 },
              { label: 'Memory', value: 67, color: 'from-emerald-500 to-emerald-600', delay: 2.3 },
              { label: 'Network', value: 23, color: 'from-purple-500 to-purple-600', delay: 2.4 }
            ].map((metric, index) => (
              <motion.div 
                key={metric.label}
                className="space-y-3 p-4 rounded-xl bg-gradient-to-br from-[#1e3a5f]/20 to-transparent border border-white/5 hover:border-white/10 transition-all group/metric"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: metric.delay, type: 'spring' }}
                whileHover={{ scale: 1.02, y: -2 }}
              >
                <div className="flex items-center justify-between text-sm">
                  <motion.span 
                    className="text-gray-400"
                    whileHover={{ color: '#ffffff' }}
                  >
                    {metric.label}
                  </motion.span>
                  <motion.span 
                    className="font-semibold text-white"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: metric.delay + 0.2 }}
                  >
                    {metric.value}%
                  </motion.span>
                </div>
                <div className="h-2.5 bg-[#0a0e1a]/50 rounded-full overflow-hidden border border-white/5">
                  <motion.div
                    className={`h-full bg-gradient-to-r ${metric.color} relative origin-left`}
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: metric.value / 100 }}
                    transition={{ 
                      duration: 1.5, 
                      delay: metric.delay + 0.3,
                      type: 'spring',
                      stiffness: 100
                    }}
                    style={{
                      boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)',
                      width: '100%'
                    }}
                  >
                    {/* Animated shimmer */}
                    <motion.div
                      className="absolute inset-0"
                      style={{
                        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                      }}
                      animate={{ x: ['-100%', '200%'] }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                    />
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Custom Scrollbar Styles */}
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  )
}

export default Dashboard
