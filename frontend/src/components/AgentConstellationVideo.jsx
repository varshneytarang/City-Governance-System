import React, { useRef, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Play, Pause } from 'lucide-react'

/**
 * Video-based Agent Constellation
 * Replaces the heavy animation component with an optimized video loop
 */
const AgentConstellationVideo = ({ reducedMotion = false }) => {
  const videoRef = useRef(null)
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [isPlaying, setIsPlaying] = useState(true)
  const [isLoaded, setIsLoaded] = useState(false)

  // Play/pause based on visibility and reduced motion preference
  useEffect(() => {
    if (!videoRef.current) return

    if (reducedMotion) {
      videoRef.current.pause()
      setIsPlaying(false)
    } else if (inView && isPlaying) {
      videoRef.current.play().catch(err => {
        console.log('Video autoplay prevented:', err)
      })
    } else if (!inView) {
      videoRef.current.pause()
    }
  }, [inView, reducedMotion, isPlaying])

  const togglePlayPause = () => {
    if (!videoRef.current) return

    if (videoRef.current.paused) {
      videoRef.current.play()
      setIsPlaying(true)
    } else {
      videoRef.current.pause()
      setIsPlaying(false)
    }
  }

  const handleVideoLoad = () => {
    setIsLoaded(true)
  }

  return (
    <section className="relative py-24 px-6 overflow-hidden bg-gradient-to-br from-neutral-lightBg to-neutral-offWhite">
      {/* Background effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gov-blue/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-gold/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-display font-bold text-gov-darkBlue mb-6">
            Multi-Agent Coordination System
          </h2>
          <p className="text-xl text-gov-gray max-w-3xl mx-auto">
            Watch how our intelligent agents work in perfect harmony, orchestrating 
            city services through AI-powered coordination
          </p>
        </motion.div>

        {/* Video Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative max-w-5xl mx-auto"
        >
          <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-gradient-to-br from-gov-blue/10 to-accent-gold/5">
            {/* Loading skeleton */}
            {!isLoaded && (
              <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse flex items-center justify-center">
                <div className="text-gov-gray text-lg">Loading visualization...</div>
              </div>
            )}

            {/* Video Element */}
            <video
              ref={videoRef}
              className={`w-full h-auto transition-opacity duration-500 ${
                isLoaded ? 'opacity-100' : 'opacity-0'
              }`}
              loop
              muted
              playsInline
              preload="auto"
              poster="/videos/agent-constellation-poster.jpg"
              onLoadedData={handleVideoLoad}
              onError={() => console.error('Video failed to load')}
            >
              {/* Multiple sources for browser compatibility */}
              <source src="/videos/agent-constellation-loop.mp4" type="video/mp4" />
              <source src="/videos/agent-constellation-loop.webm" type="video/webm" />
              
              {/* Fallback for browsers without video support */}
              <img 
                src="/videos/agent-constellation-poster.jpg" 
                alt="Agent Constellation showing six city department agents orbiting around a central coordination hub" 
                className="w-full h-auto"
              />
            </video>

            {/* Decorative overlay gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/10 via-transparent to-transparent pointer-events-none" />

            {/* Play/Pause Control (optional) */}
            {!reducedMotion && (
              <button
                onClick={togglePlayPause}
                className="absolute bottom-6 right-6 w-12 h-12 bg-white/90 backdrop-blur-sm rounded-full shadow-lg flex items-center justify-center hover:bg-white transition-all duration-300 group"
                aria-label={isPlaying ? 'Pause animation' : 'Play animation'}
              >
                {isPlaying ? (
                  <Pause className="text-gov-blue group-hover:scale-110 transition-transform" size={20} />
                ) : (
                  <Play className="text-gov-blue group-hover:scale-110 transition-transform ml-0.5" size={20} />
                )}
              </button>
            )}

            {/* Reduced Motion Indicator */}
            {reducedMotion && (
              <div className="absolute top-6 left-6 px-4 py-2 bg-white/90 backdrop-blur-sm rounded-full text-sm text-gov-gray">
                Animation paused (reduced motion)
              </div>
            )}
          </div>

          {/* Caption */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-center mt-6 text-gov-gray text-sm"
          >
            Six specialized agents — Water, Fire, Engineering, Health, Finance, and Sanitation — 
            continuously collaborate through our central coordination system
          </motion.p>
        </motion.div>

        {/* Agent Legend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 max-w-4xl mx-auto"
        >
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: 'Water', color: '#60a5fa' },
              { name: 'Fire', color: '#fb923c' },
              { name: 'Engineering', color: '#2dd4bf' },
              { name: 'Health', color: '#f472b6' },
              { name: 'Finance', color: '#fbbf24' },
              { name: 'Sanitation', color: '#a78bfa' },
            ].map((agent) => (
              <div
                key={agent.name}
                className="flex items-center gap-3 p-3 rounded-lg bg-white/50 backdrop-blur-sm border border-gray-200/50"
              >
                <div
                  className="w-4 h-4 rounded-full shadow-lg"
                  style={{
                    backgroundColor: agent.color,
                    boxShadow: `0 0 12px ${agent.color}60`,
                  }}
                />
                <span className="text-sm font-medium text-gov-slate">{agent.name}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default AgentConstellationVideo
