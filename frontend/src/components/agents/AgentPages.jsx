import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import WaterAgentPage from './WaterAgentPage'
import AgentChatBot from './AgentChatBot'
import { Flame, Wrench, Heart, DollarSign, Trash2, Home, MessageSquare } from 'lucide-react'

// Fire Agent Page Component
export const FireAgentPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <WaterAgentPageTemplate 
        agentType="fire"
        agentName="Fire & Emergency"
        icon={Flame}
        title="Fire & Emergency"
        subtitle="Response & Prevention Services"
        color="#f97316"
        accentColor="#fb923c"
        stats={[
          { label: 'Active Units', value: '24', color: '#f97316' },
          { label: 'Response Time', value: '3.2m', color: '#14b8a6' },
          { label: 'Drills Completed', value: '89', color: '#10b981' },
          { label: 'Equipment Status', value: '98%', color: '#f59e0b' },
        ]}
        zones={[
          { name: 'North Station', status: 'ready', units: '8', responseRate: 97 },
          { name: 'South Station', status: 'ready', units: '6', responseRate: 95 },
          { name: 'East Station', status: 'active', units: '5', responseRate: 98 },
          { name: 'West Station', status: 'ready', units: '5', responseRate: 96 },
        ]}
        recentActions={[
          { id: 1, action: 'Fire drill completed - North Station', status: 'success', time: '12 min ago' },
          { id: 2, action: 'Equipment maintenance finished', status: 'success', time: '45 min ago' },
          { id: 3, action: 'Emergency response - Industrial area', status: 'warning', time: '2 hours ago' },
          { id: 4, action: 'Training session scheduled', status: 'info', time: '3 hours ago' },
          { id: 5, action: 'Safety inspection passed', status: 'success', time: '5 hours ago' },
        ]}
      />
    </div>
  )
}

// Engineering Agent Page Component  
export const EngineeringAgentPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <WaterAgentPageTemplate 
        agentType="engineering"
        agentName="Engineering & Development"
        icon={Wrench}
        title="Engineering & Development"
        subtitle="Urban Infrastructure Management"
        color="#14b8a6"
        accentColor="#2dd4bf"
        stats={[
          { label: 'Active Projects', value: '34', color: '#14b8a6' },
          { label: 'Completion Rate', value: '89%', color: '#10b981' },
          { label: 'Pending Approvals', value: '12', color: '#f59e0b' },
          { label: 'Budget Usage', value: '72%', color: '#3b82f6' },
        ]}
        zones={[
          { name: 'Road Development', status: 'in-progress', projects: '12', progress: 65 },
          { name: 'Bridge Maintenance', status: 'optimal', projects: '8', progress: 92 },
          { name: 'Building Permits', status: 'active', projects: '9', progress: 78 },
          { name: 'Infrastructure Repair', status: 'in-progress', projects: '5', progress: 54 },
        ]}
        recentActions={[
          { id: 1, action: 'Road repair authorized - Main St', status: 'success', time: '8 min ago' },
          { id: 2, action: 'Building permit issued - Zone 4', status: 'success', time: '32 min ago' },
          { id: 3, action: 'Bridge inspection completed', status: 'info', time: '1 hour ago' },
          { id: 4, action: 'Project budget approved', status: 'success', time: '2 hours ago' },
          { id: 5, action: 'Site survey scheduled', status: 'info', time: '4 hours ago' },
        ]}
      />
    </div>
  )
}

