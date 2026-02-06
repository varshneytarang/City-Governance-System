import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Droplets, Flame, Wrench, Heart, DollarSign, Trash2, Network } from 'lucide-react'

const iconsMap = {
  water: Droplets,
  fire: Flame,
  engineering: Wrench,
  health: Heart,
  finance: DollarSign,
  sanitation: Trash2
}

const agents = [
  {
    id: 'water',
    name: 'Water Services',
    capabilities: ['Leak detection', 'Consumption forecasting', 'Supply routing']
  },
  {
    id: 'fire',
    name: 'Fire Response',
    capabilities: ['Risk assessment', 'Dispatch coordination', 'Incident simulation']
  },
  {
    id: 'engineering',
    name: 'Engineering',
    capabilities: ['Infrastructure design', 'Load balancing', 'Maintenance scheduling']
  },
  {
    id: 'health',
    name: 'Health',
    capabilities: ['Outbreak monitoring', 'Resource allocation', 'Emergency triage']
  },
  {
    id: 'finance',
    name: 'Finance',
    capabilities: ['Budget planning', 'Grant management', 'Transaction auditing']
  },
  {
    id: 'sanitation',
    name: 'Sanitation',
    capabilities: ['Route optimization', 'Waste categorization', 'Pickup scheduling']
  }
].map((a, i, arr) => ({
  ...a,
  icon: iconsMap[a.id] || Droplets,
  position: {
    top: `${30 + Math.sin((i / arr.length) * Math.PI * 2) * 25}%`,
    left: `${50 + Math.cos((i / arr.length) * Math.PI * 2) * 35}%`
  }
}))

const AgentConstellation = ({ reducedMotion = false }) => {
  const navigate = useNavigate()
  const [ref, inView] = useInView({ threshold: 0.2, triggerOnce: true })
  const [hoveredAgent, setHoveredAgent] = useState(null)

  return (
    <section ref={ref} className="relative py-32 px-6 bg-transparent overflow-hidden">
      {!reducedMotion && (
        <>
          <div className="absolute -left-40 -top-20 w-96 h-96 rounded-full bg-gradient-to-br from-[#0ea5e9]/15 to-[#f59e0b]/12 blur-3xl opacity-60 pointer-events-none transform -rotate-12" />
          <div className="absolute -right-32 -bottom-24 w-[28rem] h-[28rem] rounded-full bg-gradient-to-tr from-[#a78bfa]/14 to-[#34d399]/12 blur-3xl opacity-60 pointer-events-none transform rotate-6" />
        </>
      )}

      <div className="max-w-7xl mx-auto">
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

        <div className="relative w-full max-w-4xl mx-auto" style={{ height: '600px' }}>
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={inView ? { scale: 1, opacity: 1 } : {}}
            transition={{ type: 'spring', stiffness: 200, delay: 0.3 }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20"
          >
            <div className={`w-24 h-24 rounded-full professional-card flex items-center justify-center shadow-professional ${
              reducedMotion ? '' : 'animate-pulse-slow'
            }`}>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gov-navy to-accent-gold shadow-gold-glow" />
            </div>
            <p className="text-center mt-3 font-semibold text-gov-navy text-sm">Coordinator</p>
          </motion.div>

          {/* Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {agents.map((agent, index) => {
              // Calculate actual pixel positions from percentages
              const centerX = '50%'
              const centerY = '50%'
              
              return (
                <motion.line
                  key={`line-${agent.id}`}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={inView ? { pathLength: 1, opacity: 0.28 } : {}}
                  transition={{ duration: 1.0, delay: 0.2 + index * 0.06 }}
                  x1={centerX}
                  y1={centerY}
                  x2={agent.position.left}
                  y2={agent.position.top}
                  stroke="rgba(59,130,246,0.22)"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                />
              )
            })}
          </svg>

          {agents.map((agent, index) => (
            <AgentOrb
              key={agent.id}
              agent={agent}
              index={index}
              inView={inView}
              reducedMotion={reducedMotion}
              isHovered={hoveredAgent === agent.id}
              onHover={setHoveredAgent}
            />
          ))}
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

const AgentOrb = ({ agent, index, inView, reducedMotion, isHovered, onHover }) => {
  const Icon = agent.icon

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : {}}
      transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
      drag
      dragMomentum={false}
      whileDrag={{ scale: 1.1, zIndex: 1000 }}
      className="absolute cursor-grab active:cursor-grabbing transform -translate-x-1/2 -translate-y-1/2"
      style={{
        top: agent.position.top,
        left: agent.position.left,
      }}
      id={`agent-dom-${agent.id}`}
      onMouseEnter={() => onHover(agent.id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="relative">
        <div
          className={`w-20 h-20 rounded-full professional-card flex items-center justify-center transition-all duration-500 ${
            isHovered ? 'scale-110 shadow-elevated ring-2 ring-accent-gold' : 'shadow-soft'
          } ${reducedMotion ? '' : 'hover:animate-float'}`}
        >
          <Icon size={32} className="text-gov-blue" />
        </div>

        <p className="text-center mt-2 font-semibold text-sm text-gov-navy">{agent.name}</p>

        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-full mt-4 left-1/2 transform -translate-x-1/2 professional-card p-4 rounded-lg w-48 z-20 shadow-elevated"
          >
            <h4 className="font-bold mb-2 text-sm text-gov-navy">Capabilities</h4>
            <ul className="space-y-1 text-xs text-gov-gray">
              {agent.capabilities.map((cap, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="w-1 h-1 rounded-full bg-accent-gold" />
                  {cap}
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default AgentConstellation
