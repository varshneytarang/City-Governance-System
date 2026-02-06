import React from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { motion } from 'framer-motion'

/**
 * Error Boundary Component
 * Catches React errors and displays fallback UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
    
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }))

    // Log to external error tracking service (e.g., Sentry)
    if (window.errorLogger) {
      window.errorLogger.log({
        error: error.toString(),
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString()
      })
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  handleReload = () => {
    window.location.reload()
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      const { agentColor = '#3b82f6' } = this.props

      // If error keeps happening, show more drastic options
      const isPersistentError = this.state.errorCount > 2

      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4"
        >
          <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
            {/* Header */}
            <div
              className="px-6 py-8 text-white text-center"
              style={{
                background: `linear-gradient(135deg, ${agentColor}, ${agentColor}dd)`
              }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
              >
                <AlertTriangle size={64} className="mx-auto mb-4" />
              </motion.div>
              <h1 className="text-2xl font-bold mb-2">Oops! Something Went Wrong</h1>
              <p className="text-white/90 text-sm">
                {isPersistentError 
                  ? "We're having persistent issues. Please try the options below."
                  : "Don't worry, we can fix this together."}
              </p>
            </div>

            {/* Error Details */}
            <div className="px-6 py-6">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-sm font-mono text-red-800 mb-2">
                  {this.state.error?.toString() || 'Unknown error'}
                </p>
                {!isPersistentError && (
                  <p className="text-xs text-red-600">
                    Error #{this.state.errorCount} - A temporary glitch occurred
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                {!isPersistentError && (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={this.handleReset}
                    className="w-full px-4 py-3 rounded-lg text-white font-medium flex items-center justify-center gap-2 transition-all hover:shadow-lg"
                    style={{ backgroundColor: agentColor }}
                  >
                    <RefreshCw size={18} />
                    Try Again
                  </motion.button>
                )}

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleReload}
                  className="w-full px-4 py-3 bg-gray-600 hover:bg-gray-700 rounded-lg text-white font-medium flex items-center justify-center gap-2 transition-all"
                >
                  <RefreshCw size={18} />
                  Reload Page
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={this.handleGoHome}
                  className="w-full px-4 py-3 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-800 font-medium flex items-center justify-center gap-2 transition-all"
                >
                  <Home size={18} />
                  Go to Home
                </motion.button>
              </div>

              {/* Help Text */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800 mb-2 font-semibold">
                  Need Help?
                </p>
                <ul className="text-xs text-blue-700 space-y-1">
                  <li>• Try clearing your browser cache</li>
                  <li>• Check your internet connection</li>
                  <li>• Contact support: support@citygovern.ai</li>
                </ul>
              </div>

              {/* Technical Details (Collapsible) */}
              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <details className="mt-4">
                  <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                    Technical Details (Dev Mode)
                  </summary>
                  <pre className="mt-2 text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </motion.div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
