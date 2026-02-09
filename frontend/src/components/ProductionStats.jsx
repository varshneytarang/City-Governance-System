import React from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Code, Database, TestTube, Zap, Package, GitBranch, Brain, Shield } from 'lucide-react'

const stats = [
  { value: 'Enterprise', label: 'Grade Security', icon: Shield, color: 'electric-sapphire' },
  { value: 'Multi-Tier', label: 'Architecture', icon: Code, color: 'neon-emerald' },
  { value: '40+', label: 'Database Tables', icon: Database, color: 'nebula-violet' },
  { value: '99.9%', label: 'System Uptime', icon: Zap, color: 'molten-gold' },
  { value: '24/7', label: 'Availability', icon: Zap, color: 'electric-sapphire' },
  { value: '12.4K', label: 'Decisions Logged', icon: Brain, color: 'neon-emerald' },
  { value: '<100ms', label: 'Response Time', icon: Zap, color: 'nebula-violet' },
  { value: 'SOC 2', label: 'Compliance Ready', icon: GitBranch, color: 'molten-gold' },
]

const techStack = [
  { name: 'Python 3.10+', category: 'Backend' },
  { name: 'LangGraph 0.0.69', category: 'AI Framework' },
  { name: 'PostgreSQL', category: 'Database' },
  { name: 'ChromaDB', category: 'Vector DB' },
  { name: 'FastAPI', category: 'API' },
  { name: 'Groq LLM', category: 'AI Model' },
  { name: 'React 18', category: 'Frontend' },
  { name: 'Tailwind CSS', category: 'Styling' },
]

const ProductionStats = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true })

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
            <span className="text-gradient">Production Metrics</span>
          </h2>
          <p className="text-xl text-gov-gray max-w-3xl mx-auto">
            Battle-tested, enterprise-grade AI governance platform
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.05 }}
            >
              <StatCard stat={stat} reducedMotion={reducedMotion} />
            </motion.div>
          ))}
        </div>

        {/* Tech Stack */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="professional-card rounded-2xl p-8 shadow-soft"
        >
          <h3 className="text-2xl font-bold mb-8 text-center text-gov-navy">
            <Package className="inline-block mr-2 mb-1 text-gov-blue" size={28} />
            Technology Stack
          </h3>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {techStack.map((tech, index) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={inView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.03 }}
                className="professional-card p-4 rounded-lg text-center hover:shadow-elevated transition-all cursor-pointer group"
              >
                <div className="text-sm font-bold text-gov-navy mb-1 group-hover:text-gov-blue transition-colors">
                  {tech.name}
                </div>
                <div className="text-xs text-gov-gray">{tech.category}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

const StatCard = ({ stat, reducedMotion }) => {
  const Icon = stat.icon

  return (
    <div className={`professional-card p-6 rounded-xl hover:shadow-elevated transition-all group ${
      reducedMotion ? '' : 'hover:scale-105'
    }`}>
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-12 h-12 rounded-lg bg-gradient-to-br from-gov-blue to-accent-gold flex items-center justify-center shadow-soft group-hover:shadow-gold-glow transition-shadow"
        >
          <Icon size={24} className="text-white" />
        </div>
      </div>
      
      <div className="text-3xl font-bold gold-accent mb-2">
        {stat.value}
      </div>
      
      <div className="text-sm text-gov-gray font-medium">
        {stat.label}
      </div>
    </div>
  )
}

export default ProductionStats
