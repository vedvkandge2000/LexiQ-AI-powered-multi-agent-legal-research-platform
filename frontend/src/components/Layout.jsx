import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  HiOutlineScale, 
  HiOutlineChat, 
  HiOutlineLogout,
  HiOutlineMenu,
  HiOutlineX,
  HiOutlineUser,
  HiOutlineHome
} from 'react-icons/hi'
import { useAuthStore } from '../store/authStore'

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HiOutlineHome },
    { name: 'Chat', href: '/chat', icon: HiOutlineChat },
  ]

  return (
    <div className="min-h-screen flex">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-72 
        bg-navy-900/95 backdrop-blur-xl border-r border-navy-700/50
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:static lg:w-64
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-navy-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <HiOutlineScale className="w-6 h-6 text-navy-950" />
            </div>
            <div>
              <h1 className="font-display font-bold text-xl gradient-text">LexiQ</h1>
              <p className="text-xs text-gray-500">Legal AI Assistant</p>
            </div>
          </div>
          <button 
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 text-gray-400 hover:text-white"
          >
            <HiOutlineX className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                ${isActive 
                  ? 'bg-primary-500/10 text-primary-400 border border-primary-500/30' 
                  : 'text-gray-400 hover:bg-navy-800/50 hover:text-white border border-transparent'
                }
              `}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-navy-700/50">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-navy-800/30">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500/30 to-primary-700/30 flex items-center justify-center border border-primary-500/30">
              <HiOutlineUser className="w-5 h-5 text-primary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.full_name || user?.username}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role || 'User'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 
                     text-gray-400 hover:text-red-400 hover:bg-red-500/10 
                     rounded-lg transition-all duration-200"
          >
            <HiOutlineLogout className="w-5 h-5" />
            <span className="font-medium">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Mobile header */}
        <header className="lg:hidden h-16 flex items-center justify-between px-4 border-b border-navy-700/50 bg-navy-900/80 backdrop-blur-xl">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 text-gray-400 hover:text-white"
          >
            <HiOutlineMenu className="w-6 h-6" />
          </button>
          <div className="flex items-center gap-2">
            <HiOutlineScale className="w-6 h-6 text-primary-500" />
            <span className="font-display font-bold text-lg gradient-text">LexiQ</span>
          </div>
          <div className="w-10" /> {/* Spacer for centering */}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="p-4 md:p-6 lg:p-8"
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}

export default Layout

