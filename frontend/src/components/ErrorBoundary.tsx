import React, { Component, ErrorInfo, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Link } from 'react-router-dom'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ error, errorInfo })
    
    // Log error to monitoring service
    if (window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      })
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-md"
          >
            <div className="card">
              <div className="mb-8">
                <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <AlertTriangle className="w-8 h-8 text-red-400" />
                </div>
                <h1 className="text-2xl font-bold text-white mb-2">
                  Something went wrong
                </h1>
                <p className="text-white/70 mb-4">
                  We're sorry, but something unexpected happened. Please try again.
                </p>
                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details className="text-left bg-white/5 p-4 rounded-lg mb-4">
                    <summary className="text-white/80 cursor-pointer mb-2">
                      Error Details (Development)
                    </summary>
                    <pre className="text-red-400 text-xs overflow-auto">
                      {this.state.error.toString()}
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </details>
                )}
              </div>

              <div className="space-y-4">
                <button
                  onClick={this.handleRetry}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-5 h-5" />
                  Try Again
                </button>
                <Link
                  to="/"
                  className="btn-ghost w-full flex items-center justify-center gap-2"
                >
                  <Home className="w-5 h-5" />
                  Go Home
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      )
    }

    return this.props.children
  }
}

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  
  // Log to monitoring service
  if (window.Sentry) {
    window.Sentry.captureException(event.reason)
  }
})

// Global error handler for uncaught errors
window.addEventListener('error', (event) => {
  console.error('Uncaught error:', event.error)
  
  // Log to monitoring service
  if (window.Sentry) {
    window.Sentry.captureException(event.error)
  }
})
