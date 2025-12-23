import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AnalysisPage from './pages/AnalysisPage'
import ChatPage from './pages/ChatPage'

// Components
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      {/* Public routes */}
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
      />
      <Route 
        path="/register" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />} 
      />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analysis/:id" element={<AnalysisPage />} />
          <Route path="/chat/:sessionId?" element={<ChatPage />} />
        </Route>
      </Route>

      {/* Default redirect */}
      <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

