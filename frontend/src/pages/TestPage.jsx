import React, { Suspense, lazy } from 'react'
import PageLoader from '../components/PageLoader'

const ApiTestPage = lazy(() => import('../components/ApiTestPage'))

const TestPage = () => {
  return (
    <Suspense fallback={<PageLoader />}>
      <ApiTestPage />
    </Suspense>
  )
}

export default TestPage
