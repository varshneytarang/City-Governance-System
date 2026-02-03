import React, { useRef } from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { ChevronRight, Brain, Shield, User, CheckCircle2 } from 'lucide-react'

const phases = [
  { id: 1, name: 'Request Input', type: 'human', icon: User },
  { id: 2, name: 'Context Gather', type: 'llm', icon: Brain },
  { id: 3, name: 'Agent Analysis', type: 'agent', icon: Shield },
  { id: 4, name: 'Rule Check', type: 'rule', icon: CheckCircle2 },
  { id: 5, name: 'LLM Reasoning', type: 'llm', icon: Brain },
  { id: 6, name: 'Coordination', type: 'agent', icon: Shield },
  { id: 7, name: 'Conflict Check', type: 'rule', icon: CheckCircle2 },
  { id: 8, name: 'LLM Decision', type: 'llm', icon: Brain },
  { id: 9, name: 'Validation', type: 'rule', icon: CheckCircle2 },
  { id: 10, name: 'Human Review', type: 'human', icon: User },
  { id: 11, name: 'Approval', type: 'human', icon: User },
  { id: 12, name: 'Execute', type: 'agent', icon: Shield },
  { id: 13, name: 'Monitor', type: 'agent', icon: Shield },
  { id: 14, name: 'Log Decision', type: 'rule', icon: CheckCircle2 },
  { id: 15, name: 'Complete', type: 'llm', icon: Brain },
]

const typeColors = {
  human: { bg: 'bg-molten-gold/20', text: 'text-molten-gold', border: 'border-molten-gold/50' },
  llm: { bg: 'bg-electric-sapphire/20', text: 'text-electric-sapphire', border: 'border-electric-sapphire/50' },
  agent: { bg: 'bg-nebula-violet/20', text: 'text-nebula-violet', border: 'border-nebula-violet/50' },
  rule: { bg: 'bg-neon-emerald/20', text: 'text-neon-emerald', border: 'border-neon-emerald/50' },
}

const WorkflowPipeline = ({ reducedMotion }) => {
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true })
  const scrollRef = useRef(null)

  return (
    <section ref={ref} className="relative py-32 px-6 bg-cosmic-midnight/30">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-6xl font-bold font-heading mb-6">
            <span className="text-gradient">Decision Workflow</span>
          </h2>
          <p className="text-xl text-gov-gray max-w-3xl mx-auto">
            15-phase intelligent pipeline combining LLM reasoning, rule-based validation, and human oversight
          </p>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <LegendItem icon={<Brain size={16} />} label="LLM Processing" color="electric-sapphire" />
            <LegendItem icon={<CheckCircle2 size={16} />} label="Rule Engine" color="neon-emerald" />
            <LegendItem icon={<Shield size={16} />} label="Agent Action" color="nebula-violet" />
            <LegendItem icon={<User size={16} />} label="Human Oversight" color="molten-gold" />
          </div>
        </motion.div>

        {/* Pipeline - Horizontal Scroll */}
        <div className="relative">
          <div
            ref={scrollRef}
            className="overflow-x-auto pb-8 hide-scrollbar"
            style={{ scrollbarWidth: 'thin' }}
          >
            <div className="flex gap-6 min-w-max px-4">
              {phases.map((phase, index) => (
                <React.Fragment key={phase.id}>
                  {/* Phase Node */}
                  <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={inView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: index * 0.05 }}
                    className="flex-shrink-0"
                  >
                    <PhaseNode phase={phase} reducedMotion={reducedMotion} />
                  </motion.div>

                  {/* Connector Arrow */}
                  {index < phases.length - 1 && (
                    <motion.div
                      initial={{ scaleX: 0 }}
                      animate={inView ? { scaleX: 1 } : {}}
                      transition={{ duration: 0.3, delay: index * 0.05 + 0.3 }}
                      className="flex items-center"
                    >
                      <ChevronRight className="text-gray-600" size={32} />
                    </motion.div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Scroll Indicator */}
          <div className="text-center mt-4 text-sm text-gray-400">
            ← Scroll horizontally to see all 15 phases →
          </div>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16"
        >
          <PipelineStat value="~2.3s" label="Avg. Pipeline Time" />
          <PipelineStat value="15" label="Processing Phases" />
          <PipelineStat value="100%" label="Decisions Logged" />
          <PipelineStat value="3" label="Human Checkpoints" />
        </motion.div>
      </div>
    </section>
  )
}

const PhaseNode = ({ phase, reducedMotion }) => {
  const Icon = phase.icon
  const colors = typeColors[phase.type]

  return (
    <div className={`w-48 ${colors.bg} ${colors.border} border-2 rounded-xl p-4 glass-morphism ${
      reducedMotion ? '' : 'hover:scale-105'
    } transition-transform cursor-pointer`}>
      <div className="flex items-center justify-center mb-3">
        <div className={`w-12 h-12 rounded-full ${colors.bg} ${colors.border} border flex items-center justify-center`}>
          <Icon className={colors.text} size={24} />
        </div>
      </div>
      <h3 className={`text-center font-bold text-sm ${colors.text} mb-1`}>
        Phase {phase.id}
      </h3>
      <p className="text-center text-xs text-gray-300">
        {phase.name}
      </p>
    </div>
  )
}

const LegendItem = ({ icon, label, color }) => (
  <div className="flex items-center gap-2 glass-morphism px-3 py-2 rounded-lg">
    <span className={`text-${color}`} style={{ color: `var(--${color})` }}>
      {icon}
    </span>
    <span className="text-xs font-medium">{label}</span>
  </div>
)

const PipelineStat = ({ value, label }) => (
  <div className="glass-morphism p-6 rounded-xl text-center">
    <div className="text-3xl font-bold text-gradient mb-2">{value}</div>
    <div className="text-sm text-gray-400">{label}</div>
  </div>
)

export default WorkflowPipeline
