import React from 'react'
import { motion } from 'framer-motion'
import { Plus, Building2, Calendar, FileText } from 'lucide-react'

export const EntitiesPage: React.FC = () => {
  const entities = [
    {
      id: 1,
      name: 'Acme LLC',
      type: 'LLC',
      status: 'Active',
      created: '2023-01-15',
      nextDeadline: 'Annual Report - March 15, 2024'
    },
    {
      id: 2,
      name: 'Beta Corporation',
      type: 'Corporation',
      status: 'Active',
      created: '2023-06-20',
      nextDeadline: 'Franchise Tax - May 1, 2024'
    }
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gradient mb-2">
            Business Entities
          </h1>
          <p className="text-white/70">
            Manage your business entities and track compliance requirements.
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Entity
        </button>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {entities.map((entity, index) => (
          <motion.div
            key={entity.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-lg bg-primary-500/20">
                  <Building2 className="w-6 h-6 text-primary-400" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">{entity.name}</h3>
                  <p className="text-white/60">{entity.type}</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-medium">
                {entity.status}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-3 text-white/70">
                <Calendar className="w-4 h-4" />
                <span>Created: {entity.created}</span>
              </div>
              <div className="flex items-center gap-3 text-yellow-400">
                <FileText className="w-4 h-4" />
                <span>{entity.nextDeadline}</span>
              </div>
            </div>

            <div className="mt-6 flex gap-3">
              <button className="btn-primary flex-1">View Details</button>
              <button className="btn-ghost">Manage</button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
