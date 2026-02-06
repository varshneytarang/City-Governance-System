import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useInView } from 'react-intersection-observer'
import { Sparkles, TrendingUp, LogIn, UserPlus } from 'lucide-react'

const Hero = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true })
  const navigate = useNavigate()
  const [stats, setStats] = useState({ agents: 0, lines: 0, coverage: 0 })

  useEffect(() => {
    if (inView && !reducedMotion) {
      // Animate counters - slower and smoother
      const duration = 3500
      const startTime = Date.now()

      const animate = () => {
        const now = Date.now()
        const progress = Math.min((now - startTime) / duration, 1)
        // Gentler easing
        const easeOut = progress * (2 - progress)

        setStats({
          agents: Math.floor(easeOut * 6),
          lines: Math.floor(easeOut * 15000),
          coverage: Math.floor(easeOut * 90)
        })

        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }

      animate()
    } else if (inView) {
      setStats({ agents: 6, lines: 15000, coverage: 90 })
    }
  }, [inView, reducedMotion])

  return (
    <section ref={ref} className="relative min-h-screen flex items-center justify-center px-6 py-20 bg-gradient-to-br from-neutral-offWhite via-neutral-cream to-neutral-lightBg">
      <div className="max-w-6xl mx-auto text-center">
        {/* Subtitle */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="mb-6"
        >
          <span className="inline-flex items-center gap-2 px-5 py-2.5 professional-card rounded-full text-sm font-semibold text-gov-navy border-2 border-gov-blue/20">
            <Sparkles size={16} className="text-accent-gold" />
            Multi-Agent Autonomous System
          </span>
        </motion.div>

        {/* Main Title */}
        <h1
          className="text-5xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight select-none"
          style={{ 
            minHeight: '240px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <span className="block pointer-events-none font-heading" style={{ 
            lineHeight: '1.2',
            background: 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 40%, #d4af37 100%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            color: 'transparent'
          }}>
            Autonomous Intelligence
          </span>
          <span className="block text-gov-darkBlue mt-2 pointer-events-none font-heading" style={{ lineHeight: '1.2' }}>
            for Urban Evolution
          </span>
        </h1>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1.2, delay: 0.6, ease: "easeOut" }}
          className="text-lg md:text-xl text-gov-gray mb-12 max-w-3xl mx-auto leading-relaxed"
        >
          Six specialized AI agents orchestrated by LangGraph, making transparent, 
          data-driven decisions for modern city governance with full human oversight.
        </motion.p>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1.2, delay: 0.9, ease: "easeOut" }}
          className="flex flex-wrap justify-center gap-8 mb-12"
        >
          <StatCard 
            value={stats.agents} 
            label="Autonomous Agents" 
            suffix="" 
            reducedMotion={reducedMotion}
          />
          <StatCard 
            value={stats.lines} 
            label="Lines of Code" 
            suffix="+" 
            reducedMotion={reducedMotion}
          />
          <StatCard 
            value={stats.coverage} 
            label="Test Coverage" 
            suffix="%" 
            reducedMotion={reducedMotion}
          />
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ duration: 1.5, delay: 1.2, ease: "easeOut" }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          {/* Dashboard Button */}
          <button 
            onClick={() => navigate('/dashboard')}
            className="group relative px-10 py-5 bg-gov-navy text-white rounded-lg text-lg font-semibold overflow-hidden hover:shadow-elevated transition-all duration-500 border-2 border-accent-gold/30 hover:border-accent-gold"
          >
            <span className="relative z-10 flex items-center gap-3">
              Enter Dashboard
              <TrendingUp className={reducedMotion ? '' : 'group-hover:translate-x-1 transition-transform duration-500'} />
            </span>
            <div className={`absolute inset-0 bg-gradient-to-r from-gov-blue to-accent-gold opacity-0 ${reducedMotion ? '' : 'group-hover:opacity-15'} transition-opacity duration-500`}></div>
          </button>

          {/* Login Button */}
          <button 
            onClick={() => navigate('/login')}
            className="group relative px-8 py-5 bg-white text-gov-navy rounded-lg text-lg font-semibold overflow-hidden hover:shadow-elevated transition-all duration-500 border-2 border-gov-blue/30 hover:border-gov-blue"
          >
            <span className="relative z-10 flex items-center gap-2">
              <LogIn size={20} />
              Login
            </span>
            <div className={`absolute inset-0 bg-gov-blue/10 opacity-0 ${reducedMotion ? '' : 'group-hover:opacity-100'} transition-opacity duration-500`}></div>
          </button>

          {/* Register Button */}
          <button 
            onClick={() => navigate('/register')}
            className="group relative px-8 py-5 bg-gradient-to-r from-gov-blue to-accent-gold text-white rounded-lg text-lg font-semibold overflow-hidden hover:shadow-gold-glow transition-all duration-500"
          >
            <span className="relative z-10 flex items-center gap-2">
              <UserPlus size={20} />
              Sign Up
            </span>
            <div className={`absolute inset-0 bg-white/20 opacity-0 ${reducedMotion ? '' : 'group-hover:opacity-100'} transition-opacity duration-500`}></div>
          </button>
        </motion.div>
      </div>
    </section>
  )
}

const StatCard = ({ value, label, suffix, reducedMotion }) => (
  <div className="professional-card px-8 py-5 transition-all duration-500 hover:shadow-elevated hover:scale-105 group">
    <div className="text-3xl md:text-4xl font-bold mb-1 bg-gradient-to-r from-gov-navy via-gov-blue to-accent-gold bg-clip-text text-transparent">
      {value.toLocaleString()}{suffix}
    </div>
    <div className="text-sm text-gov-gray font-medium uppercase tracking-wide">{label}</div>
    <div className="h-1 w-0 bg-gradient-to-r from-gov-blue to-accent-gold group-hover:w-full transition-all duration-500 mt-3 rounded-full"></div>
  </div>
)

export default Hero
