import React from 'react'
import { motion } from 'framer-motion'
import { Droplets, Activity, TrendingUp, CheckCircle, Clock, MapPin, Home } from 'lucide-react'

const WaterAgentPage = () => {
  const stats = [
    { label: 'Active Pipelines', value: '487', icon: Activity, color: '#3b82f6' },
    { label: 'Daily Consumption', value: '2.4M L', icon: TrendingUp, color: '#14b8a6' },
    { label: 'Quality Tests', value: '156', icon: CheckCircle, color: '#10b981' },
    { label: 'Response Time', value: '1.2s', icon: Clock, color: '#f59e0b' },
  ]

  const recentActions = [
    { id: 1, action: 'Pipeline inspection completed - Sector 7', status: 'success', time: '5 min ago' },
    { id: 2, action: 'Water quality test passed - Zone A', status: 'success', time: '23 min ago' },
    { id: 3, action: 'Leak detected and repaired - Main St', status: 'warning', time: '1 hour ago' },
    { id: 4, action: 'Pressure monitoring initiated', status: 'info', time: '2 hours ago' },
    { id: 5, action: 'Supply optimization completed', status: 'success', time: '3 hours ago' },
  ]

  const zones = [
    { name: 'North Zone', status: 'optimal', consumption: '650K L', quality: 98 },
    { name: 'South Zone', status: 'optimal', consumption: '720K L', quality: 97 },
    { name: 'East Zone', status: 'good', consumption: '580K L', quality: 96 },
    { name: 'West Zone', status: 'optimal', consumption: '450K L', quality: 99 },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <a 
                href="#" 
                className="p-2 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition-all flex items-center gap-2"
              >
                <Home size={20} />
                <span className="text-sm font-medium">Home</span>
              </a>
              <div className="h-8 w-px bg-gray-200" />
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <Droplets size={24} className="text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Water Management</h1>
                  <p className="text-sm text-gray-500">Infrastructure & Distribution Control</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm font-medium text-green-600">Online</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white border-2 border-gray-100 rounded-2xl p-6 hover:border-blue-200 hover:shadow-lg transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div 
                    className="p-3 rounded-xl"
                    style={{ 
                      background: `${stat.color}15`,
                    }}
                  >
                    <Icon size={24} style={{ color: stat.color }} />
                  </div>
                </div>
                <p className="text-gray-600 text-sm mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </motion.div>
            )
          })}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Zone Status */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white border-2 border-gray-100 rounded-2xl overflow-hidden"
            >
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-1">Distribution Zones</h2>
                <p className="text-sm text-gray-500">Real-time monitoring across all zones</p>
              </div>
              
              <div className="p-6">
                <div className="space-y-4">
                  {zones.map((zone, index) => (
                    <motion.div
                      key={zone.name}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      className="p-5 rounded-xl bg-gradient-to-r from-blue-50 to-transparent border border-blue-100 hover:shadow-md transition-all"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <MapPin size={20} className="text-blue-600" />
                          <h3 className="font-bold text-gray-900">{zone.name}</h3>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          zone.status === 'optimal' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {zone.status}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Consumption</p>
                          <p className="text-lg font-bold text-gray-900">{zone.consumption}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Quality Score</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-blue-500 to-green-500"
                                style={{ width: `${zone.quality}%` }}
                              />
                            </div>
                            <span className="text-sm font-bold text-gray-900">{zone.quality}%</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>

          {/* Recent Activity */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white border-2 border-gray-100 rounded-2xl overflow-hidden"
            >
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-1">Recent Activity</h2>
                <p className="text-sm text-gray-500">Latest actions</p>
              </div>
              
              <div className="p-4 space-y-3">
                {recentActions.map((activity, index) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="p-4 rounded-xl bg-gray-50 border border-gray-100 hover:bg-blue-50 hover:border-blue-200 transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        activity.status === 'success' ? 'bg-green-500' :
                        activity.status === 'warning' ? 'bg-yellow-500' :
                        'bg-blue-500'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 mb-1">{activity.action}</p>
                        <p className="text-xs text-gray-500">{activity.time}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-8 bg-gradient-to-br from-blue-50 to-white border-2 border-blue-100 rounded-2xl p-6"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-6">Performance Metrics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">System Efficiency</span>
                <span className="font-bold text-blue-600">94%</span>
              </div>
              <div className="h-3 bg-white rounded-full overflow-hidden border border-blue-200">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                  initial={{ width: 0 }}
                  animate={{ width: '94%' }}
                  transition={{ duration: 1, delay: 0.9 }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Network Coverage</span>
                <span className="font-bold text-green-600">87%</span>
              </div>
              <div className="h-3 bg-white rounded-full overflow-hidden border border-green-200">
                <motion.div
                  className="h-full bg-gradient-to-r from-green-500 to-green-600"
                  initial={{ width: 0 }}
                  animate={{ width: '87%' }}
                  transition={{ duration: 1, delay: 1.0 }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Resource Optimization</span>
                <span className="font-bold text-purple-600">91%</span>
              </div>
              <div className="h-3 bg-white rounded-full overflow-hidden border border-purple-200">
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-500 to-purple-600"
                  initial={{ width: 0 }}
                  animate={{ width: '91%' }}
                  transition={{ duration: 1, delay: 1.1 }}
                />
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default WaterAgentPage
