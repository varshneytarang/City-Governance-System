/**
 * Accessibility Utilities
 * ARIA labels, keyboard navigation, screen reader support
 */

/**
 * Generate unique IDs for ARIA relationships
 */
export const generateAriaId = (prefix = 'aria') => {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Announce message to screen readers
 */
export const announceToScreenReader = (message, priority = 'polite') => {
  const announcement = document.createElement('div')
  announcement.setAttribute('role', 'status')
  announcement.setAttribute('aria-live', priority) // 'polite' or 'assertive'
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message
  
  document.body.appendChild(announcement)
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

/**
 * Trap focus within a modal or dialog
 */
export const trapFocus = (element) => {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  
  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]
  
  const handleTabKey = (e) => {
    if (e.key !== 'Tab') return
    
    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault()
        lastElement.focus()
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    }
  }
  
  element.addEventListener('keydown', handleTabKey)
  
  // Focus first element
  firstElement?.focus()
  
  // Return cleanup function
  return () => {
    element.removeEventListener('keydown', handleTabKey)
  }
}

/**
 * Check if element is visible on screen
 */
export const isElementVisible = (element) => {
  if (!element) return false
  
  const rect = element.getBoundingClientRect()
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  )
}

/**
 * Get ARIA labels for chat components
 */
export const getAriaLabels = () => ({
  chatbot: {
    container: 'Chat interface',
    messageList: 'Conversation messages',
    messageInput: 'Type your message',
    sendButton: 'Send message',
    clearButton: 'Clear conversation',
    searchButton: 'Search messages',
    exportButton: 'Export conversation',
    helpButton: 'Help and keyboard shortcuts',
    closeButton: 'Close chat'
  },
  message: {
    user: 'Your message',
    agent: 'Agent response',
    system: 'System message',
    timestamp: 'Sent at',
    status: 'Message status',
    retry: 'Retry sending message',
    copy: 'Copy message',
    reaction: 'React to message'
  },
  search: {
    input: 'Search conversation',
    results: 'Search results',
    next: 'Next result',
    previous: 'Previous result',
    close: 'Close search'
  },
  suggestions: {
    container: 'Message suggestions',
    item: 'Suggestion',
    label: 'Smart suggestions available'
  },
  export: {
    menu: 'Export format options',
    format: 'Export as'
  },
  help: {
    modal: 'Help and features',
    close: 'Close help'
  }
})

/**
 * Generate status announcement for screen readers
 */
export const generateStatusAnnouncement = (status, context = {}) => {
  const announcements = {
    messageSent: 'Message sent',
    messageReceived: 'New message received',
    processing: 'Processing your request',
    error: `Error: ${context.error || 'Something went wrong'}`,
    success: 'Request completed successfully',
    searching: `Found ${context.count || 0} results`,
    exported: `Conversation exported as ${context.format || 'file'}`,
    cleared: 'Conversation cleared',
    copied: 'Message copied to clipboard',
    connected: 'Connected to server',
    disconnected: 'Disconnected from server'
  }
  
  return announcements[status] || status
}

/**
 * Keyboard navigation helper
 */
export class KeyboardNavigator {
  constructor(items, options = {}) {
    this.items = items
    this.currentIndex = options.initialIndex || 0
    this.loop = options.loop !== false // Default true
    this.onSelect = options.onSelect || null
    this.onChange = options.onChange || null
  }
  
  handleKeyDown(event) {
    switch (event.key) {
      case 'ArrowDown':
      case 'Down':
        event.preventDefault()
        this.next()
        break
        
      case 'ArrowUp':
      case 'Up':
        event.preventDefault()
        this.previous()
        break
        
      case 'Home':
        event.preventDefault()
        this.first()
        break
        
      case 'End':
        event.preventDefault()
        this.last()
        break
        
      case 'Enter':
      case ' ':
        event.preventDefault()
        this.select()
        break
        
      default:
        return false
    }
    
    return true
  }
  
  next() {
    if (this.currentIndex < this.items.length - 1) {
      this.currentIndex++
    } else if (this.loop) {
      this.currentIndex = 0
    }
    this.onChange?.(this.currentIndex, this.items[this.currentIndex])
  }
  
  previous() {
    if (this.currentIndex > 0) {
      this.currentIndex--
    } else if (this.loop) {
      this.currentIndex = this.items.length - 1
    }
    this.onChange?.(this.currentIndex, this.items[this.currentIndex])
  }
  
  first() {
    this.currentIndex = 0
    this.onChange?.(this.currentIndex, this.items[this.currentIndex])
  }
  
  last() {
    this.currentIndex = this.items.length - 1
    this.onChange?.(this.currentIndex, this.items[this.currentIndex])
  }
  
  select() {
    this.onSelect?.(this.currentIndex, this.items[this.currentIndex])
  }
  
  getCurrent() {
    return this.items[this.currentIndex]
  }
}

/**
 * Focus management utilities
 */
export const focusManager = {
  // Save current focus
  save() {
    this.previousElement = document.activeElement
  },
  
  // Restore previous focus
  restore() {
    if (this.previousElement && this.previousElement.focus) {
      this.previousElement.focus()
    }
  },
  
  // Move focus to element
  moveTo(element) {
    if (element && element.focus) {
      element.focus()
    }
  }
}

/**
 * Check if user prefers reduced motion
 */
export const prefersReducedMotion = () => {
  if (!window.matchMedia) return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Get appropriate animation duration based on user preferences
 */
export const getAnimationDuration = (defaultDuration = 300) => {
  return prefersReducedMotion() ? 0 : defaultDuration
}

/**
 * Color contrast checker (WCAG AA compliance)
 */
export const hasGoodContrast = (foreground, background) => {
  // Convert hex to RGB
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }
  
  // Calculate relative luminance
  const getLuminance = (rgb) => {
    const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(val => {
      val = val / 255
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4)
    })
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
  }
  
  const fg = hexToRgb(foreground)
  const bg = hexToRgb(background)
  
  if (!fg || !bg) return true // Can't check, assume OK
  
  const l1 = getLuminance(fg)
  const l2 = getLuminance(bg)
  
  const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)
  
  // WCAG AA requires 4.5:1 for normal text
  return ratio >= 4.5
}

export default {
  generateAriaId,
  announceToScreenReader,
  trapFocus,
  isElementVisible,
  getAriaLabels,
  generateStatusAnnouncement,
  KeyboardNavigator,
  focusManager,
  prefersReducedMotion,
  getAnimationDuration,
  hasGoodContrast
}
