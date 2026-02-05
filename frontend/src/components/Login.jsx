import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import GovernmentAnimation from './GovernmentAnimation'
import '../styles/auth.css'

const GOOGLE_CLIENT_ID = '69812575473-3aq9ms8fprokd29nku17h63gc5qatvue.apps.googleusercontent.com'

const Login = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Initialize Google OAuth
  useEffect(() => {
    if (typeof google !== 'undefined') {
      google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCallback
      })
      
      // Render the Google Sign-In button
      google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        { 
          theme: 'outline', 
          size: 'large',
          width: '100%',
          text: 'signin_with'
        }
      )
    }
  }, [])

  // Handle Google OAuth callback
  const handleGoogleCallback = async (response) => {
    setLoading(true)
    setError('')

    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id_token: response.credential
        })
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Google login failed')
      }

      // Store tokens
      localStorage.setItem('city_governance_token', data.token.access_token)
      localStorage.setItem('city_governance_refresh_token', data.token.refresh_token)
      localStorage.setItem('city_governance_user', JSON.stringify(data.user))

      setSuccess('Login successful! Redirecting...')
      
      setTimeout(() => {
        window.location.href = '/'
        window.location.reload()
      }, 1500)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed')
      }

      // Store tokens
      localStorage.setItem('city_governance_token', data.token.access_token)
      localStorage.setItem('city_governance_refresh_token', data.token.refresh_token)
      localStorage.setItem('city_governance_user', JSON.stringify(data.user))

      setSuccess('Login successful! Redirecting...')
      
      setTimeout(() => {
        window.location.href = '/'
        window.location.reload() // Refresh to update auth state
      }, 1500)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = () => {
    if (typeof google !== 'undefined') {
      google.accounts.id.prompt()
    } else {
      setError('Google Sign-In is loading. Please try again in a moment.')
    }
  }

  return (
    <div className="auth-container">
      {/* Left Side - Form */}
      <motion.div 
        className="auth-form-side"
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="auth-form-content">
          {/* Logo and Title */}
          <motion.div 
            className="auth-header"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="auth-logo">
              <svg className="auth-logo-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
            </div>
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Sign in to City Governance AI</p>
          </motion.div>

          {/* Alert Messages */}
          <AnimatePresence>
            {error && (
              <motion.div 
                className="alert alert-error"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <span>{error}</span>
                <button onClick={() => setError('')}>×</button>
              </motion.div>
            )}
            {success && (
              <motion.div 
                className="alert alert-success"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <span>{success}</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Login Form */}
          <motion.form 
            onSubmit={handleSubmit}
            className="auth-form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="••••••••"
                disabled={loading}
              />
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                  disabled={loading}
                />
                <span>Remember me</span>
              </label>
              <a href="#" className="forgot-link">Forgot password?</a>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? (
                <span className="loading-spinner"></span>
              ) : (
                'Sign In'
              )}
            </button>
          </motion.form>

          {/* Divider */}
          <div className="auth-divider">
            <span>or continue with</span>
          </div>

          {/* Google Sign In Button Container */}
          <div id="google-signin-button" style={{ width: '100%' }}></div>
          
          {/* Fallback manual trigger button */}
          <button 
            type="button"
            onClick={handleGoogleLogin}
            className="btn-google"
            disabled={loading}
            style={{ marginTop: '10px' }}
          >
            <svg className="google-icon" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span>Sign in with Google</span>
          </button>

          {/* Register Link */}
          <p className="auth-footer-text">
            Don't have an account?{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('register'); }}>
              Sign up
            </a>
          </p>

          {/* Back to Home */}
          <p className="auth-back-link">
            <a href="/">← Back to Home</a>
          </p>
        </div>
      </motion.div>

      {/* Right Side - Government Animation */}
      <motion.div 
        className="auth-animation-side"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
      >
        <GovernmentAnimation type="login" />
      </motion.div>
    </div>
  )
}

export default Login
