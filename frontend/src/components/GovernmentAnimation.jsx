import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

const GovernmentAnimation = ({ type }) => {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width = canvas.offsetWidth * window.devicePixelRatio
    const height = canvas.height = canvas.offsetHeight * window.devicePixelRatio
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

    // Particle network system
    class Particle {
      constructor() {
        this.reset()
      }

      reset() {
        this.x = Math.random() * (width / window.devicePixelRatio)
        this.y = Math.random() * (height / window.devicePixelRatio)
        this.vx = (Math.random() - 0.5) * 0.5
        this.vy = (Math.random() - 0.5) * 0.5
        this.radius = Math.random() * 2 + 1
      }

      update() {
        this.x += this.vx
        this.y += this.vy

        if (this.x < 0 || this.x > width / window.devicePixelRatio) this.vx *= -1
        if (this.y < 0 || this.y > height / window.devicePixelRatio) this.vy *= -1
      }

      draw() {
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(59, 130, 246, 0.6)'
        ctx.fill()
      }
    }

    // Create particles
    const particles = Array.from({ length: 60 }, () => new Particle())

    // Animation loop
    let animationId
    const animate = () => {
      ctx.clearRect(0, 0, width / window.devicePixelRatio, height / window.devicePixelRatio)

      // Update and draw particles
      particles.forEach(particle => {
        particle.update()
        particle.draw()
      })

      // Connect nearby particles
      particles.forEach((p1, i) => {
        particles.slice(i + 1).forEach(p2 => {
          const dx = p1.x - p2.x
          const dy = p1.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < 120) {
            ctx.beginPath()
            ctx.moveTo(p1.x, p1.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.strokeStyle = `rgba(59, 130, 246, ${0.2 * (1 - dist / 120)})`
            ctx.lineWidth = 1
            ctx.stroke()
          }
        })
      })

      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => cancelAnimationFrame(animationId)
  }, [])

  return (
    <div className="government-animation">
      {/* Background Canvas */}
      <canvas ref={canvasRef} className="animation-canvas" />

      {/* City Buildings */}
      <div className="city-container">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="building"
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ 
              delay: i * 0.1,
              duration: 0.8,
              ease: "easeOut"
            }}
            style={{
              left: `${15 + i * 17}%`,
              height: `${40 + Math.random() * 30}%`,
              width: '12%'
            }}
          >
            {/* Building windows */}
            <div className="building-windows">
              {[...Array(Math.floor(Math.random() * 6) + 4)].map((_, j) => (
                <motion.div
                  key={j}
                  className="window"
                  animate={{
                    opacity: [0.3, 1, 0.3],
                  }}
                  transition={{
                    duration: 2 + Math.random() * 2,
                    repeat: Infinity,
                    delay: Math.random() * 2
                  }}
                />
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Government Logo/Icon */}
      <motion.div
        className="gov-icon"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
      >
        <svg viewBox="0 0 200 200" className="gov-logo">
          {/* Shield */}
          <motion.path
            d="M100 20 L150 40 L150 90 Q150 130 100 170 Q50 130 50 90 L50 40 Z"
            fill="none"
            stroke="rgba(59, 130, 246, 0.8)"
            strokeWidth="3"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
          
          {/* Building icon inside shield */}
          <motion.rect
            x="85"
            y="70"
            width="30"
            height="50"
            fill="rgba(59, 130, 246, 0.3)"
            stroke="rgba(59, 130, 246, 0.8)"
            strokeWidth="2"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 1, duration: 0.5 }}
          />
          
          {/* Windows */}
          {[...Array(6)].map((_, i) => (
            <motion.rect
              key={i}
              x={88 + (i % 2) * 12}
              y={75 + Math.floor(i / 2) * 12}
              width="6"
              height="6"
              fill="rgba(59, 130, 246, 0.8)"
              initial={{ opacity: 0 }}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{
                delay: 1.2 + i * 0.1,
                duration: 1.5,
                repeat: Infinity
              }}
            />
          ))}
        </svg>
      </motion.div>

      {/* Data Flow Lines */}
      {type === 'login' && (
        <div className="data-flow">
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="data-line"
              initial={{ scaleY: 0, opacity: 0 }}
              animate={{ 
                scaleY: [0, 1, 1, 0],
                opacity: [0, 1, 1, 0]
              }}
              transition={{
                duration: 3,
                delay: i * 0.3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              style={{
                left: `${10 + i * 11}%`,
              }}
            />
          ))}
        </div>
      )}

      {/* Agent Network for Register */}
      {type === 'register' && (
        <div className="agent-network">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="agent-node"
              initial={{ scale: 0 }}
              animate={{ 
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 2,
                delay: i * 0.2,
                repeat: Infinity,
                repeatDelay: 1
              }}
              style={{
                left: `${20 + (i % 3) * 30}%`,
                top: `${30 + Math.floor(i / 3) * 35}%`
              }}
            >
              <div className="agent-pulse" />
            </motion.div>
          ))}
        </div>
      )}

      {/* Floating Documents */}
      <div className="floating-documents">
        {[...Array(4)].map((_, i) => (
          <motion.div
            key={i}
            className="document"
            initial={{ y: '100%', x: `${i * 25}%`, opacity: 0 }}
            animate={{ 
              y: ['-20%', '-120%'],
              opacity: [0, 1, 1, 0]
            }}
            transition={{
              duration: 8,
              delay: i * 2,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </motion.div>
        ))}
      </div>

      {/* Info Text Overlay */}
      <motion.div 
        className="animation-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        <h2>{type === 'login' ? 'Secure Access' : 'Join the Network'}</h2>
        <p>
          {type === 'login' 
            ? 'AI-powered city governance at your fingertips' 
            : 'Be part of the intelligent city management system'}
        </p>
      </motion.div>
    </div>
  )
}

export default GovernmentAnimation
