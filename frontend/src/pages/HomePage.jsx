import React, { Suspense, lazy, useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import PageLoader from '../components/PageLoader'
import { User, LogOut } from 'lucide-react'

// Lazy load all components
const NeuralBackground = lazy(() => import('../components/NeuralBackground'))
const Hero = lazy(() => import('../components/Hero'))
const DepartmentalEcosystem = lazy(() => import('../components/DepartmentalEcosystem'))
const CoordinationBrain = lazy(() => import('../components/CoordinationBrain'))
const TransparencyVault = lazy(() => import('../components/TransparencyVault'))
const WorkflowPipeline = lazy(() => import('../components/WorkflowPipeline'))
const ProductionStats = lazy(() => import('../components/ProductionStats'))
const Footer = lazy(() => import('../components/Footer'))
const AccessibilityControls = lazy(() => import('../components/AccessibilityControls'))

const HomePage = ({ reducedMotion, highContrast, setReducedMotion, setHighContrast }) => {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is logged in
    const userStr = localStorage.getItem('city_governance_user')
    if (userStr) {
      try {
        setUser(JSON.parse(userStr))
      } catch (err) {
        console.error('Error parsing user data:', err)
      }
    }
  }, [])

  // Extract username from email (before @)
  const getDisplayName = () => {
    if (!user) return ''
    
    // If user has a name property and it's not an email, use it
    if (user.name && !user.name.includes('@')) {
      return user.name
    }
    
    // Otherwise, extract from email (part before @)
    const email = user.email || user.name || ''
    const username = email.split('@')[0]
    
    // Capitalize first letter
    return username.charAt(0).toUpperCase() + username.slice(1)
  }

  const handleLogout = () => {
    localStorage.removeItem('city_governance_token')
    localStorage.removeItem('city_governance_refresh_token')
    localStorage.removeItem('city_governance_user')
    setUser(null)
    navigate('/')
    window.location.reload()
  }

  return (
    <div className={`min-h-screen ${highContrast ? 'contrast-150' : ''}`}>
      {/* User Display - Positioned below accessibility controls */}
      {user && (
        <div className="fixed top-20 right-4 z-50">
          <div className="px-6 py-3 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg border border-gov-blue/20 flex items-center gap-3">
            <User size={20} className="text-gov-blue" />
            <span className="font-semibold text-gov-navy">{getDisplayName()}</span>
            <button
              onClick={handleLogout}
              className="ml-2 p-2 hover:bg-red-50 rounded-lg transition-colors text-red-600 flex items-center gap-1"
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      )}

      {/* Background */}
      <Suspense fallback={null}>
        <NeuralBackground reducedMotion={reducedMotion} />
      </Suspense>
      
      {/* Accessibility Controls */}
      <Suspense fallback={null}>
        <AccessibilityControls 
          reducedMotion={reducedMotion}
          setReducedMotion={setReducedMotion}
          highContrast={highContrast}
          setHighContrast={setHighContrast}
        />
      </Suspense>

      {/* Main Content */}
      <main className="relative z-10">
        <Suspense fallback={<PageLoader />}>
          <Hero reducedMotion={reducedMotion} />
          <DepartmentalEcosystem reducedMotion={reducedMotion} />
          <CoordinationBrain reducedMotion={reducedMotion} />
          <TransparencyVault reducedMotion={reducedMotion} />
          <WorkflowPipeline reducedMotion={reducedMotion} />
          <ProductionStats reducedMotion={reducedMotion} />
          <Footer />
        </Suspense>
      </main>
    </div>
  )
}

export default HomePage
