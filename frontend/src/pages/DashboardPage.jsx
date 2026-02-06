import React, { Suspense, lazy } from 'react'
import PageLoader from '../components/PageLoader'

const Dashboard = lazy(() => import('../components/Dashboard'))

const DashboardPage = ({ reducedMotion }) => {
  return (
    <Suspense fallback={<PageLoader />}>
      <Dashboard reducedMotion={reducedMotion} />
    </Suspense>
  )
}

export default DashboardPage
