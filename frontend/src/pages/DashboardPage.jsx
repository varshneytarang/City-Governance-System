import React, { Suspense, lazy, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import PageLoader from '../components/PageLoader'

const Dashboard = lazy(() => import('../components/Dashboard'))

const DashboardPage = ({ reducedMotion }) => {
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('city_governance_token')
    if (!token) {
      // Redirect to login if not authenticated
      navigate('/login', { replace: true })
    }
  }, [navigate])

  return (
    <Suspense fallback={<PageLoader />}>
      <Dashboard reducedMotion={reducedMotion} />
    </Suspense>
  )
}

export default DashboardPage
