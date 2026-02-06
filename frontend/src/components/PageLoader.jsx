import React from 'react'
import { motion } from 'framer-motion'

const PageLoader = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#1e3a5f] to-[#0f172a] flex items-center justify-center">
      <div className="text-center">
        {/* Animated logo/spinner */}
        <motion.div
          className="relative w-24 h-24 mx-auto mb-8"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <div className="absolute inset-0 rounded-full border-4 border-[#3b82f6]/20" />
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-[#3b82f6] border-r-[#d4af37]" />
          <motion.div
            className="absolute inset-3 rounded-full bg-gradient-to-br from-[#3b82f6]/20 to-[#d4af37]/20"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </motion.div>

        {/* Loading text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-white mb-2">Loading...</h2>
          <p className="text-gray-400 text-sm">Please wait while we prepare your experience</p>
        </motion.div>

        {/* Loading dots */}
        <div className="flex justify-center gap-2 mt-6">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 rounded-full bg-[#3b82f6]"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default PageLoader
