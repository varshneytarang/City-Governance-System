import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Keyboard, Sparkles, Download, Search, ThumbsUp, Copy, Zap } from 'lucide-react'

/**
 * Chat Help Modal
 * Shows features, shortcuts, and tips for using the chatbot
 */
const ChatHelp = ({ isOpen, onClose, agentColor }) => {
  if (!isOpen) return null

  const features = [
    {
      icon: <Sparkles size={18} />,
      title: 'Smart Suggestions',
      description: 'Get intelligent suggestions as you type based on your agent type'
    },
    {
      icon: <Search size={18} />,
      title: 'Message Search',
      description: 'Search through conversation history with keyboard navigation'
    },
    {
      icon: <Download size={18} />,
      title: 'Export Chat',
      description: 'Download conversations in TXT, JSON, Markdown, CSV, or HTML format'
    },
    {
      icon: <ThumbsUp size={18} />,
      title: 'Feedback',
      description: 'Rate agent responses to help improve service quality'
    },
    {
      icon: <Copy size={18} />,
      title: 'Copy Messages',
      description: 'Easily copy any message to clipboard on hover'
    },
    {
      icon: <Zap size={18} />,
      title: 'Quick Actions',
      description: 'Use pre-defined templates for common requests'
    }
  ]

  const shortcuts = [
    { keys: ['Enter'], action: 'Send message' },
    { keys: ['Shift', 'Enter'], action: 'New line' },
    { keys: ['Ctrl', 'F'], action: 'Search messages' },
    { keys: ['Ctrl', 'K'], action: 'Clear chat' },
    { keys: ['Esc'], action: 'Close search/dialogs' }
  ]

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div
            className="px-6 py-4 border-b border-gray-200 flex items-center justify-between"
            style={{ background: `linear-gradient(135deg, ${agentColor}15, ${agentColor}05)` }}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center text-white"
                style={{ backgroundColor: agentColor }}
              >
                💡
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Chatbot Features</h2>
                <p className="text-sm text-gray-600">Tips to get the most out of your conversation</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(80vh-100px)]">
            {/* Features Section */}
            <div className="mb-8">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Sparkles size={20} style={{ color: agentColor }} />
                Available Features
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 bg-gray-50 rounded-xl border border-gray-200 hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className="p-2 rounded-lg text-white flex-shrink-0"
                        style={{ backgroundColor: agentColor }}
                      >
                        {feature.icon}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-1">{feature.title}</h4>
                        <p className="text-sm text-gray-600">{feature.description}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Keyboard Shortcuts */}
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Keyboard size={20} style={{ color: agentColor }} />
                Keyboard Shortcuts
              </h3>
              <div className="space-y-2">
                {shortcuts.map((shortcut, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.05 }}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <span className="text-sm text-gray-700">{shortcut.action}</span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, i) => (
                        <React.Fragment key={i}>
                          {i > 0 && <span className="text-gray-400 text-xs mx-1">+</span>}
                          <kbd className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono shadow-sm">
                            {key}
                          </kbd>
                        </React.Fragment>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Tips Section */}
            <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
              <h3 className="text-lg font-bold text-gray-900 mb-2">💡 Pro Tips</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>Start typing to see smart suggestions tailored to your department</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>Hover over messages to reveal copy and feedback options</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>Use the search feature to quickly find past conversations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>Export chats for record-keeping or sharing with colleagues</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>Provide feedback on responses to help us improve the service</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Questions? Contact support at support@citygovern.ai
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-white font-medium transition-all hover:shadow-md"
              style={{ backgroundColor: agentColor }}
            >
              Got it!
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default ChatHelp