// Health Agent Page Component
export const HealthAgentPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <WaterAgentPageTemplate 
        agentType="health"
        agentName="Health & Wellness"
        icon={Heart}
        title="Health & Wellness"
        subtitle="Public Health Services"
        color="#ec4899"
        accentColor="#f472b6"
        stats={[
          { label: 'Active Clinics', value: '18', color: '#ec4899' },
          { label: 'Daily Patients', value: '1.2K', color: '#14b8a6' },
          { label: 'Vaccinations', value: '456', color: '#10b981' },
          { label: 'Bed Availability', value: '78%', color: '#3b82f6' },
        ]}
        zones={[
          { name: 'North Health Center', status: 'operational', capacity: '145', utilization: 82 },
          { name: 'South Clinic', status: 'operational', capacity: '98', utilization: 65 },
          { name: 'East Medical Unit', status: 'busy', capacity: '120', utilization: 94 },
          { name: 'West Health Hub', status: 'operational', capacity: '87', utilization: 71 },
        ]}
        recentActions={[
          { id: 1, action: 'Vaccination drive completed - Zone A', status: 'success', time: '15 min ago' },
          { id: 2, action: 'Health screening scheduled', status: 'info', time: '40 min ago' },
          { id: 3, action: 'Emergency supplies restocked', status: 'success', time: '1 hour ago' },
          { id: 4, action: 'Medical staff training conducted', status: 'success', time: '3 hours ago' },
          { id: 5, action: 'Patient care quality review', status: 'info', time: '5 hours ago' },
        ]}
      />
    </div>
  )
}

// Finance Agent Page Component
export const FinanceAgentPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <WaterAgentPageTemplate 
        agentType="finance"
        agentName="Finance & Budget"
        icon={DollarSign}
        title="Finance & Budget"
        subtitle="Resource Allocation & Management"
        color="#f59e0b"
        accentColor="#fbbf24"
        stats={[
          { label: 'Budget Allocated', value: '$8.4M', color: '#f59e0b' },
          { label: 'Expenditure', value: '$6.1M', color: '#ec4899' },
          { label: 'Pending Payments', value: '24', color: '#3b82f6' },
          { label: 'Efficiency Score', value: '92%', color: '#10b981' },
        ]}
        zones={[
          { name: 'Department Budgets', status: 'on-track', allocated: '$3.2M', spent: 68 },
          { name: 'Infrastructure Fund', status: 'on-track', allocated: '$2.8M', spent: 72 },
          { name: 'Emergency Reserve', status: 'healthy', allocated: '$1.5M', spent: 23 },
          { name: 'Operations', status: 'on-track', allocated: '$0.9M', spent: 81 },
        ]}
        recentActions={[
          { id: 1, action: 'Budget review completed - Q1', status: 'success', time: '20 min ago' },
          { id: 2, action: 'Payment processed - Vendor #234', status: 'success', time: '1 hour ago' },
          { id: 3, action: 'Financial audit scheduled', status: 'info', time: '2 hours ago' },
          { id: 4, action: 'Budget reallocation approved', status: 'warning', time: '4 hours ago' },
          { id: 5, action: 'Expense report generated', status: 'info', time: '6 hours ago' },
        ]}
      />
    </div>
  )
}

// Sanitation Agent Page Component
export const SanitationAgentPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <WaterAgentPageTemplate 
        agentType="sanitation"
        agentName="Sanitation & Waste Management"
        icon={Trash2}
        title="Sanitation & Waste"
        subtitle="Waste Management Services"
        color="#8b5cf6"
        accentColor="#a78bfa"
        stats={[
          { label: 'Collection Routes', value: '42', color: '#8b5cf6' },
          { label: 'Daily Collection', value: '280T', color: '#14b8a6' },
          { label: 'Recycling Rate', value: '68%', color: '#10b981' },
          { label: 'Fleet Active', value: '35/38', color: '#3b82f6' },
        ]}
        zones={[
          { name: 'North Route', status: 'completed', tonnage: '72T', efficiency: 94 },
          { name: 'South Route', status: 'in-progress', tonnage: '65T', efficiency: 89 },
          { name: 'East Route', status: 'completed', tonnage: '81T', efficiency: 96 },
          { name: 'West Route', status: 'scheduled', tonnage: '62T', efficiency: 91 },
        ]}
        recentActions={[
          { id: 1, action: 'Route optimization completed', status: 'success', time: '18 min ago' },
          { id: 2, action: 'Recycling center update', status: 'info', time: '45 min ago' },
          { id: 3, action: 'Vehicle maintenance completed', status: 'success', time: '2 hours ago' },
          { id: 4, action: 'Special collection scheduled', status: 'info', time: '3 hours ago' },
          { id: 5, action: 'Waste audit conducted', status: 'success', time: '5 hours ago' },
        ]}
      />
    </div>
  )
}

