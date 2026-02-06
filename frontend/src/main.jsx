import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import './styles/auth.css'
import { DarkModeProvider } from './contexts/DarkModeContext'
import { NotificationProvider } from './contexts/NotificationContext'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <NotificationProvider>
      <DarkModeProvider>
        <App />
      </DarkModeProvider>
    </NotificationProvider>
  </React.StrictMode>,
)
