import React from 'react'
import { motion } from 'framer-motion'
import { Shield, Calendar, AlertTriangle, CheckCircle, Clock } from 'lucide-react'

export const CompliancePage: React.FC = () => {
  const complianceItems = [
    {
      id: 1,
      title: 'Annual Report - Acme LLC',
      entity: 'Acme LLC',
      dueDate: '2024-03-15',
      status: 'pending',
      priority: 'high',
      description: 'Annual report filing required for LLC registration maintenance.'
    },
    {
      id: 2,
      title: 'Franchise Tax - Beta Corp',
      entity: 'Beta Corporation',
      dueDate: '2024-05-01',
      status: 'pending',
      priority: 'medium',
      description: 'Annual franchise tax payment required for corporation.'
    },
    {
      id: 3,
      title: 'Registered Agent Update',
      entity: 'Acme LLC',
      dueDate: '2024-01-30',
      status: 'completed',
      priority: 'low',
      description: 'Registered agent information updated successfully.'
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-400" />
      default:
        return <AlertTriangle className="w-5 h-5 text-red-400" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500/20 text-red-400'
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400'
      case 'low':
        return 'bg-green-500/20 text-green-400'
      default:
        return 'bg-gray-500/20 text-gray-400'
    }
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-3xl font-bold text-gradient mb-2">
          Compliance Management
        </h1>
        <p className="text-white/70">
          Track and manage compliance requirements for all your business entities.
        </p>
      </motion.div>

      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-red-500/20">
              <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <p className="text-white/60 text-sm">Overdue</p>
              <p className="text-2xl font-bold text-white">2</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-yellow-500/20">
              <Clock className="w-6 h-6 text-yellow-400" />
            </div>
            <div>
              <p className="text-white/60 text-sm">Due Soon</p>
              <p className="text-2xl font-bold text-white">3</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-green-500/20">
              <CheckCircle className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-white/60 text-sm">Completed</p>
              <p className="text-2xl font-bold text-white">8</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Compliance Items */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="card"
      >
        <div className="card-header">
          <h3 className="card-title">Compliance Items</h3>
          <p className="card-description">Track all compliance requirements and deadlines</p>
        </div>

        <div className="space-y-4">
          {complianceItems.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="glass p-4 rounded-lg"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  {getStatusIcon(item.status)}
                  <div>
                    <h4 className="text-white font-semibold">{item.title}</h4>
                    <p className="text-white/60 text-sm">{item.entity}</p>
                    <p className="text-white/70 text-sm mt-1">{item.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(item.priority)}`}>
                    {item.priority}
                  </span>
                  <div className="text-right">
                    <p className="text-white/60 text-sm">Due Date</p>
                    <p className="text-white font-medium">{item.dueDate}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
