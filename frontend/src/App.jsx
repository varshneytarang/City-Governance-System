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

function App() {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)

  useEffect(() => {
    // Check for prefers-reduced-motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
  }, [])

  return (
    <div className={`min-h-screen ${highContrast ? 'contrast-150' : ''}`}>
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
