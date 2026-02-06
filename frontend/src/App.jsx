import React, { useState, useEffect, Suspense } from 'react'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import PageLoader from './components/PageLoader'

// Import page components
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import TestPage from './pages/TestPage'
import { WaterPage, FirePage, EngineeringPage, HealthPage, FinancePage, SanitationPage } from './pages/AgentPages'

function App() {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [currentPage, setCurrentPage] = useState('home') // 'home', 'test', 'dashboard', or 'agent'
  const [currentAgent, setCurrentAgent] = useState('') // 'water', 'fire', 'engineering', 'health', 'finance', 'sanitation'

  useEffect(() => {
    // Check for prefers-reduced-motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
  }, [])

  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Home Page */}
          <Route 
            path="/" 
            element={
              <HomePage 
                reducedMotion={reducedMotion}
                highContrast={highContrast}
                setReducedMotion={setReducedMotion}
                setHighContrast={setHighContrast}
              />
            } 
          />

          {/* Dashboard */}
          <Route 
            path="/dashboard" 
            element={<DashboardPage reducedMotion={reducedMotion} />} 
          />

          {/* API Test Page */}
          <Route 
            path="/test" 
            element={<TestPage />} 
          />

          {/* Agent Pages */}
          <Route path="/agent/water" element={<WaterPage />} />
          <Route path="/agent/fire" element={<FirePage />} />
          <Route path="/agent/engineering" element={<EngineeringPage />} />
          <Route path="/agent/health" element={<HealthPage />} />
          <Route path="/agent/finance" element={<FinancePage />} />
          <Route path="/agent/sanitation" element={<SanitationPage />} />

          {/* 404 - Redirect to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

// Navigate component for redirects
const Navigate = ({ to }) => {
  const navigate = useNavigate()
  useEffect(() => {
    navigate(to)
  }, [navigate, to])
  return null
}

export default App
