import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import GovernmentAnimation from './GovernmentAnimation'
import '../styles/auth.css'

const GOOGLE_CLIENT_ID = '69812575473-3aq9ms8fprokd29nku17h63gc5qatvue.apps.googleusercontent.com'

const Login = () => {
  const navigate = useNavigate()
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
        navigate('/dashboard')
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
        navigate('/dashboard')
      }, 1500)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
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

          {/* Register Link */}
          <p className="auth-footer-text">
            Don't have an account?{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/register'); }}>
              Sign up
            </a>
          </p>

          {/* Back to Home */}
          <p className="auth-back-link">
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/'); }}>← Back to Home</a>
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
