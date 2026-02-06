import React, { useState } from 'react'
import { motion, useMotionValue, useTransform } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Brain, Network, Zap, Cpu, Server, Database } from 'lucide-react'

const CoordinationBrain = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.3, triggerOnce: true })
  const [activeNode, setActiveNode] = useState(null)
  const [hoveredNode, setHoveredNode] = useState(null)

  // Node positions and data
  const nodes = [
    { id: 'brain', x: 50, y: 35, icon: Brain, label: 'AI Core', color: '#3b82f6', size: 80 },
    { id: 'cpu1', x: 20, y: 15, icon: Cpu, label: 'Processor A', color: '#14b8a6', size: 60 },
    { id: 'cpu2', x: 80, y: 15, icon: Server, label: 'Processor B', color: '#14b8a6', size: 60 },
    { id: 'db1', x: 15, y: 60, icon: Database, label: 'Data Store', color: '#f59e0b', size: 60 },
    { id: 'net1', x: 50, y: 75, icon: Network, label: 'Network', color: '#8b5cf6', size: 60 },
    { id: 'db2', x: 85, y: 60, icon: Zap, label: 'Cache', color: '#f59e0b', size: 60 },
  ]

  const connections = [
    { from: 'brain', to: 'cpu1' },
    { from: 'brain', to: 'cpu2' },
    { from: 'brain', to: 'db1' },
    { from: 'brain', to: 'net1' },
    { from: 'brain', to: 'db2' },
    { from: 'cpu1', to: 'db1' },
    { from: 'cpu2', to: 'db2' },
    { from: 'db1', to: 'net1' },
    { from: 'net1', to: 'db2' },
  ]

  return (
    <section ref={ref} className="relative py-32 px-6 bg-gradient-to-br from-neutral-lightBg to-neutral-offWhite overflow-hidden">
      {/* Ambient background effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gov-blue/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-gold/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          {/* Left: Interactive Neural Network */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="relative"
          >
            <div className="relative w-full aspect-square max-w-lg mx-auto">
              {/* Connection Lines */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                {connections.map((conn, i) => {
                  const fromNode = nodes.find(n => n.id === conn.from)
                  const toNode = nodes.find(n => n.id === conn.to)
                  const isActive = activeNode === conn.from || activeNode === conn.to
                  const isHovered = hoveredNode === conn.from || hoveredNode === conn.to
                  
                  return (
                    <motion.line
                      key={`${conn.from}-${conn.to}`}
                      initial={{ pathLength: 0, opacity: 0 }}
                      animate={inView ? { 
                        pathLength: 1, 
                        opacity: isActive ? 0.8 : isHovered ? 0.5 : 0.2 
                      } : {}}
                      transition={{ 
                        pathLength: { duration: 1, delay: i * 0.1 },
                        opacity: { duration: 0.3 }
                      }}
                      x1={`${fromNode.x}%`}
                      y1={`${fromNode.y}%`}
                      x2={`${toNode.x}%`}
                      y2={`${toNode.y}%`}
                      stroke={isActive ? fromNode.color : '#3b82f6'}
                      strokeWidth={isActive ? 3 : 2}
                      strokeDasharray={isActive ? '0' : '4 4'}
                    />
                  )
                })}
              </svg>

              {/* Interactive Nodes */}
              {nodes.map((node, i) => (
                <InteractiveNode
                  key={node.id}
                  node={node}
                  index={i}
                  inView={inView}
                  reducedMotion={reducedMotion}
                  isActive={activeNode === node.id}
                  isHovered={hoveredNode === node.id}
                  onActivate={() => setActiveNode(activeNode === node.id ? null : node.id)}
                  onHover={() => setHoveredNode(node.id)}
                  onLeave={() => setHoveredNode(null)}
                />
              ))}

              {/* Floating Data Particles */}
              {!reducedMotion && activeNode && (
                <DataParticles activeNode={nodes.find(n => n.id === activeNode)} />
              )}
            </div>

            {/* Interactive Instruction */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 1.5 }}
              className="mt-6 text-center"
            >
              <p className="text-sm text-gov-gray/70 flex items-center justify-center gap-2">
                <motion.span
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-block w-2 h-2 rounded-full bg-gov-blue"
                />
                Drag nodes • Click to activate • Hover to explore
              </p>
            </motion.div>
          </motion.div>

          {/* Right: Content */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold font-heading mb-6">
              <span className="text-gradient">Coordination Intelligence</span>
            </h2>
            
            <p className="text-xl text-gov-gray mb-8 leading-relaxed">
              The LangGraph-powered coordination agent orchestrates all department agents, 
              detecting conflicts, prioritizing tasks, and ensuring harmonious city operations.
            </p>

            {/* Features */}
            <div className="space-y-4">
              <Feature
                icon={<Brain size={24} />}
                title="Intelligent Orchestration"
                description="Smart task routing and priority management across all agents"
              />
              <Feature
                icon={<Network size={24} />}
                title="Conflict Resolution"
                description="Automatic detection and resolution of inter-agent conflicts"
              />
              <Feature
                icon={<Zap size={24} />}
                title="Real-time Coordination"
                description="Instant communication and synchronization between departments"
              />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mt-8">
              <StatBox value="99.7%" label="Uptime" />
              <StatBox value="<100ms" label="Response" />
              <StatBox value="1,200+" label="Resolved" />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

// Interactive Draggable Node Component
const InteractiveNode = ({ 
  node, 
  index, 
  inView, 
  reducedMotion, 
  isActive, 
  isHovered,
  onActivate, 
  onHover, 
  onLeave 
}) => {
  const Icon = node.icon
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  // Transform for magnetic snap effect
  const magneticX = useTransform(x, [-100, 100], [-15, 15])
  const magneticY = useTransform(y, [-100, 100], [-15, 15])

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={inView ? { 
        scale: isActive ? 1.15 : isHovered ? 1.1 : 1, 
        opacity: 1 
      } : {}}
      transition={{ 
        duration: 0.5, 
        delay: 0.3 + index * 0.1,
        scale: { type: 'spring', stiffness: 300, damping: 20 }
      }}
      drag
      dragElastic={0.2}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
      whileHover={{ scale: 1.1, cursor: 'grab' }}
      whileTap={{ scale: 0.95, cursor: 'grabbing' }}
      onClick={onActivate}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      className="absolute z-10"
      style={{
        top: `${node.y}%`,
        left: `${node.x}%`,
        width: `${node.size}px`,
        height: `${node.size}px`,
        x: reducedMotion ? 0 : magneticX,
        y: reducedMotion ? 0 : magneticY,
      }}
    >
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Glow effect */}
        {(isActive || isHovered) && !reducedMotion && (
          <motion.div
            className="absolute inset-0 rounded-full blur-xl"
            style={{ backgroundColor: `${node.color}40` }}
            animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}

        {/* Main node */}
        <motion.div
          className="relative w-full h-full rounded-full professional-card shadow-professional flex items-center justify-center overflow-hidden"
          style={{
            background: isActive 
              ? `linear-gradient(135deg, ${node.color}20, ${node.color}10)`
              : 'linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7))',
            borderColor: isActive ? node.color : 'rgba(59, 130, 246, 0.2)',
            borderWidth: '2px',
            borderStyle: 'solid',
            boxShadow: isActive 
              ? `0 8px 32px ${node.color}40, 0 0 20px ${node.color}30`
              : '0 4px 20px rgba(0,0,0,0.1)',
          }}
        >
          <Icon 
            size={node.size * 0.4} 
            style={{ color: isActive ? node.color : '#3b82f6' }}
            className="relative z-10"
          />

          {/* Ripple effect on active */}
          {isActive && !reducedMotion && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{ border: `2px solid ${node.color}` }}
              initial={{ scale: 1, opacity: 1 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          )}
        </motion.div>

        {/* Label */}
        <motion.div
          className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered || isActive ? 1 : 0.7 }}
          transition={{ duration: 0.2 }}
        >
          <span 
            className="text-xs font-semibold px-2 py-1 rounded-full"
            style={{ 
              background: isActive ? `${node.color}20` : 'rgba(255,255,255,0.9)',
              color: isActive ? node.color : '#1e3a5f',
              border: `1px solid ${isActive ? node.color : 'transparent'}`,
            }}
          >
            {node.label}
          </span>
        </motion.div>
      </div>
    </motion.div>
  )
}

