import React from 'react'
import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Home, 
  Briefcase, 
  Building2, 
  FileText, 
  Shield, 
  Settings,
  LogOut
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Services', href: '/services', icon: Briefcase },
    { name: 'Entities', href: '/entities', icon: Building2 },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Compliance', href: '/compliance', icon: Shield },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3 }}
      className="w-64 glass-dark min-h-screen p-6"
    >
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gradient">
          Legal Ops
        </h1>
        <p className="text-white/60 text-sm">Platform</p>
      </div>

      <nav className="space-y-2 mb-8">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-white/20 text-white'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto">
        <div className="glass-card p-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-500/20 rounded-full flex items-center justify-center">
              <span className="text-primary-400 font-semibold">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </span>
            </div>
            <div>
              <p className="text-white font-medium">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-white/60 text-sm">{user?.email}</p>
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-all duration-200 w-full"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </button>
      </div>
    </motion.div>
  )
}
