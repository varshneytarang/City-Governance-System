import React from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Brain, Network, Zap } from 'lucide-react'

const CoordinationBrain = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.3, triggerOnce: true })

  const connections = [
    { from: { x: 50, y: 30 }, to: { x: 20, y: 20 }, delay: 0 },
    { from: { x: 50, y: 30 }, to: { x: 80, y: 20 }, delay: 0.1 },
    { from: { x: 50, y: 30 }, to: { x: 20, y: 50 }, delay: 0.2 },
    { from: { x: 50, y: 30 }, to: { x: 80, y: 50 }, delay: 0.3 },
    { from: { x: 50, y: 30 }, to: { x: 35, y: 70 }, delay: 0.4 },
    { from: { x: 50, y: 30 }, to: { x: 65, y: 70 }, delay: 0.5 },
  ]

  return (
    <section ref={ref} className="relative py-32 px-6 bg-gradient-to-br from-neutral-lightBg to-neutral-offWhite">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          {/* Left: Visual */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="relative"
          >
            <div className="relative w-full aspect-square max-w-lg mx-auto">
              {/* Central Brain */}
              <div className="absolute top-1/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className={`w-32 h-32 rounded-full professional-card shadow-professional flex items-center justify-center ${
                  reducedMotion ? '' : 'animate-pulse-slow'
                }`}>
                  <Brain size={64} className="text-gov-blue" />
                </div>
              </div>

              {/* Connection Nodes */}
              {connections.map((conn, i) => (
                <React.Fragment key={i}>
                  {/* Line */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none">
                    <motion.line
                      initial={{ pathLength: 0 }}
                      animate={inView && !reducedMotion ? { pathLength: 1 } : {}}
                      transition={{ duration: 1, delay: conn.delay }}
                      x1={`${conn.from.x}%`}
                      y1={`${conn.from.y}%`}
                      x2={`${conn.to.x}%`}
                      y2={`${conn.to.y}%`}
                      stroke="#3b82f6"
                      strokeWidth="2"
                      opacity="0.3"
                    />
                  </svg>
                  
                  {/* Endpoint */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={inView ? { scale: 1 } : {}}
                    transition={{ duration: 0.4, delay: conn.delay + 0.5 }}
                    className="absolute w-8 h-8 rounded-full bg-accent-gold/60 shadow-gold-glow"
                    style={{
                      top: `${conn.to.y}%`,
                      left: `${conn.to.x}%`,
                      transform: 'translate(-50%, -50%)'
                    }}
                  >
                    {!reducedMotion && (
                      <div className="absolute inset-0 rounded-full bg-neon-emerald animate-ping opacity-75"></div>
                    )}
                  </motion.div>
                </React.Fragment>
              ))}

              {/* Floating Particles */}
              {!reducedMotion && (
                <>
                  {[...Array(6)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 rounded-full bg-gov-blue"
                      style={{
                        top: `${Math.random() * 100}%`,
                        left: `${Math.random() * 100}%`,
                      }}
                      animate={{
                        y: [0, -20, 0],
                        opacity: [0.3, 1, 0.3],
                      }}
                      transition={{
                        duration: 3,
                        delay: i * 0.5,
                        repeat: Infinity,
                      }}
                    />
                  ))}
                </>
              )}
            </div>
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
