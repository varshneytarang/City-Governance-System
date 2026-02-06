import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles } from 'lucide-react'

/**
 * Message Suggestions Component
 * Shows smart autocomplete suggestions based on user input
 */
const MessageSuggestions = ({ suggestions, onSelect, isVisible }) => {
  if (!isVisible || suggestions.length === 0) return null
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden z-10"
      >
        <div className="px-3 py-2 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200 flex items-center gap-2">
          <Sparkles size={14} className="text-purple-500" />
          <span className="text-xs font-semibold text-gray-700">Smart Suggestions</span>
        </div>
        <div className="max-h-48 overflow-y-auto">
          {suggestions.map((suggestion, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => onSelect(suggestion)}
              className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-b-0 flex items-start gap-2"
            >
              <span className="text-gray-400 text-xs mt-0.5">→</span>
              <span className="text-gray-700 flex-1">{suggestion}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

export default MessageSuggestions
