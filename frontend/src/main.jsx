import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#243b53',
            color: '#fff',
            border: '1px solid rgba(212, 175, 55, 0.3)',
          },
          success: {
            iconTheme: {
              primary: '#d4af37',
              secondary: '#102a43',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#102a43',
            },
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>,
)

