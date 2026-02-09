import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, X, Minimize2, Maximize2, Trash2, ChevronLeft, Wifi, WifiOff, Download, Search as SearchIcon, HelpCircle, Moon, Sun, GripVertical } from 'lucide-react'
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
  const resizeRef = useRef(null)
  const [backendOnline, setBackendOnline] = useState(true)
  const [showValidationError, setShowValidationError] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const [chatWidth, setChatWidth] = useState(380)
  const [isResizing, setIsResizing] = useState(false)

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

  // Handle horizontal resize
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return
      
      const newWidth = e.clientX
      // Constrain between 300px and 600px
      if (newWidth >= 300 && newWidth <= 600) {
        setChatWidth(newWidth)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.body.style.cursor = 'default'
      document.body.style.userSelect = 'auto'
    }

    if (isResizing) {
      document.body.style.cursor = 'ew-resize'
      document.body.style.userSelect = 'none'
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing])

  const handleResizeStart = (e) => {
    e.preventDefault()
    setIsResizing(true)
  }

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
      <div className="relative h-full">
        {/* Minimized State - Show a vertical tab */}
        {isMinimized && (
          <motion.div
            initial={{ x: -60 }}
            animate={{ x: 0 }}
            className={`absolute left-0 top-0 bottom-0 w-12 flex flex-col items-center justify-center cursor-pointer shadow-lg z-50 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r`}
            onClick={onToggleMinimize}
            style={{ borderLeftColor: agentColor, borderLeftWidth: '4px' }}
          >
            <div className="transform -rotate-90 whitespace-nowrap text-sm font-semibold text-gray-700 mb-4">
              {agentName}
            </div>
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs mb-2"
              style={{ backgroundColor: agentColor }}
            >
              {agentName.charAt(0)}
            </div>
            <Maximize2 size={16} className="text-gray-500 mt-2" />
          </motion.div>
        )}

        {/* Full Chat Interface */}
        <motion.div
          initial={{ x: 0 }}
          animate={{ 
            x: 0,
            width: isMinimized ? 0 : chatWidth,
            opacity: isMinimized ? 0 : 1
          }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className={`flex flex-col h-full border-r shadow-xl ${isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} ${isMinimized ? 'pointer-events-none' : ''}`}
          style={{ 
            minWidth: isMinimized ? 0 : '300px',
            overflow: 'hidden'
          }}
          role="region"
          aria-label={ariaLabels.chatbot.container}
          aria-hidden={isMinimized}
        >
          {/* Resize Handle */}
          {!isMinimized && (
            <div
              ref={resizeRef}
              onMouseDown={handleResizeStart}
              className={`absolute right-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-blue-400 transition-colors z-50 group ${isResizing ? 'bg-blue-500' : 'bg-transparent'}`}
              title="Drag to resize"
            >
              <div className="absolute right-0 top-1/2 -translate-y-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                <GripVertical size={16} className="text-blue-500" />
              </div>
            </div>
          )}

        {/* Header */}
        <div 
          className={`flex items-center justify-between px-4 py-3 border-b flex-shrink-0 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}
          style={{ backgroundColor: isDarkMode ? undefined : `${agentColor}08` }}
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
              style={{ backgroundColor: agentColor }}
            >
              {agentName.charAt(0)}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className={`font-bold text-sm truncate ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{agentName}</h3>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${backendOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className={`text-xs flex items-center gap-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
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

          <div className="flex items-center gap-1 flex-shrink-0">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`}
              title={isDarkMode ? 'Light mode' : 'Dark mode'}
              aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            
            {/* Help Button */}
            <button
              onClick={() => setShowHelp(true)}
              className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`}
              title={ariaLabels.chatbot.helpButton}
              aria-label={ariaLabels.chatbot.helpButton}
            >
              <HelpCircle size={16} />
            </button>
            
            {messages.length > 0 && (
              <>
                <button
                  onClick={toggleSearch}
                  className={`p-2 rounded-lg transition-colors ${showSearch ? 'bg-blue-100 text-blue-600' : isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`}
                  title="Search messages (Ctrl+F)"
                  aria-label="Search messages"
                >
                  <SearchIcon size={16} />
                </button>
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setShowExportMenu(!showExportMenu)
                    }}
                    className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`}
                    title="Export chat"
                    aria-label="Export chat"
                  >
                    <Download size={16} />
                  </button>
                  {showExportMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`absolute right-0 top-full mt-1 rounded-lg shadow-lg overflow-hidden z-20 min-w-[120px] ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border`}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {['text', 'json', 'markdown', 'csv', 'html'].map(format => (
                        <button
                          key={format}
                          onClick={() => handleExport(format)}
                          className={`w-full px-3 py-2 text-left text-sm transition-colors border-b last:border-b-0 ${isDarkMode ? 'hover:bg-gray-700 border-gray-700 text-gray-300' : 'hover:bg-gray-50 border-gray-100 text-gray-700'}`}
                        >
                          .{format}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </div>
              </>
            )}
            
            {/* Minimize Button */}
            {onToggleMinimize && (
              <button
                onClick={onToggleMinimize}
                className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'}`}
                title={isMinimized ? "Expand" : "Minimize"}
                aria-label={isMinimized ? "Expand chat" : "Minimize chat"}
              >
                <Minimize2 size={16} />
              </button>
            )}
            
            {/* Close Button */}
            {onClose && (
              <button
                onClick={onClose}
                className={`p-2 rounded-lg transition-colors ${isDarkMode ? 'hover:bg-red-900/30 text-red-400' : 'hover:bg-red-50 text-red-600'}`}
                title="Close chat"
                aria-label="Close chat"
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
      <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${isDarkMode ? 'bg-gray-900' : 'bg-white'}`}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div 
              className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
              style={{ backgroundColor: `${agentColor}20` }}
            >
              <span className="text-2xl">💬</span>
            </div>
            <h4 className={`font-bold mb-2 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Start a Conversation</h4>
            <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
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
      <div className={`border-t p-3 flex-shrink-0 relative ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200'}`}>
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
            className={`mb-2 p-2 rounded-lg text-xs flex items-center gap-2 ${isDarkMode ? 'bg-red-900/30 border-red-800 text-red-400' : 'bg-red-50 border-red-200 text-red-700'} border`}
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
            className={`mb-2 p-2 rounded-lg text-xs ${isDarkMode ? 'bg-yellow-900/30 border-yellow-800 text-yellow-400' : 'bg-yellow-50 border-yellow-200 text-yellow-700'} border`}
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
              className={`w-full px-3 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-offset-1 text-sm ${isDarkMode ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-500'}`}
              style={{ '--tw-ring-color': agentColor }}
              disabled={isProcessing}
              aria-label="Message input"
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
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
            {messages.length > 0 && (
              <button
                onClick={handleClearChat}
                className={`p-2 rounded-lg transition-all ${isDarkMode ? 'bg-gray-700 hover:bg-gray-600 text-gray-300' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'}`}
                title="Clear chat"
                aria-label="Clear chat"
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        </div>

        <p className={`text-xs mt-2 text-center ${isDarkMode ? 'text-gray-500' : 'text-gray-500'}`}>
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
    </div>
    </ErrorBoundary>
  )
}

export default AgentChatBot
