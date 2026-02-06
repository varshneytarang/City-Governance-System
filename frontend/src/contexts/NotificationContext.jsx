import React, { createContext, useContext, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

/**
 * Notification Context
 * Global notification system for toasts and alerts
 */
const NotificationContext = createContext()

export const useNotification = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider')
  }
  return context
}

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([])

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random()
    const newNotification = {
      id,
      type: 'info',
      duration: 5000,
      dismissible: true,
      ...notification
    }

    setNotifications(prev => [...prev, newNotification])

    // Auto-dismiss after duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }, [])

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  // Shorthand methods
  const success = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'success', message })
  }, [addNotification])

  const error = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'error', message, duration: 7000 })
  }, [addNotification])

  const warning = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'warning', message })
  }, [addNotification])

  const info = useCallback((message, options = {}) => {
    return addNotification({ ...options, type: 'info', message })
  }, [addNotification])

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer
        notifications={notifications}
        onDismiss={removeNotification}
      />
    </NotificationContext.Provider>
  )
}

/**
 * Notification Container Component
 */
const NotificationContainer = ({ notifications, onDismiss }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
      <AnimatePresence>
        {notifications.map(notification => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onDismiss={() => onDismiss(notification.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}

/**
 * Individual Notification Toast
 */
const NotificationToast = ({ notification, onDismiss }) => {
  const { type, message, title, dismissible } = notification

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} className="text-green-600" />
      case 'error':
        return <XCircle size={20} className="text-red-600" />
      case 'warning':
        return <AlertTriangle size={20} className="text-yellow-600" />
      case 'info':
      default:
        return <Info size={20} className="text-blue-600" />
    }
  }

  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, x: 50 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      exit={{ opacity: 0, x: 50, transition: { duration: 0.2 } }}
      className={`${getStyles()} border rounded-lg shadow-lg p-4 flex items-start gap-3 pointer-events-auto min-w-[300px]`}
      role="alert"
      aria-live="polite"
    >
      {/* Icon */}
      <div className="flex-shrink-0 mt-0.5">
        {getIcon()}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="font-semibold text-gray-900 mb-1 text-sm">{title}</h4>
        )}
        <p className="text-sm text-gray-700 leading-relaxed">{message}</p>
      </div>

      {/* Dismiss Button */}
      {dismissible && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 p-1 rounded hover:bg-black/5 transition-colors"
          aria-label="Dismiss notification"
        >
          <X size={16} className="text-gray-500" />
        </button>
      )}
    </motion.div>
  )
}

export default NotificationContext
