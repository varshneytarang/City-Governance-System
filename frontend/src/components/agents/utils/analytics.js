/**
 * Conversation Analytics
 * Track and analyze chat interactions
 */

/**
 * Analytics event tracker
 */
class ConversationAnalytics {
  constructor(agentType) {
    this.agentType = agentType
    this.sessionId = this.generateSessionId()
    this.events = []
    this.startTime = Date.now()
  }

  generateSessionId() {
    return `${this.agentType}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Track an event
   */
  track(eventName, data = {}) {
    const event = {
      sessionId: this.sessionId,
      agentType: this.agentType,
      eventName,
      timestamp: new Date().toISOString(),
      data,
      url: window.location.href,
      userAgent: navigator.userAgent
    }

    this.events.push(event)
    
    // Store in localStorage for persistence
    this.saveToStorage()
    
    // Send to analytics service (if configured)
    if (window.analytics && typeof window.analytics.track === 'function') {
      window.analytics.track(eventName, event)
    }
    
    return event
  }

  /**
   * Track message sent
   */
  trackMessageSent(message, metadata = {}) {
    return this.track('message_sent', {
      messageLength: message.length,
      wordCount: message.split(/\s+/).length,
      ...metadata
    })
  }

  /**
   * Track message received
   */
  trackMessageReceived(response, duration) {
    return this.track('message_received', {
      responseLength: response.length,
      duration,
      status: 'success'
    })
  }

  /**
   * Track error
   */
  trackError(error, context = {}) {
    return this.track('error_occurred', {
      error: error.message || error.toString(),
      errorType: error.name,
      ...context
    })
  }

  /**
   * Track feature usage
   */
  trackFeatureUsage(feature, action, metadata = {}) {
    return this.track('feature_used', {
      feature,
      action,
      ...metadata
    })
  }

  /**
   * Track search query
   */
  trackSearch(query, resultsCount) {
    return this.track('search_performed', {
      query,
      resultsCount,
      queryLength: query.length
    })
  }

  /**
   * Track export
   */
  trackExport(format, messageCount) {
    return this.track('chat_exported', {
      format,
      messageCount
    })
  }

  /**
   * Track reaction
   */
  trackReaction(messageId, reactionType) {
    return this.track('message_reaction', {
      messageId,
      reactionType
    })
  }

  /**
   * Track suggestion usage
   */
  trackSuggestionUsed(suggestion, source = 'smart-suggestions') {
    return this.track('suggestion_used', {
      suggestion,
      source,
      suggestionLength: suggestion.length
    })
  }

  /**
   * Get session metrics
   */
  getSessionMetrics() {
    const duration = Date.now() - this.startTime
    const messagesSent = this.events.filter(e => e.eventName === 'message_sent').length
    const messagesReceived = this.events.filter(e => e.eventName === 'message_received').length
    const errors = this.events.filter(e => e.eventName === 'error_occurred').length
    const searches = this.events.filter(e => e.eventName === 'search_performed').length
    const exports = this.events.filter(e => e.eventName === 'chat_exported').length
    const reactions = this.events.filter(e => e.eventName === 'message_reaction').length

    return {
      sessionId: this.sessionId,
      agentType: this.agentType,
      duration: Math.round(duration / 1000), // in seconds
      totalEvents: this.events.length,
      messagesSent,
      messagesReceived,
      successRate: messagesSent > 0 ? (messagesReceived / messagesSent * 100).toFixed(2) : 0,
      errors,
      searches,
      exports,
      reactions,
      averageMessageLength: this.getAverageMessageLength(),
      mostUsedFeatures: this.getMostUsedFeatures()
    }
  }

  /**
   * Get average message length
   */
  getAverageMessageLength() {
    const messages = this.events.filter(e => e.eventName === 'message_sent')
    if (messages.length === 0) return 0

    const total = messages.reduce((sum, e) => sum + (e.data.messageLength || 0), 0)
    return Math.round(total / messages.length)
  }

  /**
   * Get most used features
   */
  getMostUsedFeatures() {
    const featureEvents = this.events.filter(e => e.eventName === 'feature_used')
    const featureCounts = {}

    featureEvents.forEach(event => {
      const feature = event.data.feature
      featureCounts[feature] = (featureCounts[feature] || 0) + 1
    })

    return Object.entries(featureCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([feature, count]) => ({ feature, count }))
  }

  /**
   * Get engagement score (0-100)
   */
  getEngagementScore() {
    const metrics = this.getSessionMetrics()
    let score = 0

    // Messages sent/received (40 points)
    score += Math.min((metrics.messagesSent + metrics.messagesReceived) * 4, 40)

    // Feature usage (30 points)
    const featureUsage = metrics.searches + metrics.exports + metrics.reactions
    score += Math.min(featureUsage * 10, 30)

    // Session duration (20 points)
    const minutes = metrics.duration / 60
    score += Math.min(minutes * 4, 20)

    // Success rate (10 points)
    score += parseFloat(metrics.successRate) / 10

    return Math.min(Math.round(score), 100)
  }

  /**
   * Save events to localStorage
   */
  saveToStorage() {
    try {
      const key = `analytics_${this.sessionId}`
      localStorage.setItem(key, JSON.stringify({
        sessionId: this.sessionId,
        agentType: this.agentType,
        startTime: this.startTime,
        events: this.events
      }))
    } catch (error) {
      console.error('Failed to save analytics:', error)
    }
  }

  /**
   * Load previous session data
   */
  static loadFromStorage(sessionId) {
    try {
      const key = `analytics_${sessionId}`
      const data = localStorage.getItem(key)
      return data ? JSON.parse(data) : null
    } catch (error) {
      console.error('Failed to load analytics:', error)
      return null
    }
  }

  /**
   * Get all sessions for an agent
   */
  static getAllSessions(agentType) {
    const sessions = []
    const prefix = `analytics_${agentType}`

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(prefix)) {
        try {
          const data = JSON.parse(localStorage.getItem(key))
          sessions.push(data)
        } catch (error) {
          console.error('Failed to parse session:', error)
        }
      }
    }

    return sessions
  }

  /**
   * Clear old sessions (older than 30 days)
   */
  static cleanupOldSessions() {
    const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000)
    const keysToRemove = []

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith('analytics_')) {
        try {
          const data = JSON.parse(localStorage.getItem(key))
          if (data.startTime < thirtyDaysAgo) {
            keysToRemove.push(key)
          }
        } catch (error) {
          keysToRemove.push(key) // Remove corrupted data
        }
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key))
    return keysToRemove.length
  }

  /**
   * Export analytics summary
   */
  exportSummary() {
    return {
      ...this.getSessionMetrics(),
      engagementScore: this.getEngagementScore(),
      events: this.events,
      exportedAt: new Date().toISOString()
    }
  }
}

/**
 * Create analytics instance
 */
export const createAnalytics = (agentType) => {
  return new ConversationAnalytics(agentType)
}

export default ConversationAnalytics