// Animated Data Particles
const DataParticles = ({ activeNode }) => {
  return (
    <>
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1.5 h-1.5 rounded-full pointer-events-none"
          style={{
            backgroundColor: activeNode.color,
            left: `${activeNode.x}%`,
            top: `${activeNode.y}%`,
            filter: `drop-shadow(0 0 4px ${activeNode.color})`,
          }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{
            x: [0, (Math.random() - 0.5) * 200],
            y: [0, (Math.random() - 0.5) * 200],
            scale: [0, 1, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 2,
            delay: i * 0.2,
            repeat: Infinity,
            ease: 'easeOut',
          }}
        />
      ))}
    </>
  )
}

const Feature = ({ icon, title, description }) => (
  <div className="flex gap-4">
    <div className="flex-shrink-0 w-12 h-12 rounded-lg professional-card shadow-soft flex items-center justify-center text-gov-blue">
      {icon}
    </div>
    <div>
      <h3 className="font-bold text-lg mb-1 text-gov-navy">{title}</h3>
      <p className="text-gov-gray text-sm">{description}</p>
    </div>
  </div>
)

const StatBox = ({ value, label }) => (
  <div className="professional-card p-4 rounded-lg text-center shadow-soft">
    <div className="text-2xl font-bold text-accent-gold mb-1">{value}</div>
    <div className="text-xs text-gov-gray">{label}</div>
  </div>
)

export default CoordinationBrain
