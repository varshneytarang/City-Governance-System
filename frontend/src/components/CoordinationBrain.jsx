import React, { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Brain, Network, Zap } from 'lucide-react'

const CoordinationBrain = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.3, triggerOnce: true })

  // Generate random particles with 3D positions
  const particles = useMemo(() => {
    return Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      z: Math.random() * 100,
      size: Math.random() * 4 + 2,
      duration: Math.random() * 10 + 5,
      delay: Math.random() * 5,
      color: ['#3b82f6', '#14b8a6', '#f59e0b', '#8b5cf6'][Math.floor(Math.random() * 4)]
    }))
  }, [])

  // Generate orbital paths
  const orbitPaths = useMemo(() => {
    return Array.from({ length: 5 }, (_, i) => ({
      id: i,
      radius: 30 + i * 15,
      duration: 15 + i * 3,
      offset: (i * 360) / 5,
      particles: Array.from({ length: 3 + i }, (_, j) => ({
        id: `${i}-${j}`,
        angle: (j * 360) / (3 + i),
        size: Math.random() * 6 + 3,
        color: ['#3b82f6', '#14b8a6', '#f59e0b'][i % 3]
      }))
    }))
  }, [])

  return (
    <section ref={ref} className="relative py-32 px-6 bg-gradient-to-br from-neutral-lightBg to-neutral-offWhite overflow-hidden">
      {/* Ambient background effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gov-blue/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-gold/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          {/* Left: Autonomous 3D Particle Universe */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="relative"
          >
            <div className="relative w-full aspect-square max-w-lg mx-auto">
              {/* 3D Perspective Container */}
              <div 
                className="absolute inset-0 overflow-hidden rounded-2xl"
                style={{ 
                  perspective: '1000px',
                  transformStyle: 'preserve-3d'
                }}
              >
                {/* Central Pulsing Core */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                  <motion.div
                    className="relative w-32 h-32"
                    animate={!reducedMotion ? {
                      rotate: [0, 360],
                      scale: [1, 1.1, 1]
                    } : {}}
                    transition={{
                      rotate: { duration: 20, repeat: Infinity, ease: 'linear' },
                      scale: { duration: 3, repeat: Infinity, ease: 'easeInOut' }
                    }}
                  >
                    {/* Core glow layers */}
                    {[...Array(3)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="absolute inset-0 rounded-full"
                        style={{
                          background: `radial-gradient(circle, rgba(59, 130, 246, ${0.4 - i * 0.1}) 0%, transparent 70%)`,
                          filter: 'blur(15px)'
                        }}
                        animate={!reducedMotion ? {
                          scale: [1, 1.5 + i * 0.3, 1],
                          opacity: [0.6, 0.2, 0.6]
                        } : {}}
                        transition={{
                          duration: 3 + i,
                          repeat: Infinity,
                          delay: i * 0.5
                        }}
                      />
                    ))}
                    
                    {/* Core icon */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <motion.div
                        className="w-20 h-20 rounded-full bg-gradient-to-br from-gov-blue to-blue-600 shadow-2xl flex items-center justify-center"
                        animate={!reducedMotion ? {
                          boxShadow: [
                            '0 0 20px rgba(59, 130, 246, 0.5)',
                            '0 0 40px rgba(59, 130, 246, 0.8)',
                            '0 0 20px rgba(59, 130, 246, 0.5)'
                          ]
                        } : {}}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <Brain className="text-white" size={40} />
                      </motion.div>
                    </div>
                  </motion.div>
                </div>

                {/* Orbital Rings with Particles */}
                {orbitPaths.map((orbit) => (
                  <div key={orbit.id} className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                    {/* Orbit ring */}
                    <motion.div
                      className="absolute rounded-full border border-gov-blue/10"
                      style={{
                        width: `${orbit.radius * 2}%`,
                        height: `${orbit.radius * 2}%`,
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                      }}
                      animate={!reducedMotion ? {
                        rotate: [orbit.offset, orbit.offset + 360],
                        opacity: [0.2, 0.4, 0.2]
                      } : {}}
                      transition={{
                        rotate: { duration: orbit.duration, repeat: Infinity, ease: 'linear' },
                        opacity: { duration: 3, repeat: Infinity }
                      }}
                    />

                    {/* Orbital particles */}
                    {orbit.particles.map((particle) => (
                      <motion.div
                        key={particle.id}
                        className="absolute rounded-full"
                        style={{
                          width: `${particle.size}px`,
                          height: `${particle.size}px`,
                          backgroundColor: particle.color,
                          boxShadow: `0 0 ${particle.size * 2}px ${particle.color}`,
                          left: '50%',
                          top: '50%',
                        }}
                        animate={!reducedMotion ? {
                          rotate: [particle.angle, particle.angle + 360],
                          x: [
                            Math.cos((particle.angle * Math.PI) / 180) * orbit.radius * 4,
                            Math.cos(((particle.angle + 360) * Math.PI) / 180) * orbit.radius * 4
                          ],
                          y: [
                            Math.sin((particle.angle * Math.PI) / 180) * orbit.radius * 4,
                            Math.sin(((particle.angle + 360) * Math.PI) / 180) * orbit.radius * 4
                          ],
                          scale: [1, 1.3, 1],
                        } : {}}
                        transition={{
                          rotate: { duration: orbit.duration, repeat: Infinity, ease: 'linear' },
                          x: { duration: orbit.duration, repeat: Infinity, ease: 'linear' },
                          y: { duration: orbit.duration, repeat: Infinity, ease: 'linear' },
                          scale: { duration: 2, repeat: Infinity, ease: 'easeInOut' }
                        }}
                      />
                    ))}
                  </div>
                ))}

                {/* 3D Floating Particles */}
                {!reducedMotion && particles.map((particle) => (
                  <motion.div
                    key={particle.id}
                    className="absolute rounded-full pointer-events-none"
                    style={{
                      width: `${particle.size}px`,
                      height: `${particle.size}px`,
                      backgroundColor: particle.color,
                      filter: `blur(${particle.size * 0.3}px)`,
                      left: `${particle.x}%`,
                      top: `${particle.y}%`,
                    }}
                    initial={{
                      opacity: 0,
                      scale: 0,
                      z: particle.z
                    }}
                    animate={inView ? {
                      opacity: [0, 0.8, 0],
                      scale: [0, 1, 0],
                      x: [0, (Math.random() - 0.5) * 300],
                      y: [0, (Math.random() - 0.5) * 300],
                      z: [particle.z, particle.z + 50, particle.z],
                      rotateX: [0, 360],
                      rotateY: [0, 360],
                    } : {}}
                    transition={{
                      duration: particle.duration,
                      delay: particle.delay,
                      repeat: Infinity,
                      ease: 'easeInOut'
                    }}
                  />
                ))}

                {/* Data Stream Lines */}
                {!reducedMotion && (
                  <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
                    {[...Array(8)].map((_, i) => {
                      const angle = (i * 360) / 8
                      const x1 = 50 + Math.cos((angle * Math.PI) / 180) * 10
                      const y1 = 50 + Math.sin((angle * Math.PI) / 180) * 10
                      const x2 = 50 + Math.cos((angle * Math.PI) / 180) * 45
                      const y2 = 50 + Math.sin((angle * Math.PI) / 180) * 45
                      
                      return (
                        <motion.line
                          key={i}
                          x1={`${x1}%`}
                          y1={`${y1}%`}
                          x2={`${x2}%`}
                          y2={`${y2}%`}
                          stroke="url(#gradient)"
                          strokeWidth="2"
                          initial={{ pathLength: 0, opacity: 0 }}
                          animate={{
                            pathLength: [0, 1, 0],
                            opacity: [0, 0.6, 0]
                          }}
                          transition={{
                            duration: 3,
                            delay: i * 0.3,
                            repeat: Infinity,
                            ease: 'easeInOut'
                          }}
                        />
                      )
                    })}
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
                        <stop offset="50%" stopColor="#3b82f6" stopOpacity="1" />
                        <stop offset="100%" stopColor="#14b8a6" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                  </svg>
                )}

                {/* Energy Bursts */}
                {!reducedMotion && [...Array(4)].map((_, i) => (
                  <motion.div
                    key={`burst-${i}`}
                    className="absolute top-1/2 left-1/2"
                    style={{
                      width: '200px',
                      height: '200px',
                      marginLeft: '-100px',
                      marginTop: '-100px',
                    }}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{
                      opacity: [0, 0.3, 0],
                      scale: [0, 2, 0],
                      rotate: [0, 180]
                    }}
                    transition={{
                      duration: 4,
                      delay: i * 1,
                      repeat: Infinity,
                      ease: 'easeOut'
                    }}
                  >
                    <div 
                      className="w-full h-full rounded-full border-2"
                      style={{
                        borderColor: ['#3b82f6', '#14b8a6', '#f59e0b', '#8b5cf6'][i],
                        boxShadow: `0 0 50px ${['#3b82f6', '#14b8a6', '#f59e0b', '#8b5cf6'][i]}40`
                      }}
                    />
                  </motion.div>
                ))}
              </div>

              {/* Status Text */}
              <motion.div
                className="absolute -bottom-12 left-0 right-0 text-center"
                initial={{ opacity: 0 }}
                animate={inView ? { opacity: 1 } : {}}
                transition={{ delay: 1 }}
              >
                <div className="flex items-center justify-center gap-2 text-xs text-gov-gray/60">
                  <motion.div
                    className="w-1.5 h-1.5 rounded-full bg-neon-emerald"
                    animate={!reducedMotion ? {
                      scale: [1, 1.5, 1],
                      opacity: [0.5, 1, 0.5]
                    } : {}}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <span className="font-mono">AUTONOMOUS COORDINATION ACTIVE</span>
                  <motion.div
                    className="w-1.5 h-1.5 rounded-full bg-neon-emerald"
                    animate={!reducedMotion ? {
                      scale: [1, 1.5, 1],
                      opacity: [0.5, 1, 0.5]
                    } : {}}
                    transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                  />
                </div>
              </motion.div>
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
