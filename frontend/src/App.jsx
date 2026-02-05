import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import NeuralBackground from './components/NeuralBackground'
import CustomCursor from './components/CustomCursor'
import Hero from './components/Hero'
import DepartmentalEcosystem from './components/DepartmentalEcosystem'
import CoordinationBrain from './components/CoordinationBrain'
import TransparencyVault from './components/TransparencyVault'
import WorkflowPipeline from './components/WorkflowPipeline'
import ProductionStats from './components/ProductionStats'
import Footer from './components/Footer'
import AccessibilityControls from './components/AccessibilityControls'
import ApiTestPage from './components/ApiTestPage'
import Dashboard from './components/Dashboard'
import WaterAgentPage from './components/agents/WaterAgentPage'
import { FireAgentPage, EngineeringAgentPage, HealthAgentPage, FinanceAgentPage, SanitationAgentPage } from './components/agents/AgentPages'

function App() {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [currentPage, setCurrentPage] = useState('home') // 'home', 'test', 'dashboard', or 'agent'
  const [currentAgent, setCurrentAgent] = useState('') // 'water', 'fire', 'engineering', 'health', 'finance', 'sanitation'

  useEffect(() => {
    // Check for prefers-reduced-motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
    
    // Check URL hash for pages
    const hash = window.location.hash
    if (hash === '#test') {
      setCurrentPage('test')
    } else if (hash === '#dashboard') {
      setCurrentPage('dashboard')
    } else if (hash.startsWith('#agent/')) {
      setCurrentPage('agent')
      setCurrentAgent(hash.replace('#agent/', ''))
    }
    
    // Listen for hash changes
    const handleHashChange = () => {
      const hash = window.location.hash
      if (hash === '#test') {
        setCurrentPage('test')
      } else if (hash === '#dashboard') {
        setCurrentPage('dashboard')
      } else if (hash.startsWith('#agent/')) {
        setCurrentPage('agent')
        setCurrentAgent(hash.replace('#agent/', ''))
      } else {
        setCurrentPage('home')
        setCurrentAgent('')
      }
    }
    
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  // Render test page if selected
  if (currentPage === 'test') {
    return <ApiTestPage />
  }

  // Render dashboard if selected
  if (currentPage === 'dashboard') {
    return <Dashboard reducedMotion={reducedMotion} />
  }

  // Render agent page if selected
  if (currentPage === 'agent') {
    switch (currentAgent) {
      case 'water':
        return <WaterAgentPage />
      case 'fire':
        return <FireAgentPage />
      case 'engineering':
        return <EngineeringAgentPage />
      case 'health':
        return <HealthAgentPage />
      case 'finance':
        return <FinanceAgentPage />
      case 'sanitation':
        return <SanitationAgentPage />
      default:
        window.location.hash = ''
        return null
    }
  }

  return (
    <div className={`min-h-screen ${highContrast ? 'contrast-150' : ''}`}>
      {/* Navigation Toggle */}
      <div className="fixed top-4 right-4 z-50 flex gap-3">
        <a
          href="#dashboard"
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold rounded-lg shadow-lg transition-all transform hover:scale-105"
        >
          📊 Dashboard
        </a>
        <a
          href="#test"
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-lg shadow-lg transition-all transform hover:scale-105"
        >
          🧪 API Test
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
        <DepartmentalEcosystem reducedMotion={reducedMotion} />
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
