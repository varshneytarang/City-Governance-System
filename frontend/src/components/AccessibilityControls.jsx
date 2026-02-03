import React from 'react'
import { motion } from 'framer-motion'
import { Zap, Contrast } from 'lucide-react'

const AccessibilityControls = ({ 
  reducedMotion, 
  setReducedMotion, 
  highContrast, 
  setHighContrast 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="fixed top-6 right-6 z-50 flex gap-3"
    >
      <button
        onClick={() => setReducedMotion(!reducedMotion)}
        className={`professional-card p-3 rounded-lg hover:shadow-soft transition-all ${
          reducedMotion ? 'bg-professional-green/10 ring-2 ring-professional-green' : ''
        }`}
        aria-label="Toggle reduced motion"
        title={reducedMotion ? 'Enable animations' : 'Reduce motion'}
      >
        <Zap className={reducedMotion ? 'text-professional-green' : 'text-gov-navy'} size={20} />
      </button>

      <button
        onClick={() => setHighContrast(!highContrast)}
        className={`professional-card p-3 rounded-lg hover:shadow-soft transition-all ${
          highContrast ? 'bg-accent-gold/10 ring-2 ring-accent-gold' : ''
        }`}
        aria-label="Toggle high contrast"
        title={highContrast ? 'Normal contrast' : 'High contrast'}
      >
        <Contrast className={highContrast ? 'text-accent-gold' : 'text-gov-navy'} size={20} />
      </button>
    </motion.div>
  )
}

export default AccessibilityControls
