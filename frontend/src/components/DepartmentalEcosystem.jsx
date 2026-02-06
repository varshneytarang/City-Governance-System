import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import {
  Droplets,
  Flame,
  Wrench,
  Shield,
  BarChart3,
  Trash2,
  Cpu,
  Zap
} from 'lucide-react'

/**
 * DepartmentalEcosystem - A stunning 3D orbital visualization
 * 
 * Features:
 * - Central Coordinator hub with command center aesthetic
 * - 6 department agents in 3D elliptical orbits
 * - Glassmorphism design with blur and transparency
 * - Professional color palette (deep blues, teals, gold accents)
 * - Animated orbital paths with depth perspective
 */

const ORBIT = {
  width: 1200,
  height: 760,
  radiusX: 520,
  radiusY: 260,
}

ORBIT.centerX = ORBIT.width / 2
// Optional visual nudge to align the Coordinator with the visual intersection
// (use these if the rotated orbit ring or perspective makes the visual center
// appear offset from the logical center)
ORBIT.offsetX = 0
ORBIT.offsetY = 0

ORBIT.centerX = ORBIT.width / 2 + ORBIT.offsetX
ORBIT.centerY = ORBIT.height / 2 + ORBIT.offsetY

const agents = [
  {
    id: 'water',
    name: 'Water Services',
    icon: Droplets,
    color: '#0ea5e9',
    gradient: 'from-sky-400 to-cyan-500',
    capabilities: ['Leak detection', 'Consumption forecasting', 'Supply routing'],
    orbitSpeed: 45,
    orbitDelay: 0,
  },
  {
    id: 'fire',
    name: 'Fire Response',
    icon: Flame,
    color: '#f97316',
    gradient: 'from-orange-400 to-red-500',
    capabilities: ['Risk assessment', 'Dispatch coordination', 'Incident simulation'],
    orbitSpeed: 50,
    orbitDelay: 1,
  },
  {
    id: 'engineering',
    name: 'Engineering',
    icon: Wrench,
    color: '#6366f1',
    gradient: 'from-indigo-400 to-purple-500',
    capabilities: ['Infrastructure design', 'Load balancing', 'Maintenance scheduling'],
    orbitSpeed: 55,
    orbitDelay: 2,
  },
  {
    id: 'health',
    name: 'Health',
    icon: Shield,
    color: '#14b8a6',
    gradient: 'from-teal-400 to-cyan-500',
    capabilities: ['Outbreak monitoring', 'Risk mitigation', 'Emergency triage'],
    orbitSpeed: 48,
    orbitDelay: 3,
  },
  {
    id: 'finance',
    name: 'Finance',
    icon: BarChart3,
    color: '#eab308',
    gradient: 'from-yellow-400 to-amber-500',
    capabilities: ['Budget planning', 'Forecast modeling', 'Transaction auditing'],
    orbitSpeed: 52,
    orbitDelay: 4,
  },
  {
    id: 'sanitation',
    name: 'Sanitation',
    icon: Trash2,
    color: '#22c55e',
    gradient: 'from-green-400 to-emerald-500',
    capabilities: ['Route optimization', 'Waste categorization', 'Pickup scheduling'],
    orbitSpeed: 47,
    orbitDelay: 5,
  },
]

