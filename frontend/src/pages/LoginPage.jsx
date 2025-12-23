import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineScale, HiOutlineMail, HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!username.trim() || !password.trim()) {
      toast.error('Please enter both username and password')
      return
    }

    setIsLoading(true)
    
    try {
      const response = await authAPI.login(username, password)
      
      if (response.success) {
        login(response.user, response.token)
        toast.success(response.message)
        navigate('/dashboard')
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed. Please try again.'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-navy-900 via-navy-950 to-black" />
        
        {/* Pattern overlay */}
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4af37' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center p-12 xl:p-20">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Logo */}
            <div className="flex items-center gap-4 mb-12">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-gold-lg">
                <HiOutlineScale className="w-10 h-10 text-navy-950" />
              </div>
              <div>
                <h1 className="font-display text-4xl font-bold gradient-text">LexiQ</h1>
                <p className="text-gray-400 text-sm">AI-Powered Legal Research</p>
              </div>
            </div>

            {/* Tagline */}
            <h2 className="font-display text-4xl xl:text-5xl font-semibold text-white mb-6 leading-tight">
              Legal Research,<br />
              <span className="gradient-text">Revolutionized</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-md leading-relaxed">
              Harness the power of AI to analyze cases, find precedents, 
              and build stronger legal arguments in minutes.
            </p>

            {/* Features */}
            <div className="mt-12 space-y-4">
              {[
                'AI-powered case similarity analysis',
                'Instant statute explanations',
                'Judicial pattern insights',
                'Real-time news relevance'
              ].map((feature, index) => (
                <motion.div
                  key={feature}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-2 h-2 rounded-full bg-primary-500" />
                  <span className="text-gray-300">{feature}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Decorative elements */}
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl" />
        <div className="absolute top-20 right-20 w-64 h-64 bg-primary-500/10 rounded-full blur-2xl" />
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <HiOutlineScale className="w-7 h-7 text-navy-950" />
            </div>
            <h1 className="font-display text-3xl font-bold gradient-text">LexiQ</h1>
          </div>

          <div className="card p-8">
            <div className="text-center mb-8">
              <h2 className="font-display text-2xl font-semibold text-white mb-2">Welcome Back</h2>
              <p className="text-gray-400">Sign in to continue to LexiQ</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username field */}
              <div>
                <label className="input-label">Username</label>
                <div className="relative">
                  <HiOutlineMail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input pl-12"
                    placeholder="Enter your username"
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Password field */}
              <div>
                <label className="input-label">Password</label>
                <div className="relative">
                  <HiOutlineLockClosed className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input pl-12 pr-12"
                    placeholder="Enter your password"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                  >
                    {showPassword ? (
                      <HiOutlineEyeOff className="w-5 h-5" />
                    ) : (
                      <HiOutlineEye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Signing in...</span>
                  </>
                ) : (
                  <span>Sign In</span>
                )}
              </button>
            </form>

            {/* Register link */}
            <p className="mt-8 text-center text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium">
                Create Account
              </Link>
            </p>
          </div>

          {/* Footer */}
          <p className="mt-8 text-center text-gray-500 text-sm">
            © 2024 LexiQ. AI-Powered Legal Research Platform.
          </p>
        </motion.div>
      </div>
    </div>
  )
}

export default LoginPage