// Reusable Template Component
const WaterAgentPageTemplate = ({ 
  agentType, 
  agentName, 
  icon: Icon, 
  title, 
  subtitle, 
  color, 
  accentColor, 
  stats, 
  zones, 
  recentActions 
}) => {
  const navigate = useNavigate()
  const [showChat, setShowChat] = useState(true)
  const [isChatMinimized, setIsChatMinimized] = useState(false)
  
  return (
    <>
      {/* Chatbot Sidebar */}
      {showChat && (
        <div className="fixed left-0 top-0 bottom-0 z-40">
          <AgentChatBot
            agentType={agentType}
            agentName={agentName}
            agentColor={color}
            onClose={() => setShowChat(false)}
            isMinimized={isChatMinimized}
            onToggleMinimize={() => setIsChatMinimized(!isChatMinimized)}
          />
        </div>
      )}

      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${showChat && !isChatMinimized ? 'ml-[320px]' : 'ml-0'}`}>
        {/* Floating Chat Toggle Button */}
        {!showChat && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            onClick={() => setShowChat(true)}
            className="fixed left-4 bottom-4 z-50 w-14 h-14 rounded-full text-white shadow-lg hover:shadow-xl transition-all flex items-center justify-center"
            style={{ backgroundColor: color }}
            title="Open Chat"
          >
            <MessageSquare size={24} />
          </motion.button>
        )}

      <header className="border-b border-gray-200 bg-white sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate('/')}
                className="p-2 rounded-lg hover:bg-gray-100 transition-all flex items-center gap-2 cursor-pointer"
                style={{ background: `${color}10`, color: color }}
              >
                <Home size={20} />
                <span className="text-sm font-medium">Home</span>
              </button>
              <div className="h-8 w-px bg-gray-200" />
              <div className="flex items-center gap-3">
                <div 
                  className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg"
                  style={{ 
                    background: `linear-gradient(135deg, ${color}, ${accentColor})`,
                    boxShadow: `0 4px 20px ${color}40`
                  }}
                >
                  <Icon size={24} className="text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
                  <p className="text-sm text-gray-500">{subtitle}</p>
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
          {stats.map((stat, index) => (
            <div
              key={stat.label}
              className="bg-white border-2 border-gray-100 rounded-2xl p-6 hover:shadow-lg transition-all"
              style={{ borderColor: `${stat.color}20` }}
            >
              <p className="text-gray-600 text-sm mb-1">{stat.label}</p>
              <p className="text-3xl font-bold" style={{ color: stat.color }}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Zones/Areas */}
          <div className="lg:col-span-2">
            <div className="bg-white border-2 border-gray-100 rounded-2xl overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900">Operations Overview</h2>
              </div>
              
              <div className="p-6 space-y-4">
                {zones.map((zone, index) => (
                  <div
                    key={zone.name}
                    className="p-5 rounded-xl border-2 hover:shadow-md transition-all"
                    style={{ 
                      background: `linear-gradient(to right, ${color}08, transparent)`,
                      borderColor: `${color}20`
                    }}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-gray-900">{zone.name}</h3>
                      <span 
                        className="px-3 py-1 rounded-full text-xs font-semibold text-white"
                        style={{ background: color }}
                      >
                        {zone.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500 mb-1">{Object.keys(zone)[2]}</p>
                        <p className="text-lg font-bold text-gray-900">{Object.values(zone)[2]}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Performance</p>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full"
                              style={{ 
                                width: `${Object.values(zone)[3]}%`,
                                background: `linear-gradient(to right, ${color}, ${accentColor})`
                              }}
                            />
                          </div>
                          <span className="text-sm font-bold" style={{ color: color }}>{Object.values(zone)[3]}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div>
            <div className="bg-white border-2 border-gray-100 rounded-2xl overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
              </div>
              
              <div className="p-4 space-y-3">
                {recentActions.map((activity) => (
                  <div
                    key={activity.id}
                    className="p-4 rounded-xl border hover:shadow-sm transition-all"
                    style={{ 
                      background: `${color}05`,
                      borderColor: `${color}15`
                    }}
                  >
                    <p className="text-sm text-gray-900 mb-1">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </>
  )
}