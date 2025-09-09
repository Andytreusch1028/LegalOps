import React from 'react'
import { motion } from 'framer-motion'
import { Bell, Search } from 'lucide-react'

export const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ y: -50 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3 }}
      className="glass-dark p-4 border-b border-white/10"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-semibold text-white">
            Welcome back!
          </h2>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="text"
              placeholder="Search..."
              className="glass-input pl-10 pr-4 py-2 w-64"
            />
          </div>

          <button 
            className="glass-button p-2 relative"
            title="Notifications"
            aria-label="View notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full" aria-label="3 unread notifications"></span>
          </button>
        </div>
      </div>
    </motion.header>
  )
}
