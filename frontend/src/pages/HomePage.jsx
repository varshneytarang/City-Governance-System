import React, { Suspense, lazy } from 'react'
import { Link } from 'react-router-dom'
import PageLoader from '../components/PageLoader'

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
  return (
    <div className={`min-h-screen ${highContrast ? 'contrast-150' : ''}`}>
      {/* Navigation Toggle */}
      <div className="fixed top-4 right-4 z-50 flex gap-3">
        <Link
          to="/dashboard"
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold rounded-lg shadow-lg transition-all transform hover:scale-105"
        >
          📊 Dashboard
        </Link>
        <Link
          to="/test"
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-lg shadow-lg transition-all transform hover:scale-105"
        >
          🧪 API Test
        </Link>
      </div>

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
