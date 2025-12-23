import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  HiOutlineScale, 
  HiOutlineUser, 
  HiOutlineMail, 
  HiOutlineLockClosed, 
  HiOutlineEye, 
  HiOutlineEyeOff,
  HiOutlineBriefcase 
} from 'react-icons/hi'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'

function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    role: 'user'
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validation
    if (!formData.username.trim() || !formData.email.trim() || !formData.password.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    setIsLoading(true)
    
    try {
      const response = await authAPI.register({
        username: formData.username,
        email: formData.email,
        full_name: formData.full_name,
        password: formData.password,
        role: formData.role
      })
      
      if (response.success) {
        toast.success('Account created successfully! Please sign in.')
        navigate('/login')
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed. Please try again.'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const roles = [
    { value: 'user', label: 'General User' },
    { value: 'lawyer', label: 'Lawyer' },
    { value: 'student', label: 'Law Student' },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      {/* Background decorations */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-primary-500/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-lg relative z-10"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-gold">
            <HiOutlineScale className="w-7 h-7 text-navy-950" />
          </div>
          <h1 className="font-display text-3xl font-bold gradient-text">LexiQ</h1>
        </div>

        <div className="card p-8">
          <div className="text-center mb-8">
            <h2 className="font-display text-2xl font-semibold text-white mb-2">Create Account</h2>
            <p className="text-gray-400">Join LexiQ to access AI-powered legal research</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username field */}
            <div>
              <label className="input-label">Username *</label>
              <div className="relative">
                <HiOutlineUser className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="input pl-12"
                  placeholder="Choose a username"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Full name field */}
            <div>
              <label className="input-label">Full Name</label>
              <div className="relative">
                <HiOutlineUser className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="input pl-12"
                  placeholder="Your full name"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Email field */}
            <div>
              <label className="input-label">Email *</label>
              <div className="relative">
                <HiOutlineMail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input pl-12"
                  placeholder="your@email.com"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Role selection */}
            <div>
              <label className="input-label">I am a</label>
              <div className="relative">
                <HiOutlineBriefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  className="input pl-12 appearance-none cursor-pointer"
                  disabled={isLoading}
                >
                  {roles.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                  <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Password field */}
            <div>
              <label className="input-label">Password *</label>
              <div className="relative">
                <HiOutlineLockClosed className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input pl-12 pr-12"
                  placeholder="Min. 8 characters"
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

            {/* Confirm password field */}
            <div>
              <label className="input-label">Confirm Password *</label>
              <div className="relative">
                <HiOutlineLockClosed className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="input pl-12"
                  placeholder="Confirm your password"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full mt-6"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Creating account...</span>
                </>
              ) : (
                <span>Create Account</span>
              )}
            </button>
          </form>

          {/* Login link */}
          <p className="mt-8 text-center text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
              Sign In
            </Link>
          </p>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-gray-500 text-sm">
          By creating an account, you agree to our Terms of Service and Privacy Policy.
        </p>
      </motion.div>
    </div>
  )
}

export default RegisterPage

