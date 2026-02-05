import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Droplets, Flame, Wrench, Heart, DollarSign, Trash2, Network } from 'lucide-react'

const agents = [
  { id: 'water', name: 'Water', icon: Droplets, color: '#3b82f6', description: 'Infrastructure Management' },
  { id: 'fire', name: 'Fire', icon: Flame, color: '#f97316', description: 'Emergency Response' },
  { id: 'engineering', name: 'Engineering', icon: Wrench, color: '#14b8a6', description: 'Urban Development' },
  { id: 'health', name: 'Health', icon: Heart, color: '#ec4899', description: 'Public Wellness' },
  { id: 'finance', name: 'Finance', icon: DollarSign, color: '#f59e0b', description: 'Resource Allocation' },
  { id: 'sanitation', name: 'Sanitation', icon: Trash2, color: '#8b5cf6', description: 'Waste Management' },
]

const AgentConstellation = ({ reducedMotion = false }) => {
  const [ref, inView] = useInView({ threshold: 0.2, triggerOnce: true })
  const [hoveredAgent, setHoveredAgent] = useState(null)

  return (
    <section 
      ref={ref} 
      className="relative py-24 px-6 bg-white overflow-hidden"
    >
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-[0.03]">
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, #1e3a5f 1.5px, transparent 0)',
            backgroundSize: '48px 48px'
          }}
        />
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold font-heading text-gov-navy mb-3">
            Departmental Ecosystem
          </h2>
          <p className="text-gov-darkBlue/70 text-lg">
            Six specialized agents coordinated by intelligent hub
          </p>
        </motion.div>

        {/* Agent Grid */}
        <div className="relative">
          {/* Central Hub */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={inView ? { scale: 1, opacity: 1 } : {}}
            transition={{ type: 'spring', stiffness: 200, delay: 0.3 }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20"
          >
            <div className="w-28 h-28 rounded-2xl bg-gradient-to-br from-gov-blue to-gov-darkBlue shadow-2xl flex items-center justify-center relative overflow-hidden group cursor-pointer">
              <div className="absolute inset-0 bg-gradient-to-tr from-white/20 to-transparent" />
              <Network size={48} className="text-white relative z-10" />
              
              {!reducedMotion && (
                <motion.div
                  className="absolute inset-0 bg-white/20"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                  style={{ background: 'conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%)' }}
                />
              )}
            </div>
            <p className="text-center mt-3 font-semibold text-gov-navy text-sm">Coordinator</p>
          </motion.div>

          {/* Agents in hexagonal pattern */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-12 relative">
            {agents.map((agent, index) => {
              const Icon = agent.icon
              const isHovered = hoveredAgent === agent.id
              
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 40, scale: 0.8 }}
                  animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
                  transition={{ 
                    duration: 0.6, 
                    delay: 0.5 + index * 0.1,
                    type: 'spring',
                    stiffness: 150
                  }}
                  onMouseEnter={() => setHoveredAgent(agent.id)}
                  onMouseLeave={() => setHoveredAgent(null)}
                  onClick={() => window.location.hash = `#agent/${agent.id}`}
                  className="relative flex flex-col items-center group cursor-pointer"
                >
                  {/* Connection line to center */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none overflow-visible" style={{ zIndex: -1 }}>
                    <motion.line
                      x1="50%" y1="50%"
                      x2="50%" y2="50%"
                      stroke={agent.color}
                      strokeWidth={isHovered ? 2 : 1}
                      strokeDasharray="4 4"
                      opacity={isHovered ? 0.6 : 0.2}
                      transition={{ duration: 0.3 }}
                    />
                  </svg>

                  {/* Agent card */}
                  <motion.div
                    whileHover={{ scale: 1.1, y: -8 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                    className="w-24 h-24 rounded-xl shadow-lg flex items-center justify-center relative overflow-hidden"
                    style={{
                      background: isHovered 
                        ? `linear-gradient(135deg, ${agent.color}20, ${agent.color}10)`
                        : 'white',
                      border: `2px solid ${isHovered ? agent.color : '#e5e7eb'}`,
                    }}
                  >
                    <div 
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      style={{
                        background: `radial-gradient(circle at 30% 30%, ${agent.color}15, transparent 70%)`
                      }}
                    />
                    <Icon size={40} className="relative z-10" style={{ color: agent.color }} />
                  </motion.div>

                  {/* Label */}
                  <motion.div className="mt-4 text-center">
                    <h3 
                      className="font-bold text-base mb-1 transition-colors"
                      style={{ color: isHovered ? agent.color : '#1e3a5f' }}
                    >
                      {agent.name}
                    </h3>
                    <p className="text-xs text-gray-600">{agent.description}</p>
                  </motion.div>

                  {/* Glow effect on hover */}
                  {!reducedMotion && (
                    <motion.div
                      className="absolute w-24 h-24 rounded-xl"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ 
                        opacity: isHovered ? 0.4 : 0,
                        scale: isHovered ? 1.4 : 0.8,
                      }}
                      transition={{ duration: 0.3 }}
                      style={{
                        background: `radial-gradient(circle, ${agent.color}40, transparent 70%)`,
                        filter: 'blur(20px)',
                        pointerEvents: 'none',
                      }}
                    />
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="flex justify-center items-center gap-8 mt-16 text-sm"
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-gov-darkBlue font-medium">Online</span>
          </div>
          <div className="h-4 w-px bg-gray-300" />
          <span className="text-gray-600">6 Active Agents</span>
          <div className="h-4 w-px bg-gray-300" />
          <span className="text-gray-600">99.9% Uptime</span>
        </motion.div>
      </div>
    </section>
  )
}

export default AgentConstellation
