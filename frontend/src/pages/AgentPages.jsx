import React, { Suspense, lazy } from 'react'
import PageLoader from '../components/PageLoader'

// Lazy load all agent pages
const WaterAgentPage = lazy(() => import('../components/agents/WaterAgentPage'))
const FireAgentPage = lazy(() => import('../components/agents/FireAgentPage'))
const EngineeringAgentPage = lazy(() => import('../components/agents/EngineeringAgentPage'))
const HealthAgentPage = lazy(() => import('../components/agents/HealthAgentPage'))
const FinanceAgentPage = lazy(() => import('../components/agents/FinanceAgentPage'))
const SanitationAgentPage = lazy(() => import('../components/agents/SanitationAgentPage'))

// Individual agent page wrappers
export const WaterPage = () => (
  <Suspense fallback={<PageLoader />}>
    <WaterAgentPage />
  </Suspense>
)

export const FirePage = () => (
  <Suspense fallback={<PageLoader />}>
    <FireAgentPage />
  </Suspense>
)

export const EngineeringPage = () => (
  <Suspense fallback={<PageLoader />}>
    <EngineeringAgentPage />
  </Suspense>
)

export const HealthPage = () => (
  <Suspense fallback={<PageLoader />}>
    <HealthAgentPage />
  </Suspense>
)

export const FinancePage = () => (
  <Suspense fallback={<PageLoader />}>
    <FinanceAgentPage />
  </Suspense>
)

export const SanitationPage = () => (
  <Suspense fallback={<PageLoader />}>
    <SanitationAgentPage />
  </Suspense>
)
