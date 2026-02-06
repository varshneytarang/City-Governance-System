import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Bot, CheckCircle, XCircle, Clock, AlertTriangle, ThumbsUp, ThumbsDown, Copy, Check, RefreshCw } from 'lucide-react'
import { getAriaLabels } from './utils/accessibility'

/**
 * Individual chat message component
 * Displays user, agent, or system messages with appropriate styling
 * Now with retry, accessibility, and enhanced interactions
 */
const ChatMessage = ({ message, agentColor = '#3b82f6', onRetry }) => {
  const isUser = message.type === 'user'
  const isAgent = message.type === 'agent'
  const isSystem = message.type === 'system'
  
  const [reaction, setReaction] = useState(message.reaction || null)
  const [isCopied, setIsCopied] = useState(false)
  const [showActions, setShowActions] = useState(false)
  
  const ariaLabels = getAriaLabels()

  const getIcon = () => {
    if (isUser) return <User size={16} />
    if (isAgent) return <Bot size={16} />
    return <AlertTriangle size={16} />
  }

  const getStatusIcon = () => {
    if (!message.status) return null
    
    switch (message.status) {
      case 'success':
        return <CheckCircle size={14} className="text-green-500" />
      case 'error':
        return <XCircle size={14} className="text-red-500" />
      case 'processing':
        return <Clock size={14} className="text-yellow-500 animate-pulse" />
      default:
        return null
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  const handleReaction = (reactionType) => {
    setReaction(reaction === reactionType ? null : reactionType)
    // Could send feedback to backend here
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
      role="article"
      aria-label={isUser ? ariaLabels.message.user : isAgent ? ariaLabels.message.agent : ariaLabels.message.system}
    >
      {/* Avatar */}
      <div 
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-blue-100 text-blue-600' 
            : isAgent
            ? 'text-white'
            : 'bg-gray-100 text-gray-600'
        }`}
        style={isAgent ? { backgroundColor: agentColor } : {}}
        aria-hidden="true"
      >
        {getIcon()}
      </div>

      {/* Message Bubble */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`rounded-2xl px-4 py-3 relative group ${
            isUser
              ? 'bg-blue-600 text-white rounded-tr-sm'
              : isAgent
              ? 'bg-gray-100 text-gray-900 rounded-tl-sm'
              : message.status === 'error'
              ? 'bg-red-50 text-red-900 border border-red-200'
              : message.status === 'warning'
              ? 'bg-yellow-50 text-yellow-900 border border-yellow-200'
              : 'bg-gray-50 text-gray-900 border border-gray-200'
          }`}
          onMouseEnter={() => setShowActions(true)}
          onMouseLeave={() => setShowActions(false)}
        >
          {/* Message Content */}
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>

          {/* Retry Button for Failed Messages */}
          {message.canRetry && message.status === 'error' && onRetry && (
            <motion.button
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => onRetry(message)}
              className="mt-3 px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs rounded-lg flex items-center gap-2 transition-colors"
              aria-label="Retry sending message"
            >
              <RefreshCw size={14} />
              Retry
            </motion.button>
          )}

          {/* Action Buttons */}
          <AnimatePresence>
            {showActions && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className={`absolute ${isUser ? 'left-0 -translate-x-full' : 'right-0 translate-x-full'} top-0 flex items-center gap-1 px-2`}
              >
                {/* Copy Button */}
                <button
                  onClick={handleCopy}
                  className="p-1.5 rounded-lg bg-white border border-gray-200 hover:bg-gray-50 transition-colors shadow-sm"
                  title={ariaLabels.message.copy}
                  aria-label={ariaLabels.message.copy}
                >
                  {isCopied ? (
                    <Check size={14} className="text-green-500" />
                  ) : (
                    <Copy size={14} className="text-gray-600" />
                  )}
                </button>
                
                {/* Reaction Buttons (only for agent messages) */}
                {isAgent && (
                  <>
                    <button
                      onClick={() => handleReaction('positive')}
                      className={`p-1.5 rounded-lg border transition-colors shadow-sm ${
                        reaction === 'positive'
                          ? 'bg-green-50 border-green-300 text-green-600'
                          : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-600'
                      }`}
                      title="Helpful response"
                      aria-label="Mark as helpful"
                      aria-pressed={reaction === 'positive'}
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      onClick={() => handleReaction('negative')}
                      className={`p-1.5 rounded-lg border transition-colors shadow-sm ${
                        reaction === 'negative'
                          ? 'bg-red-50 border-red-300 text-red-600'
                          : 'bg-white border-gray-200 hover:bg-gray-50 text-gray-600'
                      }`}
                      title="Not helpful"
                      aria-label="Mark as not helpful"
                      aria-pressed={reaction === 'negative'}
                    >
                      <ThumbsDown size={14} />
                    </button>
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Request Type Badge (for user messages) */}
          {isUser && message.requestType && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                {message.requestType}
              </span>
              {message.location && (
                <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                  📍 {message.location}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Timestamp and Status */}
        <div className="flex items-center gap-2 mt-1 px-2">
          <span className="text-xs text-gray-400">
            {formatTime(message.timestamp)}
          </span>
          {getStatusIcon()}
        </div>
      </div>
    </motion.div>
  )
}

export default ChatMessage
