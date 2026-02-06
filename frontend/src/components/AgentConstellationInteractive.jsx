import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Droplets, Flame, Wrench, Heart, DollarSign, Trash2, Zap } from 'lucide-react'

const agents = [
  { id: 'water', name: 'Water', icon: Droplets, color: '#60a5fa', accent: '#93c5fd' },
  { id: 'fire', name: 'Fire', icon: Flame, color: '#fb923c', accent: '#fdba74' },
  { id: 'engineering', name: 'Engineering', icon: Wrench, color: '#2dd4bf', accent: '#5eead4' },
  { id: 'health', name: 'Health', icon: Heart, color: '#f472b6', accent: '#f9a8d4' },
  { id: 'finance', name: 'Finance', icon: DollarSign, color: '#fbbf24', accent: '#fcd34d' },
  { id: 'sanitation', name: 'Sanitation', icon: Trash2, color: '#a78bfa', accent: '#c4b5fd' },
]

const AgentConstellationInteractive = ({ reducedMotion = false }) => {
  const navigate = useNavigate()
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [hoveredAgent, setHoveredAgent] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [orbitAngle, setOrbitAngle] = useState(0)

  // Continuous smooth orbit
  useEffect(() => {
    if (reducedMotion) return
    const interval = setInterval(() => {
      setOrbitAngle(prev => (prev + 0.2) % 360)
    }, 40)
    return () => clearInterval(interval)
  }, [reducedMotion])

  // Calculate 3D elliptical orbit positions
  const getOrbitPosition = (index, baseAngle) => {
    const angle = ((index * 60) + baseAngle) * (Math.PI / 180)
    const radiusX = 320
    const radiusY = 145
    const x = Math.cos(angle) * radiusX
    const y = Math.sin(angle) * radiusY
    const z = Math.sin(angle) * 75
    const scale = 0.65 + (0.45 * ((Math.sin(angle) + 1) / 2))
    return { x, y, z, scale }
  }

  // Slide up animation variants
  const slideUpVariants = {
    hidden: { opacity: 0, y: 60 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }
    }
  }

  return (
    <section 
      ref={ref} 
      className="relative h-full px-6 overflow-hidden"
      style={{ background: 'transparent' }}
    >
      {/* Subtle grid pattern */}
      <div className="absolute inset-0 opacity-[0.02]">
        <div 
          className="absolute inset-0"
          style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }}
        />
      </div>

      {/* Gliding ambient lights */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div 
          className="absolute top-1/4 left-1/4 w-[400px] h-[400px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
          animate={{
            x: [0, 40, 0],
            y: [0, -20, 0],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div 
          className="absolute bottom-1/4 right-1/4 w-[350px] h-[350px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%)',
            filter: 'blur(60px)',
          }}
          animate={{
            x: [0, -40, 0],
            y: [0, 30, 0],
          }}
          transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <div className="max-w-full mx-auto relative z-10 h-full flex items-center justify-center">
        {/* 3D Stage */}
        <motion.div 
          variants={slideUpVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          transition={{ delay: 0.2 }}
          className="relative mx-auto"
          style={{ 
            width: '100%',
            maxWidth: '850px',
            height: '520px',
            perspective: '1400px',
          }}
        >
          <div 
            className="absolute inset-0 flex items-center justify-center"
            style={{
              transformStyle: 'preserve-3d',
              transform: 'rotateX(28deg)',
            }}
          >
            {/* Orbital tracks with slide up */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 30 }}
              animate={inView ? { opacity: 1, scale: 1, y: 0 } : {}}
              transition={{ duration: 1, delay: 0.4 }}
              className="absolute"
              style={{
                width: '640px',
                height: '290px',
                border: '1px solid rgba(96, 165, 250, 0.25)',
                borderRadius: '50%',
                boxShadow: '0 0 30px rgba(59, 130, 246, 0.12), inset 0 0 50px rgba(59, 130, 246, 0.06)',
              }}
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 30 }}
              animate={inView ? { opacity: 1, scale: 1, y: 0 } : {}}
              transition={{ duration: 1, delay: 0.5 }}
              className="absolute"
              style={{
                width: '710px',
                height: '325px',
                border: '1px dashed rgba(251, 191, 36, 0.18)',
                borderRadius: '50%',
              }}
            />

            {/* Central Hub - slides up and rotates */}
            <motion.div
              initial={{ scale: 0, opacity: 0, y: 50 }}
              animate={inView ? { scale: 1, opacity: 1, y: 0 } : {}}
              transition={{ type: 'spring', stiffness: 150, delay: 0.6 }}
              className="absolute z-50"
              style={{ transformStyle: 'preserve-3d' }}
            >
              {/* Rotating glow ring */}
              <motion.div
                className="absolute rounded-full"
                style={{
                  width: '170px',
                  height: '170px',
                  left: '-50px',
                  top: '-50px',
                  background: 'conic-gradient(from 0deg, rgba(251, 191, 36, 0) 0%, rgba(251, 191, 36, 0.35) 25%, rgba(59, 130, 246, 0.35) 50%, rgba(251, 191, 36, 0.35) 75%, rgba(251, 191, 36, 0) 100%)',
                  filter: 'blur(18px)',
                }}
                animate={!reducedMotion ? { rotate: 360 } : {}}
                transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
              />

              {/* Crystal Hub */}
              <motion.div
                className="relative w-20 h-20 cursor-pointer group"
                whileHover={{ scale: 1.15 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 30%, #fbbf24 100%)',
                  borderRadius: '24px',
                  transform: 'rotate(45deg)',
                  boxShadow: '0 20px 40px rgba(59, 130, 246, 0.4), 0 0 50px rgba(251, 191, 36, 0.35), inset 0 2px 8px rgba(255, 255, 255, 0.3)',
                }}
              >
                {/* Glass highlight */}
                <div 
                  className="absolute inset-1 rounded-[20px]"
                  style={{
                    background: 'linear-gradient(135deg, rgba(255,255,255,0.5) 0%, transparent 60%)',
                  }}
                />

                {/* Pulsing inner glow */}
                <motion.div
                  className="absolute inset-3 rounded-[16px]"
                  style={{
                    background: 'radial-gradient(circle at 30% 30%, rgba(251, 191, 36, 0.7), rgba(59, 130, 246, 0.4))',
                  }}
                  animate={!reducedMotion ? {
                    opacity: [0.6, 1, 0.6],
                  } : {}}
                  transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                />

                <div 
                  className="absolute inset-0 flex items-center justify-center"
                  style={{ transform: 'rotate(-45deg)' }}
                >
                  <Zap size={28} className="text-white drop-shadow-lg" />
                </div>

                {/* Hover expand ring */}
                <motion.div
                  className="absolute inset-0 rounded-[20px] border-2 border-white/30"
                  initial={{ scale: 1, opacity: 0 }}
                  whileHover={{ scale: 1.3, opacity: 1 }}
                  transition={{ duration: 0.3 }}
                />
              </motion.div>

              <motion.p 
                className="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap font-bold text-sm text-white/90"
                initial={{ opacity: 0, y: -10 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 1 }}
              >
                Coordinator
              </motion.p>
            </motion.div>

            {/* Orbiting Agents - gliding motion */}
            {agents.map((agent, index) => {
              const pos = getOrbitPosition(index, orbitAngle)
              const Icon = agent.icon
              const isHovered = hoveredAgent === agent.id
              const isSelected = selectedAgent === agent.id
              const isFront = pos.y > 0

              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, scale: 0, y: 60 }}
                  animate={inView ? { 
                    opacity: 1, 
                    scale: 1,
                    x: pos.x,
                    y: pos.y,
                  } : {}}
                  transition={{ 
                    opacity: { duration: 0.6, delay: 0.7 + index * 0.1 },
                    scale: { duration: 0.6, delay: 0.7 + index * 0.1 },
                    x: { duration: 0.05, ease: 'linear' },
                    y: { duration: 0.05, ease: 'linear' },
                  }}
                  className="absolute cursor-pointer"
                  style={{
                    top: '50%',
                    left: '50%',
                    zIndex: isFront ? 40 : 20,
                    transformStyle: 'preserve-3d',
                    transform: `translateZ(${pos.z}px) scale(${pos.scale})`,
                  }}
                  onMouseEnter={() => setHoveredAgent(agent.id)}
                  onMouseLeave={() => setHoveredAgent(null)}
                  onClick={() => setSelectedAgent(isSelected ? null : agent.id)}
                >
                  {/* Connection line */}
                  <svg 
                    className="absolute pointer-events-none"
                    style={{
                      width: '340px',
                      height: '215px',
                      left: '-170px',
                      top: '-107px',
                      overflow: 'visible',
                    }}
                  >
                    <motion.line
                      x1="170" y1="107"
                      x2={170 - pos.x} y2={107 - pos.y}
                      stroke={isHovered ? agent.color : 'rgba(96, 165, 250, 0.3)'}
                      strokeWidth={isHovered ? 2.5 : 1}
                      strokeDasharray={isHovered ? '0' : '4 4'}
                      animate={{ opacity: isHovered ? 1 : 0.5 }}
                      transition={{ duration: 0.3 }}
                    />
                  </svg>

                  {/* Glassmorphism orb with hover animations */}
                  <motion.div
                    className="relative group"
                    whileHover={{ 
                      scale: 1.2,
                      rotateY: 15,
                      rotateX: -10,
                    }}
                    whileTap={{ scale: 0.95 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    style={{
                      width: '75px',
                      height: '75px',
                      borderRadius: '50%',
                      background: isHovered || isSelected
                        ? `linear-gradient(135deg, ${agent.color}30, ${agent.color}15)`
                        : 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))',
                      backdropFilter: 'blur(12px)',
                      WebkitBackdropFilter: 'blur(12px)',
                      border: `2px solid ${isHovered || isSelected ? agent.color : 'rgba(255,255,255,0.3)'}`,
                      boxShadow: isHovered || isSelected
                        ? `0 20px 50px ${agent.color}50, 0 0 30px ${agent.color}40, inset 0 1px 3px rgba(255,255,255,0.6)`
                        : '0 10px 30px rgba(0,0,0,0.3), 0 4px 15px rgba(59, 130, 246, 0.2), inset 0 1px 3px rgba(255,255,255,0.3)',
                      transformStyle: 'preserve-3d',
                    }}
                  >
                    {/* Glass highlight */}
                    <div 
                      className="absolute rounded-full"
                      style={{
                        top: '4px',
                        left: '8px',
                        width: '50%',
                        height: '30%',
                        background: 'linear-gradient(180deg, rgba(255,255,255,0.8) 0%, transparent 100%)',
                        borderRadius: '50%',
                      }}
                    />

                    {/* Icon container */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <motion.div 
                        className="p-3 rounded-xl"
                        style={{
                          background: `linear-gradient(135deg, ${agent.color}, ${agent.accent})`,
                          boxShadow: `0 4px 20px ${agent.color}60`,
                        }}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 17 }}
                      >
                        <Icon size={20} className="text-white" />
                      </motion.div>
                    </div>

                    {/* Hover glow ring */}
                    <motion.div
                      className="absolute inset-0 rounded-full"
                      style={{
                        border: `2px solid ${agent.accent}`,
                      }}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ 
                        opacity: isHovered ? 1 : 0,
                        scale: isHovered ? 1.2 : 0.9,
                      }}
                      transition={{ duration: 0.3 }}
                    />
                  </motion.div>

                  {/* Label - slides up on hover */}
                  <motion.p
                    className="absolute -bottom-7 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs font-semibold"
                    style={{ color: isHovered || isSelected ? agent.color : 'rgba(255,255,255,0.7)' }}
                    animate={{ 
                      y: isHovered ? -5 : 0,
                      opacity: pos.scale > 0.8 ? 1 : 0.6 
                    }}
                    transition={{ duration: 0.2 }}
                  >
                    {agent.name}
                  </motion.p>
                </motion.div>
              )
            })}

            {/* Floating particles - gliding animation */}
            {!reducedMotion && inView && [...Array(10)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 rounded-full"
                style={{
                  background: i % 2 === 0 ? 'rgba(96, 165, 250, 0.6)' : 'rgba(251, 191, 36, 0.5)',
                  boxShadow: i % 2 === 0 
                    ? '0 0 10px rgba(96, 165, 250, 0.9)' 
                    : '0 0 10px rgba(251, 191, 36, 0.9)',
                }}
                animate={{
                  x: [
                    Math.cos((i * 36) * Math.PI / 180) * 280,
                    Math.cos((i * 36 + 180) * Math.PI / 180) * 280,
                  ],
                  y: [
                    Math.sin((i * 36) * Math.PI / 180) * 125,
                    Math.sin((i * 36 + 180) * Math.PI / 180) * 125,
                  ],
                  opacity: [0, 1, 0],
                  scale: [0, 1.2, 0],
                }}
                transition={{
                  duration: 8,
                  delay: i * 0.4,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Modal - slides up */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-6"
            style={{ background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(12px)' }}
            onClick={() => setSelectedAgent(null)}
          >
            <motion.div
              initial={{ scale: 0.8, y: 60, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.8, y: 60, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              onClick={(e) => e.stopPropagation()}
              className="relative max-w-sm w-full rounded-3xl overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.98))',
                backdropFilter: 'blur(20px)',
                boxShadow: '0 30px 90px rgba(0,0,0,0.5), 0 0 1px rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              {(() => {
                const agent = agents.find(a => a.id === selectedAgent)
                const Icon = agent?.icon
                return (
                  <div className="p-6">
                    <div 
                      className="absolute top-0 left-0 right-0 h-1"
                      style={{ background: `linear-gradient(90deg, ${agent?.color}, ${agent?.accent})` }}
                    />

                    <div className="flex items-center gap-4 mb-5">
                      <motion.div 
                        className="w-14 h-14 rounded-2xl flex items-center justify-center"
                        style={{ 
                          background: `linear-gradient(135deg, ${agent?.color}, ${agent?.accent})`,
                          boxShadow: `0 10px 30px ${agent?.color}50`,
                        }}
                        whileHover={{ scale: 1.1, rotate: 5 }}
                      >
                        <Icon size={26} className="text-white" />
                      </motion.div>
                      <div>
                        <h3 className="text-xl font-bold text-white">{agent?.name}</h3>
                        <p className="text-sm text-white/60">Department Agent</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 mb-5">
                      <motion.div 
                        className="rounded-xl p-4 text-center"
                        style={{ background: 'rgba(96, 165, 250, 0.1)' }}
                        whileHover={{ scale: 1.05, y: -2 }}
                      >
                        <div className="text-2xl font-bold" style={{ color: agent?.color }}>2,847</div>
                        <div className="text-xs text-white/60 mt-1">Tasks</div>
                      </motion.div>
                      <motion.div 
                        className="rounded-xl p-4 text-center"
                        style={{ background: 'rgba(16, 185, 129, 0.1)' }}
                        whileHover={{ scale: 1.05, y: -2 }}
                      >
                        <div className="text-2xl font-bold text-green-400">99.9%</div>
                        <div className="text-xs text-white/60 mt-1">Uptime</div>
                      </motion.div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <motion.button
                        onClick={() => navigate(`/agent/${agent?.id}`)}
                        className="py-3 rounded-xl font-semibold text-white transition-all"
                        style={{ 
                          background: `linear-gradient(135deg, ${agent?.color}, ${agent?.accent})`,
                          boxShadow: `0 4px 20px ${agent?.color}40`,
                        }}
                        whileHover={{ scale: 1.02, boxShadow: `0 6px 30px ${agent?.color}60` }}
                        whileTap={{ scale: 0.98 }}
                      >
                        View Details
                      </motion.button>
                      <motion.button
                        onClick={() => setSelectedAgent(null)}
                        className="py-3 rounded-xl font-semibold text-white/80 transition-all"
                        style={{ 
                          background: 'rgba(255, 255, 255, 0.1)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                        }}
                        whileHover={{ scale: 1.02, background: 'rgba(255, 255, 255, 0.15)' }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Close
                      </motion.button>
                    </div>
                  </div>
                )
              })()}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  )
}

export default AgentConstellationInteractive
