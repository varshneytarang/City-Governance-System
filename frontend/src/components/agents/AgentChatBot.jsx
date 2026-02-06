import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, X, Minimize2, Maximize2, Trash2, ChevronLeft, Wifi, WifiOff, Download, Search as SearchIcon, HelpCircle, Moon, Sun } from 'lucide-react'
import ChatMessage from './ChatMessage'
import QuickActions from './QuickActions'
import MessageSuggestions from './MessageSuggestions'
import ChatSearch from './ChatSearch'
import ChatHelp from './ChatHelp'
import ErrorBoundary from './ErrorBoundary'
import useChatbot from './hooks/useChatbot'
import { useDarkMode } from '../../contexts/DarkModeContext'
import { useNotification } from '../../contexts/NotificationContext'
import { getSmartSuggestions } from './utils/messageParser'
import { exportChat, getChatStatistics } from './utils/chatExport'
import { getAriaLabels } from './utils/accessibility'

/**
 * Agent Chatbot Component
 * Provides interactive chat interface for querying department agents
 */
const AgentChatBot = ({ 
  agentType = 'water',
  agentName = 'Water Management',
  agentColor = '#3b82f6',
  onClose = null,
  isMinimized = false,
  onToggleMinimize = null
}) => {
  const {
    messages,
    inputValue,
    setInputValue,
    isProcessing,
    sendMessage,
    clearChat,
    retryMessage,
    handleQuickAction,
    checkBackendHealth,
    analytics
  } = useChatbot(agentType)

  const { isDarkMode, toggleDarkMode } = useDarkMode()
  const notification = useNotification()
  const ariaLabels = getAriaLabels()

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const [backendOnline, setBackendOnline] = useState(true)
  const [showValidationError, setShowValidationError] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [showHelp, setShowHelp] = useState(false)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    if (!isMinimized) {
      inputRef.current?.focus()
    }
  }, [isMinimized])

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      const isOnline = await checkBackendHealth()
      setBackendOnline(isOnline)
    }
    checkHealth()
    
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [checkBackendHealth])

  // Update suggestions when input changes
  useEffect(() => {
    if (inputValue.trim().length >= 2) {
      const newSuggestions = getSmartSuggestions(inputValue, agentType, messages)
      setSuggestions(newSuggestions)
      setShowSuggestions(newSuggestions.length > 0)
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [inputValue, agentType, messages])

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowExportMenu(false)
    }
    if (showExportMenu) {
      document.addEventListener('click', handleClickOutside)
      return () => document.removeEventListener('click', handleClickOutside)
    }
  }, [showExportMenu])

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl+F or Cmd+F for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'f' && messages.length > 0) {
        e.preventDefault()
        setShowSearch(!showSearch)
      }
      // Ctrl+K or Cmd+K to clear chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        if (messages.length > 0 && window.confirm('Clear chat history?')) {
          clearChat()
        }
      }
      // ? to show help
      if (e.key === '?' && !inputRef.current?.matches(':focus')) {
        e.preventDefault()
        setShowHelp(true)
      }
      // Esc to close modals
      if (e.key === 'Escape') {
        setShowSearch(false)
        setShowHelp(false)
        setShowExportMenu(false)
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [showSearch, messages, clearChat])

  // Get request types for current agent
  const getRequestTypes = () => {
    const types = {
      water: ['capacity_query', 'maintenance_request', 'emergency_response', 'water_quality_check', 'pipeline_repair'],
      fire: ['fire_emergency', 'fire_inspection', 'fire_safety_assessment', 'hazmat_response', 'rescue_operation'],
      engineering: ['project_planning', 'infrastructure_assessment', 'road_repair', 'bridge_inspection', 'construction_approval'],
      health: ['health_inspection', 'disease_outbreak', 'vaccination_campaign', 'restaurant_inspection', 'public_health_assessment'],
      finance: ['budget_approval', 'cost_estimation', 'financial_audit', 'revenue_forecast', 'expenditure_review'],
      sanitation: ['waste_collection', 'street_cleaning', 'sanitation_inspection', 'recycling_request', 'hazardous_waste_disposal']
    }
    return types[agentType] || types.water
  }

  const handleSend = () => {
    if (!inputValue.trim()) {
      setShowValidationError(true)
      setTimeout(() => setShowValidationError(false), 3000)
      return
    }
    setShowValidationError(false)
    setShowSuggestions(false)
    sendMessage(inputValue)
  }

  const handleSuggestionSelect = (suggestion) => {
    setInputValue(suggestion)
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  const handleExport = (format) => {
    try {
      exportChat(messages, agentName, format, agentColor)
      setShowExportMenu(false)
      notification.success(`Chat exported as .${format}`, {
        duration: 3000
      })
      
      // Track analytics
      if (analytics) {
        analytics.trackExport(format, messages.length)
      }
    } catch (error) {
      notification.error(`Failed to export: ${error.message}`)
    }
  }

  const toggleSearch = () => {
    setShowSearch(!showSearch)
  }

  const handleSearchResultClick = (message) => {
    // Scroll to message (could enhance with highlighting)
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleQuickActionClick = (action) => {
    handleQuickAction(action)
    // Auto-focus input after selecting quick action
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      clearChat()
      notification.info('Conversation cleared', { duration: 2000 })
    }
  }

  const handleRetry = (message) => {
    retryMessage(message)
    notification.info('Retrying message...', { duration: 2000 })
  }

  return (
    <ErrorBoundary agentColor={agentColor}>
      <motion.div
        initial={{ x: -320 }}
        animate={{ x: isMinimized ? -320 : 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className={`flex flex-col h-full border-r shadow-xl ${isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'}`}
        style={{ width: '320px' }}
        role="region"
        aria-label={ariaLabels.chatbot.container}
      >
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-4 border-b border-gray-200 flex-shrink-0"
        style={{ backgroundColor: `${agentColor}10` }}
      >
        <div className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
            style={{ backgroundColor: agentColor }}
          >
            {agentName.charAt(0)}
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-sm">{agentName}</h3>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-xs text-gray-600 flex items-center gap-1">
                {backendOnline ? (
                  <>
                    <Wifi size={12} />
                    Online
                  </>
                ) : (
                  <>
                    <WifiOff size={12} />
                    Offline
                  </>
                )}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            title={isDarkMode ? 'Light mode' : 'Dark mode'}
            aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          
          {/* Help Button */}
          <button
            onClick={() => setShowHelp(true)}
            className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            title={ariaLabels.chatbot.helpButton}
            aria-label={ariaLabels.chatbot.helpButton}
          >
            <HelpCircle size={16} />
          </button>
          
          {messages.length > 0 && (
            <>
              <button
                onClick={toggleSearch}
                className={`p-2 rounded-lg transition-colors ${showSearch ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'}`}
                title="Search messages (Ctrl+F)"
              >
                <SearchIcon size={16} />
              </button>
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowExportMenu(!showExportMenu)
                  }}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Export chat"
                >
                  <Download size={16} />
                </button>
                {showExportMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden z-20 min-w-[120px]"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {['text', 'json', 'markdown', 'csv', 'html'].map(format => (
                      <button
                        key={format}
                        onClick={() => handleExport(format)}
                        className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
                      >
                        .{format}
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>
            </>
          )}
          {onToggleMinimize && (
            <button
              onClick={onToggleMinimize}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title={isMinimized ? "Expand" : "Minimize"}
            >
              {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title="Close"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <ChatSearch 
        messages={messages}
        onResultClick={handleSearchResultClick}
        isOpen={showSearch}
        onClose={() => setShowSearch(false)}
      />

      {/* Quick Actions */}
      <QuickActions 
        agentType={agentType} 
        onActionClick={handleQuickActionClick}
        agentColor={agentColor}
      />

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div 
              className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
              style={{ backgroundColor: `${agentColor}20` }}
            >
              <span className="text-2xl">💬</span>
            </div>
            <h4 className="font-bold text-gray-900 mb-2">Start a Conversation</h4>
            <p className="text-sm text-gray-600">
              Ask me anything about {agentName.toLowerCase()}. Use quick actions above or type your question below.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage 
                key={message.id} 
                message={message}
                agentColor={agentColor}
                onRetry={handleRetry}
              />
            ))}
            {isProcessing && (
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <div className="flex gap-1">
                  <motion.div
                    className="w-2 h-2 rounded-full bg-gray-400"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className="w-2 h-2 rounded-full bg-gray-400"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className="w-2 h-2 rounded-full bg-gray-400"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
                <span>Processing...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-3 bg-gray-50 flex-shrink-0 relative">
        {/* Message Suggestions */}
        <MessageSuggestions 
          suggestions={suggestions}
          onSelect={handleSuggestionSelect}
          isVisible={showSuggestions}
        />
        
        {/* Backend Offline Warning */}
        {!backendOnline && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-2 p-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2"
          >
            <WifiOff size={14} />
            <span>Backend offline. Start the backend server at http://localhost:8000</span>
          </motion.div>
        )}

        {/* Validation Error */}
        {showValidationError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-2 p-2 bg-yellow-50 border border-yellow-200 rounded-lg text-xs text-yellow-700"
          >
            Please enter a message
          </motion.div>
        )}

        {/* Message Input */}
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-offset-1 text-sm"
              style={{ '--tw-ring-color': agentColor }}
              disabled={isProcessing}
            />
          </div>
          
          {/* Action Buttons */}
          <div className="flex flex-col gap-1">
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isProcessing || !backendOnline}
              className="p-2 rounded-lg text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-md"
              style={{ backgroundColor: agentColor }}
              title={!backendOnline ? "Backend offline" : "Send message"}
            >
              <Send size={18} />
            </button>
            {messages.length > 0 && (
              <button
                onClick={handleClearChat}
                className="p-2 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-700 transition-all"
                title="Clear chat"
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        </div>

        <p className="text-xs text-gray-500 mt-2 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>

      {/* Help Modal */}
      <ChatHelp 
        isOpen={showHelp}
        onClose={() => setShowHelp(false)}
        agentColor={agentColor}
      />
    </motion.div>
    </ErrorBoundary>
  )
}

export default AgentChatBot
