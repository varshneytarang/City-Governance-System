import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import NeuralBackground from './components/NeuralBackground'
import CustomCursor from './components/CustomCursor'
import Hero from './components/Hero'
import AgentConstellation from './components/AgentConstellation'
import CoordinationBrain from './components/CoordinationBrain'
import TransparencyVault from './components/TransparencyVault'
import WorkflowPipeline from './components/WorkflowPipeline'
import ProductionStats from './components/ProductionStats'
import Footer from './components/Footer'
import AccessibilityControls from './components/AccessibilityControls'
import ApiTestPage from './components/ApiTestPage'

function App() {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [currentPage, setCurrentPage] = useState('home') // 'home' or 'test'

  useEffect(() => {
    // Check for prefers-reduced-motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
    
    // Check URL hash for test page
    if (window.location.hash === '#test') {
      setCurrentPage('test')
    }
    
    // Listen for hash changes
    const handleHashChange = () => {
      if (window.location.hash === '#test') {
        setCurrentPage('test')
      } else {
        setCurrentPage('home')
      }
    }
    
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  // Render test page if selected
  if (currentPage === 'test') {
    return <ApiTestPage />
  }

  return (
    <div className={`min-h-screen ${highContrast ? 'contrast-150' : ''}`}>
      {/* Navigation Toggle */}
      <div className="fixed top-4 right-4 z-50">
        <a
          href="#test"
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-lg shadow-lg transition-all transform hover:scale-105"
        >
          🧪 API Test Console
        </a>
      </div>

      {/* Background */}
      <NeuralBackground reducedMotion={reducedMotion} />
      
      {/* Custom Cursor */}
      {!reducedMotion && <CustomCursor />}
      
      {/* Accessibility Controls */}
      <AccessibilityControls 
        reducedMotion={reducedMotion}
        setReducedMotion={setReducedMotion}
        highContrast={highContrast}
        setHighContrast={setHighContrast}
      />

      {/* Main Content */}
      <main className="relative z-10">
        <Hero reducedMotion={reducedMotion} />
        <AgentConstellation reducedMotion={reducedMotion} />
        <CoordinationBrain reducedMotion={reducedMotion} />
        <TransparencyVault reducedMotion={reducedMotion} />
        <WorkflowPipeline reducedMotion={reducedMotion} />
        <ProductionStats reducedMotion={reducedMotion} />
        <Footer />
      </main>
    </div>
  )
}

export default App