// Calculate 3D elliptical orbit positions
// Each agent gets a slightly different ellipse to avoid overlap
const getOrbitPosition = (index, total, time, orbitDelay, orbitSpeed) => {
  // Use circular orbits for smooth rotation and even angular spacing
  const baseRadius = ORBIT.radiusX - 40 // inner padding to keep nodes inside container
  // Small radial jitter so nodes don't perfectly overlap when crossing
  const radialJitter = (index - (total - 1) / 2) * 8
  const r = baseRadius + radialJitter

  // Evenly space agents around the circle (degrees)
  const basePhase = (360 / total) * index
  // time controls rotation; orbitDelay tweaks phase slightly per agent
  const angleDeg = (time * (orbitSpeed / 50)) + basePhase + orbitDelay * 6
  const angle = (angleDeg % 360) * (Math.PI / 180)

  const x = Math.cos(angle) * r
  const y = Math.sin(angle) * r

  // z-depth for simple 3D effect
  const z = Math.sin(angle)

  // Depth tilt: bring front elements slightly downwards
  const depthShift = z * 32

  // Slightly larger base scale for bigger agent nodes
  const scale = 0.76 + (z + 1) * 0.22

  const opacity = 0.55 + (z + 1) * 0.25

  const zIndex = Math.round((z + 1) * 100)

  return { x, y: y - depthShift, scale, opacity, zIndex, z }
}

