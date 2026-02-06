/**
 * Authentication utility functions
 */

export const getAuthToken = () => {
  return localStorage.getItem('city_governance_token')
}

export const getRefreshToken = () => {
  return localStorage.getItem('city_governance_refresh_token')
}

export const getUser = () => {
  const userStr = localStorage.getItem('city_governance_user')
  return userStr ? JSON.parse(userStr) : null
}

export const isAuthenticated = () => {
  return !!getAuthToken()
}

export const logout = () => {
  localStorage.removeItem('city_governance_token')
  localStorage.removeItem('city_governance_refresh_token')
  localStorage.removeItem('city_governance_user')
  window.location.href = '/login'
}

export const setAuthData = (token, refreshToken, user) => {
  localStorage.setItem('city_governance_token', token)
  localStorage.setItem('city_governance_refresh_token', refreshToken)
  localStorage.setItem('city_governance_user', JSON.stringify(user))
}
