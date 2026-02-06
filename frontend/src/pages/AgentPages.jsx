import React, { Suspense, lazy } from 'react'
import PageLoader from '../components/PageLoader'

// Lazy load all agent pages
const WaterAgentPage = lazy(() => import('../components/agents/WaterAgentPage'))

// Individual agent page wrappers
export const WaterPage = () => (
  <Suspense fallback={<PageLoader />}>
    <WaterAgentPage />
  </Suspense>
)

export const FirePage = () => {
  const FireAgentPage = lazy(() => 
    import('../components/agents/AgentPages').then(module => ({ default: module.FireAgentPage }))
  )
  return (
    <Suspense fallback={<PageLoader />}>
      <FireAgentPage />
    </Suspense>
  )
}

export const EngineeringPage = () => {
  const EngineeringAgentPage = lazy(() => 
    import('../components/agents/AgentPages').then(module => ({ default: module.EngineeringAgentPage }))
  )
  return (
    <Suspense fallback={<PageLoader />}>
      <EngineeringAgentPage />
    </Suspense>
  )
}

export const HealthPage = () => {
  const HealthAgentPage = lazy(() => 
    import('../components/agents/AgentPages').then(module => ({ default: module.HealthAgentPage }))
  )
  return (
    <Suspense fallback={<PageLoader />}>
      <HealthAgentPage />
    </Suspense>
  )
}

export const FinancePage = () => {
  const FinanceAgentPage = lazy(() => 
    import('../components/agents/AgentPages').then(module => ({ default: module.FinanceAgentPage }))
  )
  return (
    <Suspense fallback={<PageLoader />}>
      <FinanceAgentPage />
    </Suspense>
  )
}

export const SanitationPage = () => {
  const SanitationAgentPage = lazy(() => 
    import('../components/agents/AgentPages').then(module => ({ default: module.SanitationAgentPage }))
  )
  return (
    <Suspense fallback={<PageLoader />}>
      <SanitationAgentPage />
    </Suspense>
  )
}
