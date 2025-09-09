import React from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { 
  Building2, 
  FileText, 
  Shield, 
  Clock,
  TrendingUp,
  CheckCircle
} from 'lucide-react'

export const DashboardPage: React.FC = () => {
  const { user } = useAuth()

  const stats = [
    {
      title: 'Active Entities',
      value: '3',
      icon: Building2,
      change: '+1 this month',
      color: 'text-blue-400'
    },
    {
      title: 'Documents',
      value: '24',
      icon: FileText,
      change: '+5 this week',
      color: 'text-green-400'
    },
    {
      title: 'Compliance Items',
      value: '8',
      icon: Shield,
      change: '2 pending',
      color: 'text-yellow-400'
    },
    {
      title: 'Upcoming Deadlines',
      value: '3',
      icon: Clock,
      change: 'Next 30 days',
      color: 'text-red-400'
    }
  ]

  const recentActivities = [
    {
      id: 1,
      action: 'Document uploaded',
      entity: 'Acme LLC',
      time: '2 hours ago',
      icon: FileText
    },
    {
      id: 2,
      action: 'Compliance check completed',
      entity: 'Acme LLC',
      time: '1 day ago',
      icon: CheckCircle
    },
    {
      id: 3,
      action: 'Annual report filed',
      entity: 'Beta Corp',
      time: '3 days ago',
      icon: TrendingUp
    }
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-3xl font-bold text-gradient mb-2">
          Dashboard
        </h1>
        <p className="text-white/70">
          Welcome back, {user?.first_name}! Here's what's happening with your legal operations.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/60 text-sm">{stat.title}</p>
                <p className="text-3xl font-bold text-white mt-1">{stat.value}</p>
                <p className={`text-sm ${stat.color} mt-1`}>{stat.change}</p>
              </div>
              <div className={`p-3 rounded-lg bg-white/10 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="card-title">Recent Activity</h3>
            <p className="card-description">Your latest legal operations</p>
          </div>
          <div className="space-y-4">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-white/10">
                  <activity.icon className="w-4 h-4 text-white/60" />
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium">{activity.action}</p>
                  <p className="text-white/60 text-sm">{activity.entity}</p>
                </div>
                <p className="text-white/40 text-sm">{activity.time}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="card"
        >
          <div className="card-header">
            <h3 className="card-title">Quick Actions</h3>
            <p className="card-description">Common tasks and shortcuts</p>
          </div>
          <div className="space-y-3">
            <button className="btn-primary w-full justify-start">
              <Building2 className="w-4 h-4 mr-2" />
              Create New Entity
            </button>
            <button className="btn-secondary w-full justify-start">
              <FileText className="w-4 h-4 mr-2" />
              Upload Document
            </button>
            <button className="btn-ghost w-full justify-start">
              <Shield className="w-4 h-4 mr-2" />
              Check Compliance
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
