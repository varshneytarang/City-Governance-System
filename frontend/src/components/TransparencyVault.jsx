import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Search, Database, Shield, Lock } from 'lucide-react'

const decisions = [
  { id: 1, title: 'Emergency Water Main Repair', dept: 'Water', priority: 'high', timestamp: '2026-02-03 08:23' },
  { id: 2, title: 'Fire Station Resource Allocation', dept: 'Fire', priority: 'high', timestamp: '2026-02-03 07:15' },
  { id: 3, title: 'Infrastructure Assessment Bridge-7', dept: 'Engineering', priority: 'medium', timestamp: '2026-02-02 14:30' },
  { id: 4, title: 'Healthcare Facility Expansion', dept: 'Health', priority: 'medium', timestamp: '2026-02-02 11:45' },
  { id: 5, title: 'Budget Reallocation Q1', dept: 'Finance', priority: 'low', timestamp: '2026-02-01 16:20' },
  { id: 6, title: 'Waste Collection Route Optimization', dept: 'Sanitation', priority: 'medium', timestamp: '2026-02-01 09:10' },
]

const TransparencyVault = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.2, triggerOnce: true })
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDecision, setSelectedDecision] = useState(null)

  const filteredDecisions = decisions.filter(d =>
    d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.dept.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <section ref={ref} className="relative py-32 px-6 bg-white">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-6xl font-bold font-heading mb-6">
            <span className="text-gradient">Transparency Vault</span>
          </h2>
          <p className="text-xl text-gov-gray max-w-3xl mx-auto">
            Every decision tracked, logged, and stored in ChromaDB for complete transparency and accountability
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left: 3D Pyramid Vault */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8 }}
            className="relative"
          >
            <div className="relative w-full aspect-square max-w-md mx-auto perspective-1000">
              {/* Pyramid */}
              <div
                className={`relative w-full h-full ${
                  reducedMotion ? '' : 'animate-spin-slow'
                }`}
                style={{ transformStyle: 'preserve-3d' }}
              >
                <div className="absolute inset-0 bg-white/90 backdrop-blur-xl border-2 border-gov-blue/30 transform-gpu shadow-professional"
                     style={{
                       clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)',
                       transform: 'rotateX(60deg) rotateZ(45deg)',
                       boxShadow: '0 0 60px rgba(59, 130, 246, 0.3)',
                     }}>
                  {/* Inner crystals */}
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-8 h-8 bg-accent-gold/60 rounded"
                      style={{
                        top: `${20 + i * 15}%`,
                        left: `${25 + (i % 2) * 25}%`,
                        boxShadow: '0 0 20px rgba(212, 175, 55, 0.6)',
                      }}
                      animate={reducedMotion ? {} : {
                        y: [0, -10, 0],
                        rotate: [0, 180, 360],
                      }}
                      transition={{
                        duration: 4,
                        delay: i * 0.5,
                        repeat: Infinity,
                      }}
                    />
                  ))}
                </div>
              </div>

              {/* Vault Label */}
              <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-center w-full">
                <p className="text-sm font-bold text-gov-blue mb-2">Decision Crystals</p>
                <div className="flex justify-center gap-6 text-xs text-gov-gray">
                  <span className="flex items-center gap-1">
                    <Lock size={12} /> Immutable
                  </span>
                  <span className="flex items-center gap-1">
                    <Shield size={12} /> Verified
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right: Search & Decisions */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            {/* Search Bar */}
            <div className="mb-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gov-gray" size={20} />
                <input
                  type="text"
                  placeholder="Search decisions... (try 'emergency', 'water', 'fire')"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 professional-card rounded-lg text-gov-navy placeholder-gov-lightGray focus:outline-none focus:ring-2 focus:ring-gov-blue shadow-soft"
                />
              </div>
            </div>

            {/* Decision List */}
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
              <AnimatePresence mode="popLayout">
                {filteredDecisions.map((decision, index) => (
                  <motion.div
                    key={decision.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    onClick={() => setSelectedDecision(decision.id === selectedDecision ? null : decision.id)}
                    className={`professional-card p-4 rounded-lg cursor-pointer transition-all hover:shadow-elevated ${
                      selectedDecision === decision.id ? 'ring-2 ring-accent-gold shadow-gold-glow' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-bold text-sm mb-1 text-gov-navy">{decision.title}</h3>
                        <div className="flex items-center gap-3 text-xs text-gov-gray">
                          <span className="flex items-center gap-1">
                            <Database size={12} />
                            {decision.dept}
                          </span>
                          <span>{decision.timestamp}</span>
                        </div>
                      </div>
                      <PriorityBadge priority={decision.priority} />
                    </div>

                    {/* Expanded Details */}
                    {selectedDecision === decision.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="mt-3 pt-3 border-t border-gray-200 text-xs text-gov-gray"
                      >
                        <p className="mb-2">
                          <strong>Vector ID:</strong> chroma_{decision.id}_{Math.random().toString(36).substr(2, 9)}
                        </p>
                        <p>
                          <strong>Reasoning:</strong> AI-driven analysis with 95% confidence based on historical data and real-time sensor inputs.
                        </p>
                      </motion.div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>

              {filteredDecisions.length === 0 && (
                <div className="text-center py-12 text-gov-gray">
                  <Database size={48} className="mx-auto mb-4 opacity-30" />
                  <p>No decisions found matching "{searchTerm}"</p>
                </div>
              )}
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-4 mt-8">
              <MetricCard value="12.4K" label="Total Decisions" />
              <MetricCard value="100%" label="Logged" />
              <MetricCard value="<5s" label="Retrieval Time" />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

const PriorityBadge = ({ priority }) => {
  const colors = {
    high: 'bg-red-500/20 text-red-400 ring-red-500/30',
    medium: 'bg-yellow-500/20 text-yellow-400 ring-yellow-500/30',
    low: 'bg-green-500/20 text-green-400 ring-green-500/30',
  }

  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold ring-1 ${colors[priority]}`}>
      {priority.toUpperCase()}
    </span>
  )
}

const MetricCard = ({ value, label }) => (
  <div className="professional-card p-3 rounded-lg text-center shadow-soft">
    <div className="text-xl font-bold text-accent-gold mb-1">{value}</div>
    <div className="text-xs text-gov-gray">{label}</div>
  </div>
)

export default TransparencyVault
