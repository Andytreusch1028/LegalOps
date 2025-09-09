import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Shield, Zap, Users, FileText, CheckCircle } from 'lucide-react'

export const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-900/20 via-purple-900/20 to-secondary-900/20" />
        <div className="relative container mx-auto px-4 py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-4xl mx-auto"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gradient">
              Legal Ops Platform
            </h1>
            <p className="text-xl md:text-2xl text-white/80 mb-8 leading-relaxed">
              AI-powered legal operations platform that makes business formation and compliance 
              management accessible, efficient, and cost-effective for everyone.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="btn-ghost text-lg px-8 py-4"
              >
                Sign In
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4 text-gradient">
              Why Choose Legal Ops Platform?
            </h2>
            <p className="text-xl text-white/70 max-w-2xl mx-auto">
              Experience the future of legal operations with our AI-powered platform
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-glow-primary transition-all duration-300"
              >
                <div className="text-primary-400 mb-4">
                  <feature.icon className="w-12 h-12" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-white/70">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="card text-center max-w-3xl mx-auto"
          >
            <h2 className="text-3xl font-bold mb-4 text-gradient">
              Ready to Transform Your Legal Operations?
            </h2>
            <p className="text-lg text-white/70 mb-8">
              Join thousands of businesses that trust Legal Ops Platform for their legal needs
            </p>
            <Link
              to="/register"
              className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2"
            >
              Start Your Journey
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

const features = [
  {
    icon: Zap,
    title: 'AI-Powered Efficiency',
    description: 'Leverage advanced AI for intelligent form completion, document generation, and compliance management.'
  },
  {
    icon: Shield,
    title: 'UPL Compliant',
    description: 'Built with Florida UPL regulations in mind, ensuring all services are legally compliant.'
  },
  {
    icon: Users,
    title: 'Expert Support',
    description: 'Access to legal professionals and comprehensive support throughout your business journey.'
  },
  {
    icon: FileText,
    title: 'Document Management',
    description: 'Secure document vault with version control, e-signatures, and automated workflows.'
  },
  {
    icon: CheckCircle,
    title: 'Compliance Tracking',
    description: 'Real-time compliance monitoring with automated reminders and deadline tracking.'
  },
  {
    icon: ArrowRight,
    title: 'Multi-State Ready',
    description: 'Scalable architecture ready for expansion to Delaware, New York, and beyond.'
  }
]
