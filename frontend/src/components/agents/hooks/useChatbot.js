import { useState, useEffect, useCallback, useRef } from 'react'
import { createAnalytics } from '../utils/analytics'
import { announceToScreenReader, generateStatusAnnouncement } from '../utils/accessibility'
import { debounce } from '../utils/performance'

/**
 * Custom hook for chatbot functionality
 * Manages chat state, message handling, and API integration
 * Now with retry logic, analytics, and accessibility
 */
const useChatbot = (agentType) => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentJobId, setCurrentJobId] = useState(null)
  const [retryCount, setRetryCount] = useState(0)
  
  const pollingIntervalRef = useRef(null)
  const analyticsRef = useRef(null)
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-1febd.up.railway.app/api/v1'
  const MAX_RETRIES = 3

  // Initialize analytics
  useEffect(() => {
    if (!analyticsRef.current) {
      analyticsRef.current = createAnalytics(agentType)
      analyticsRef.current.track('session_started')
    }
    
    return () => {
      if (analyticsRef.current) {
        analyticsRef.current.track('session_ended', {
          metrics: analyticsRef.current.getSessionMetrics()
        })
      }
    }
  }, [agentType])

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem(`chat_${agentType}`)
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        setMessages(parsed)
        
        if (analyticsRef.current && parsed.length > 0) {
          analyticsRef.current.track('history_loaded', {
            messageCount: parsed.length
          })
        }
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    }
  }, [agentType])

  // Save chat history to localStorage when messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_${agentType}`, JSON.stringify(messages))
    }
  }, [messages, agentType])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearTimeout(pollingIntervalRef.current)
      }
    }
  }, [])

  // Add a new message to the chat
  const addMessage = useCallback((message) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      ...message
    }
    setMessages(prev => [...prev, newMessage])
    
    // Accessibility announcement
    if (message.type === 'user') {
      announceToScreenReader(generateStatusAnnouncement('messageSent'))
    } else if (message.type === 'agent') {
      announceToScreenReader(generateStatusAnnouncement('messageReceived'))
    }
    
    return newMessage.id
  }, [])

  // Update an existing message
  const updateMessage = useCallback((messageId, updates) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, ...updates } : msg
    ))
  }, [])

  // Poll for job result with analytics
  const pollForResult = useCallback(async (jobId, systemMessageId) => {
    const maxAttempts = 30 // 60 seconds total (2 sec intervals)
    let attempts = 0

    const poll = async () => {
      if (attempts >= maxAttempts) {
        updateMessage(systemMessageId, {
          content: '⏱️ Request timed out. Please try again.',
          status: 'error'
        })
        setIsProcessing(false)
        setCurrentJobId(null)
        announceToScreenReader(generateStatusAnnouncement('error', { error: 'Request timed out' }))
        return
      }

      attempts++

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/query/${jobId}`)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()

        if (data.status === 'succeeded') {
          // Job completed successfully
          const result = data.result || {}
          const requestDuration = Date.now() - (systemMessageId.timestamp || Date.now())
          
          // Use the LLM-generated reason as the main response (like ChatGPT)
          let responseContent = result.reason || result.decision || 'Request completed'
          
          // Add agent response message
          addMessage({
            type: 'agent',
            content: responseContent,
            result: result,
            status: 'success',
            jobId: jobId
          })
          
          // Track analytics
          if (analyticsRef.current) {
            analyticsRef.current.trackMessageReceived(responseContent, requestDuration)
          }

          // Remove system processing message
          setMessages(prev => prev.filter(msg => msg.id !== systemMessageId))
          
          setIsProcessing(false)
          setCurrentJobId(null)
          setRetryCount(0) // Reset retry count on success
          
          announceToScreenReader(generateStatusAnnouncement('success'))
          
        } else if (data.status === 'failed') {
          // Job failed
          const errorMsg = data.error || 'Request failed'
          
          updateMessage(systemMessageId, {
            content: `❌ ${errorMsg}`,
            status: 'error'
          })
          
          // Track error
          if (analyticsRef.current) {
            analyticsRef.current.trackError(new Error(errorMsg), { context: 'polling' })
          }
          
          setIsProcessing(false)
          setCurrentJobId(null)
          announceToScreenReader(generateStatusAnnouncement('error', { error: errorMsg }))
          
        } else {
          // Still processing (queued or running)
          updateMessage(systemMessageId, {
            content: `⏳ Processing... (attempt ${attempts}/${maxAttempts})`,
            status: 'processing'
          })
          
          // Poll again after 2 seconds
          pollingIntervalRef.current = setTimeout(poll, 2000)
        }
        
      } catch (error) {
        console.error('Polling error:', error)
        
        updateMessage(systemMessageId, {
          content: `❌ Error: ${error.message}`,
          status: 'error'
        })
        
        setIsProcessing(false)
        setCurrentJobId(null)
      }
    }

    // Start polling
    poll()
  }, [addMessage, updateMessage, API_BASE_URL])

  // Send a message to the backend API with retry logic
  const sendMessage = useCallback(async (message, isRetry = false) => {
    if (!message.trim()) return

    const requestStartTime = Date.now()

    // Add user message (only if not retry)
    if (!isRetry) {
      addMessage({
        type: 'user',
        content: message,
        status: 'sent'
      })
      
      // Track analytics
      if (analyticsRef.current) {
        analyticsRef.current.trackMessageSent(message)
      }
    }

    // Clear input
    setInputValue('')
    setIsProcessing(true)
    
    announceToScreenReader(generateStatusAnnouncement('processing'))

    try {
      // Prepare payload - send a general query type for the agent
      const payload = {
        type: `${agentType}_general_query`,
        location: 'General',
        reason: message,
        from: `${agentType.charAt(0).toUpperCase() + agentType.slice(1)} Agent Chat`
      }

      // Submit query to backend
      const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (!data.job_id) {
        throw new Error('No job_id returned from API')
      }

      setCurrentJobId(data.job_id)

      // Add system message showing processing status
      const systemMessageId = addMessage({
        type: 'system',
        content: `⏳ Processing your request...`,
        status: 'processing',
        jobId: data.job_id
      })

      // Start polling for result
      pollForResult(data.job_id, systemMessageId)

    } catch (error) {
      console.error('Submit query error:', error)
      
      // Track error
      if (analyticsRef.current) {
        analyticsRef.current.trackError(error, { context: 'sendMessage' })
      }
      
      // Retry logic
      if (retryCount < MAX_RETRIES) {
        setRetryCount(prev => prev + 1)
        
        addMessage({
          type: 'system',
          content: `⚠️ Request failed. Retrying... (Attempt ${retryCount + 1}/${MAX_RETRIES})`,
          status: 'warning',
          canRetry: true,
          originalMessage: message
        })
        
        announceToScreenReader(`Retrying request, attempt ${retryCount + 1}`)
        
        // Exponential backoff
        setTimeout(() => {
          sendMessage(message, true)
        }, Math.pow(2, retryCount) * 1000)
      } else {
        addMessage({
          type: 'system',
          content: `❌ Failed to submit request after ${MAX_RETRIES} attempts: ${error.message}\n\nMake sure the backend is running at ${API_BASE_URL}`,,
          status: 'error',
          canRetry: true,
          originalMessage: message
        })
        
        announceToScreenReader(generateStatusAnnouncement('error', { error: error.message }))
        setRetryCount(0)
      }
      
      setIsProcessing(false)
    }
  }, [addMessage, agentType, pollForResult, API_BASE_URL, retryCount])

  // Clear chat history with analytics
  const clearChat = useCallback(() => {
    const messageCount = messages.length
    
    setMessages([])
    localStorage.removeItem(`chat_${agentType}`)
    setCurrentJobId(null)
    setIsProcessing(false)
    setRetryCount(0)
    
    if (pollingIntervalRef.current) {
      clearTimeout(pollingIntervalRef.current)
    }
    
    // Track analytics
    if (analyticsRef.current) {
      analyticsRef.current.track('chat_cleared', { messageCount })
    }
    
    announceToScreenReader('Conversation cleared')
  }, [agentType, messages.length])

  // Retry failed message
  const retryMessage = useCallback((message) => {
    if (message.originalMessage) {
      sendMessage(message.originalMessage, true)
    }
  }, [sendMessage])

  // Quick action handler
  const handleQuickAction = useCallback((action) => {
    setInputValue(action.label)
    
    // Track analytics
    if (analyticsRef.current) {
      analyticsRef.current.trackFeatureUsage('quick-actions', 'selected', {
        action: action.label
      })
    }
  }, [])

  // Check backend health
  const checkBackendHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`)
      const data = await response.json()
      return data.status === 'ok'
    } catch (error) {
      console.error('Backend health check failed:', error)
      return false
    }
  }, [API_BASE_URL])

  return {
    messages,
    inputValue,
    setInputValue,
    isProcessing,
    currentJobId,
    sendMessage,
    addMessage,
    updateMessage,
    clearChat,
    retryMessage,
    handleQuickAction,
    checkBackendHealth,
    analytics: analyticsRef.current
  }
}

export default useChatbot
