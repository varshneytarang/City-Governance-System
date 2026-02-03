import React from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Droplets, Flame, Wrench, Heart, DollarSign, Trash2 } from 'lucide-react'

const agents = [
  {
    id: 'water',
    name: 'Water',
    icon: Droplets,
    color: 'electric-sapphire',
    capabilities: ['Leak Detection', 'Pressure Monitoring', 'Quality Testing'],
    position: { top: '20%', left: '50%', rotate: 0 }
  },
  {
    id: 'fire',
    name: 'Fire',
    icon: Flame,
    color: 'molten-gold',
    capabilities: ['Risk Assessment', 'Resource Allocation', 'Emergency Response'],
    position: { top: '40%', left: '80%', rotate: 60 }
  },
  {
    id: 'engineering',
    name: 'Engineering',
    icon: Wrench,
    color: 'neon-emerald',
    capabilities: ['Infrastructure Monitor', 'Maintenance Planning', 'Project Management'],
    position: { top: '70%', left: '80%', rotate: 120 }
  },
  {
    id: 'health',
    name: 'Health',
    icon: Heart,
    color: 'nebula-violet',
    capabilities: ['Disease Tracking', 'Resource Planning', 'Emergency Prep'],
    position: { top: '80%', left: '50%', rotate: 180 }
  },
  {
    id: 'finance',
    name: 'Finance',
    icon: DollarSign,
    color: 'molten-gold',
    capabilities: ['Budget Optimization', 'Cost Analysis', 'Fund Allocation'],
    position: { top: '70%', left: '20%', rotate: 240 }
  },
  {
    id: 'sanitation',
    name: 'Sanitation',
    icon: Trash2,
    color: 'neon-emerald',
    capabilities: ['Waste Management', 'Route Optimization', 'Resource Tracking'],
    position: { top: '40%', left: '20%', rotate: 300 }
  }
]

const AgentConstellation = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.2, triggerOnce: true })
  const [hoveredAgent, setHoveredAgent] = React.useState(null)

  return (
    <section ref={ref} className="relative py-32 px-6 bg-white">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl md:text-6xl font-bold font-heading mb-6">
            <span className="text-gradient">Department Agents</span>
          </h2>
          <p className="text-xl text-gov-gray max-w-3xl mx-auto">
            Six specialized AI agents working in harmony, each an expert in their domain
          </p>
        </motion.div>

        {/* Constellation Container */}
        <div className="relative w-full max-w-4xl mx-auto" style={{ height: '600px' }}>
          {/* Central Coordination Node */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={inView ? { scale: 1, opacity: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
          >
            <div className={`w-24 h-24 rounded-full professional-card flex items-center justify-center shadow-professional ${
              reducedMotion ? '' : 'animate-pulse-slow'
            }`}>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gov-navy to-accent-gold shadow-gold-glow"></div>
            </div>
            <p className="text-center mt-3 font-bold text-sm text-gov-navy">Coordination Hub</p>
          </motion.div>

          {/* Agent Orbs */}
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

          {/* Connection Lines */}
          {!reducedMotion && inView && (
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {agents.map((agent, index) => (
                <motion.line
                  key={`line-${agent.id}`}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 0.3 }}
                  transition={{ duration: 1.5, delay: 0.5 + index * 0.1 }}
                  x1="50%"
                  y1="50%"
                  x2={agent.position.left}
                  y2={agent.position.top}
                  stroke="url(#gradient)"
                  strokeWidth="2"
                  strokeDasharray="4 4"
                />
              ))}
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#d4af37" stopOpacity="0.3" />
                </linearGradient>
              </defs>
            </svg>
          )}
        </div>
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
      className="absolute cursor-grab active:cursor-grabbing"
      style={{ 
        top: agent.position.top, 
        left: agent.position.left,
        x: '-50%',
        y: '-50%'
      }}
      onMouseEnter={() => onHover(agent.id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="relative">
        {/* Orb */}
        <div
          className={`w-20 h-20 rounded-full professional-card flex items-center justify-center transition-all duration-500 ${
            isHovered ? 'scale-110 shadow-elevated ring-2 ring-accent-gold' : 'shadow-soft'
          } ${reducedMotion ? '' : 'hover:animate-float'}`}
        >
          <Icon 
            size={32} 
            className="text-gov-blue"
          />
        </div>

        {/* Label */}
        <p className="text-center mt-2 font-semibold text-sm text-gov-navy">{agent.name}</p>

        {/* Capabilities Popup */}
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
                  <span className="w-1 h-1 rounded-full bg-accent-gold"></span>
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