const DepartmentalEcosystem = ({ reducedMotion = false }) => {
  const [ref, inView] = useInView({ threshold: 0.15, triggerOnce: false })
  const [hoveredAgent, setHoveredAgent] = useState(null)
    const [time, setTime] = useState(0)
    const [isPaused, setIsPaused] = useState(false)
    const [isAnimating, setIsAnimating] = useState(false)

    // Delay animation start until entrance completes
    useEffect(() => {
      if (inView && !isAnimating) {
        // Wait for entrance animation to complete (0.6s + longest delay)
        const timer = setTimeout(() => {
          setIsAnimating(true)
        }, 1200)
        return () => clearTimeout(timer)
      }
    }, [inView, isAnimating])

    // Animate orbit rotation using requestAnimationFrame for smoothness
    // Clamp large frame deltas to avoid jumpy frames when the tab resumes
    useEffect(() => {
      if (reducedMotion || !isAnimating) return

      let raf = null
      let last = performance.now()

      const step = (now) => {
        let delta = now - last
        // prevent giant jumps (e.g., when resuming from background)
        delta = Math.min(delta, 40)
        last = now
        if (!isPaused) {
          // advance time in degrees per frame (scaled by delta)
          setTime(t => (t + (delta * 0.035)) % 360)
        }
        raf = requestAnimationFrame(step)
      }

      raf = requestAnimationFrame(step)
      return () => cancelAnimationFrame(raf)
    }, [reducedMotion, isPaused, isAnimating])

    // Pause rotation only when hovering a specific agent
    useEffect(() => {
      setIsPaused(hoveredAgent !== null)
    }, [hoveredAgent])

  return (
    <section 
      ref={ref} 
      className="relative py-32 px-6 overflow-hidden"
      style={{
        background: 'linear-gradient(180deg, #0a0f1a 0%, #0d1424 50%, #0a0f1a 100%)',
      }}
    >
      {/* Animated Background Elements */}
      <BackgroundEffects inView={inView} reducedMotion={reducedMotion} />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, ease: 'easeOut' }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-teal-400 bg-clip-text text-transparent">
              Department
            </span>{' '}
            <span className="bg-gradient-to-r from-amber-300 via-yellow-400 to-amber-500 bg-clip-text text-transparent">
              Agents
            </span>
          </h2>
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Six specialized AI agents working in harmony, each an expert in their domain
          </p>
        </motion.div>

        {/* Orbital System Container */}
        <div
          className="relative mx-auto"
          style={{
              width: `${ORBIT.width}px`,
              height: `${ORBIT.height}px`,
              perspective: '1200px',
              position: 'relative',
              margin: '0 auto'
            }}
        >
          {/* Orbit Path Rings */}
          <OrbitRings inView={inView} reducedMotion={reducedMotion} />

          {/* Central Coordinator Hub */}
          <CoordinatorHub inView={inView} reducedMotion={reducedMotion} />

          {/* Connection Lines */}
          <ConnectionLines 
            agents={agents} 
            time={time} 
            hoveredAgent={hoveredAgent}
            inView={inView}
          />

          {/* Orbiting Agent Nodes */}
          {agents.map((agent, index) => (
            <AgentNode
              key={agent.id}
              agent={agent}
              index={index}
              total={agents.length}
              time={time}
              inView={inView}
              reducedMotion={reducedMotion}
              isHovered={hoveredAgent === agent.id}
              onHover={setHoveredAgent}
            />
          ))}
        </div>

        {/* Legend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.2 }}
          className="mt-16 flex flex-wrap justify-center gap-4"
        >
          {agents.map((agent) => {
            const Icon = agent.icon
            return (
              <div
                key={agent.id}
                className="flex items-center gap-2 px-4 py-2 rounded-full backdrop-blur-md border border-white/10"
                style={{ backgroundColor: `${agent.color}15` }}
              >
                <Icon size={16} style={{ color: agent.color }} />
                <span className="text-sm text-slate-300">{agent.name}</span>
              </div>
            )
          })}
        </motion.div>
      </div>
    </section>
  )
}

// Background ambient effects
const BackgroundEffects = ({ inView, reducedMotion }) => (
  <>
    {/* Grid Pattern */}
    <div 
      className="absolute inset-0 opacity-[0.03]"
      style={{
        backgroundImage: `
          linear-gradient(rgba(59, 130, 246, 0.3) 1px, transparent 1px),
          linear-gradient(90deg, rgba(59, 130, 246, 0.3) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
      }}
    />

    {/* Radial Gradient Glows */}
    <motion.div
      initial={{ opacity: 0 }}
      animate={inView ? { opacity: 1 } : {}}
      transition={{ duration: 2 }}
      className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] pointer-events-none"
      style={{
        background: 'radial-gradient(ellipse at center, rgba(6, 182, 212, 0.08) 0%, transparent 60%)',
      }}
    />

    {/* Floating Particles */}
    {!reducedMotion && (
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 rounded-full bg-cyan-400/30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.6, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>
    )}
  </>
)

// 3D Orbit ring paths
const OrbitRings = ({ inView, reducedMotion }) => (
  <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ transformStyle: 'preserve-3d' }}>
    {/* Main orbit ellipse */}
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={inView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 1.2, ease: 'easeOut' }}
      className="absolute"
      style={{
        width: `${ORBIT.radiusX * 2}px`,
        height: `${ORBIT.radiusY * 2}px`,
        borderRadius: '50%',
        border: '1px solid rgba(59, 130, 246, 0.15)',
        transform: 'rotateX(68deg)',
        boxShadow: `
          0 0 40px rgba(6, 182, 212, 0.05),
          inset 0 0 40px rgba(6, 182, 212, 0.03)
        `,
      }}
    />
    
    {/* Secondary orbit ellipse */}
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={inView ? { opacity: 0.5, scale: 1 } : {}}
      transition={{ duration: 1.2, delay: 0.2, ease: 'easeOut' }}
      className="absolute"
      style={{
        width: `${ORBIT.radiusX * 2 + 80}px`,
        height: `${ORBIT.radiusY * 2 + 60}px`,
        borderRadius: '50%',
        border: '1px dashed rgba(59, 130, 246, 0.08)',
        transform: 'rotateX(68deg)',
      }}
    />

    {/* Inner glow ring */}
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={inView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 1, delay: 0.4 }}
      className="absolute w-48 h-48 rounded-full"
      style={{
        background: 'radial-gradient(circle, rgba(251, 191, 36, 0.1) 0%, transparent 70%)',
      }}
    />

    {/* Exact agent path ring (matches getOrbitPosition base radius) */}
    <motion.div
      initial={{ opacity: 0 }}
      animate={inView ? { opacity: 0.6 } : {}}
      transition={{ duration: 1.1, delay: 0.15 }}
      className="absolute"
      style={{
        width: `${(ORBIT.radiusX - 40) * 2}px`,
        height: `${(ORBIT.radiusX - 40) * 2 * (ORBIT.radiusY / ORBIT.radiusX)}px`,
        borderRadius: '50%',
        border: '1px solid rgba(59, 130, 246, 0.12)',
        transform: 'rotateX(68deg)',
        boxShadow: '0 0 30px rgba(6,182,212,0.03) inset',
      }}
    />
  </div>
)

// Central Coordinator Hub
const CoordinatorHub = ({ inView, reducedMotion }) => {
  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : {}}
      transition={{ duration: 0.8, delay: 0.3, type: 'spring', stiffness: 200, damping: 20 }}
      className="absolute z-50"
      style={{ left: `calc(${ORBIT.centerX}px - 50px)`, top: `calc(${ORBIT.centerY}px - 50px)`, transform: 'translate(-50%, -50%)' }}
    >
      {/* Outer pulsing ring */}
      {!reducedMotion && (
        <motion.div
          className="absolute inset-0 -m-4 rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(251, 191, 36, 0.2) 0%, transparent 70%)' }}
          animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0.2, 0.5] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}

      {/* Glassmorphism card */}
      <div
        className="relative w-28 h-28 rounded-full flex items-center justify-center cursor-pointer group"
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.18)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 60px rgba(251,191,36,0.15), inset 0 1px 0 rgba(255,255,255,0.1)'
        }}
      >
        <motion.div
          className="w-20 h-20 rounded-full flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg, #1e3a5f 0%, #0d1f3c 50%, #0a1628 100%)' }}
          animate={!reducedMotion ? { boxShadow: ['inset 0 -4px 12px rgba(0,0,0,0.4), inset 0 4px 12px rgba(251,191,36,0.1), 0 4px 20px rgba(251,191,36,0.2)', 'inset 0 -4px 12px rgba(0,0,0,0.4), inset 0 4px 12px rgba(251,191,36,0.2), 0 4px 30px rgba(251,191,36,0.3)'] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Cpu className="text-amber-400 w-8 h-8" />
        </motion.div>
      </div>

      {/* Label */}
      <div style={{ position: 'absolute', bottom: -40, left: '50%', transform: 'translateX(-50%)' }}>
        <span className="text-sm font-semibold bg-gradient-to-r from-amber-300 to-yellow-500 bg-clip-text text-transparent">Coordination Hub</span>
      </div>
    </motion.div>
  )
}

// Dynamic connection lines between hub and agents
const ConnectionLines = ({ agents, time, hoveredAgent, inView }) => {
  if (!inView) return null

  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      viewBox={`0 0 ${ORBIT.width} ${ORBIT.height}`}
      preserveAspectRatio="xMidYMid meet"
      style={{ zIndex: 1 }}
    >
      <defs>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="rgba(251, 191, 36, 0.4)" />
          <stop offset="50%" stopColor="rgba(59, 130, 246, 0.3)" />
          <stop offset="100%" stopColor="rgba(6, 182, 212, 0.4)" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {agents.map((agent, index) => {
        const pos = getOrbitPosition(index, agents.length, time, agent.orbitDelay, agent.orbitSpeed)
        const centerX = ORBIT.centerX
        const centerY = ORBIT.centerY
        const isActive = hoveredAgent === agent.id

        return (
          <motion.line
            key={`line-${agent.id}`}
            x1={centerX}
            y1={centerY}
            x2={centerX + pos.x}
            y2={centerY + pos.y}
            stroke={isActive ? agent.color : 'url(#lineGradient)'}
            strokeWidth={isActive ? 2.5 : 1}
            strokeOpacity={isActive ? 0.95 : 0.22}
            strokeDasharray={isActive ? '0' : '6 4'}
            filter={isActive ? 'url(#glow)' : undefined}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay: 0.25 + index * 0.05 }}
          />
        )
      })}
    </svg>
  )
}

// Individual Agent Node
const AgentNode = ({
  agent,
  index,
  total,
  time,
  inView,
  reducedMotion,
  isHovered,
  onHover
}) => {
  const Icon = agent.icon
  const pos = getOrbitPosition(index, total, time, agent.orbitDelay, agent.orbitSpeed)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={inView ? {
        opacity: pos.opacity,
        scale: pos.scale,
        x: pos.x,
        y: pos.y,
      } : {}}
      transition={{
        duration: 0.6,
        delay: 0.6 + index * 0.1,
        x: { duration: 0 },
        y: { duration: 0 },
        scale: { duration: 0.3 },
        opacity: { duration: 0.3 },
      }}
      className="absolute cursor-pointer"
      style={{
          left: '50%',
          top: '50%',
          marginLeft: '-56px',
          marginTop: '-56px',
        zIndex: pos.zIndex,
        transformStyle: 'preserve-3d',
        filter: `blur(${Math.max(0, (1 - pos.scale) * 6)}px)`,
      }}
      onMouseEnter={() => onHover(agent.id)}
      onMouseLeave={() => onHover(null)}
    >
      {/* Glassmorphism Node */}
      <motion.div
        whileHover={{ scale: 1.12 }}
        whileTap={{ scale: 0.95 }}
        className="relative w-28 h-28 rounded-2xl flex items-center justify-center transition-all duration-300"
        style={{
          background: isHovered 
            ? `linear-gradient(135deg, ${agent.color}30 0%, ${agent.color}10 100%)`
            : 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: isHovered 
            ? `1px solid ${agent.color}60`
            : '1px solid rgba(255,255,255,0.12)',
          boxShadow: isHovered
            ? `0 8px 32px ${agent.color}40, 0 0 40px ${agent.color}20`
            : '0 8px 32px rgba(0,0,0,0.2)',
        }}
      >
        {/* Icon with gradient background */}
        <div
          className={`w-16 h-16 rounded-xl flex items-center justify-center bg-gradient-to-br ${agent.gradient}`}
          style={{
            boxShadow: `0 6px 18px ${agent.color}40`,
          }}
        >
          <Icon className="text-white w-8 h-8" />
        </div>

        {/* Active indicator */}
        {!reducedMotion && (
          <motion.div
            className="absolute -top-1 -right-1 w-3 h-3 rounded-full"
            style={{ backgroundColor: agent.color }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [1, 0.7, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: index * 0.3,
            }}
          />
        )}
      </motion.div>

      {/* Agent Name */}
      <motion.p 
        className="text-center mt-2 text-sm font-medium whitespace-nowrap"
        style={{ 
          color: isHovered ? agent.color : 'rgba(203, 213, 225, 0.8)',
          textShadow: isHovered ? `0 0 10px ${agent.color}80` : 'none',
        }}
        animate={{ opacity: pos.opacity }}
      >
        {agent.name}
      </motion.p>

      {/* Hover Tooltip */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full mt-4 left-1/2 -translate-x-1/2 w-64 p-4 rounded-xl z-[100]"
            style={{
              background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              border: `1px solid ${agent.color}40`,
              boxShadow: `0 20px 40px rgba(0,0,0,0.4), 0 0 30px ${agent.color}20`,
            }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br ${agent.gradient}`}
              >
                <Icon className="text-white w-4 h-4" />
              </div>
              <h4 className="font-bold text-white text-sm">{agent.name}</h4>
            </div>
            
            <div className="space-y-2">
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wide">
                Capabilities
              </p>
              <ul className="space-y-1.5">
                {agent.capabilities.map((cap, i) => (
                  <li key={i} className="flex items-center gap-2 text-xs text-slate-300">
                    <Zap size={10} style={{ color: agent.color }} />
                    {cap}
                  </li>
                ))}
              </ul>
            </div>

            {/* Status indicator */}
            <div className="mt-3 pt-3 border-t border-slate-700/50 flex items-center gap-2">
              <span 
                className="w-2 h-2 rounded-full animate-pulse"
                style={{ backgroundColor: '#22c55e' }}
              />
              <span className="text-xs text-green-400">Online & Ready</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default DepartmentalEcosystem
