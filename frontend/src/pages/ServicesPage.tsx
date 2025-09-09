import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle, Star } from 'lucide-react'

export const ServicesPage: React.FC = () => {
  const services = [
    {
      id: 1,
      name: 'Business Formation',
      description: 'Complete LLC, Corporation, and Partnership formation with AI-powered guidance.',
      price: '$299',
      features: ['AI-powered form completion', 'Real-time name checking', 'Registered agent service', 'Operating agreement'],
      popular: true
    },
    {
      id: 2,
      name: 'Compliance Management',
      description: 'Automated compliance tracking and deadline management for ongoing requirements.',
      price: '$99/month',
      features: ['Automated reminders', 'Compliance calendar', 'Document storage', 'Expert support'],
      popular: false
    },
    {
      id: 3,
      name: 'Document Generation',
      description: 'AI-powered legal document creation and management system.',
      price: '$149',
      features: ['Operating agreements', 'Bylaws generation', 'Contract templates', 'E-signature integration'],
      popular: false
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
          Our Services
        </h1>
        <p className="text-white/70">
          Choose from our comprehensive suite of legal services designed for modern businesses.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service, index) => (
          <motion.div
            key={service.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            className={`card relative ${service.popular ? 'ring-2 ring-primary-500/50' : ''}`}
          >
            {service.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <div className="bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center gap-1">
                  <Star className="w-4 h-4" />
                  Most Popular
                </div>
              </div>
            )}

            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-white mb-2">{service.name}</h3>
              <p className="text-white/70 mb-4">{service.description}</p>
              <div className="text-3xl font-bold text-primary-400">{service.price}</div>
            </div>

            <div className="space-y-3 mb-6">
              {service.features.map((feature, featureIndex) => (
                <div key={featureIndex} className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                  <span className="text-white/80">{feature}</span>
                </div>
              ))}
            </div>

            <button className={`w-full py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
              service.popular 
                ? 'bg-primary-600 hover:bg-primary-700 text-white' 
                : 'btn-primary'
            }`}>
              Get Started
              <ArrowRight className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
