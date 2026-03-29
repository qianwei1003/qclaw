import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Server,
  Play,
  Square,
  RefreshCw,
  Activity,
  Clock,
  Cpu,
  HardDrive,
  Zap,
  AlertCircle,
} from 'lucide-react'
import './Dashboard.css'

interface GatewayStatus {
  running: boolean
  uptime: string
  version: string
  port: number
  cpu: number
  memory: number
  lastCheck: Date
}

const defaultStatus: GatewayStatus = {
  running: false,
  uptime: '0h 0m',
  version: '1.0.0',
  port: 18789,
  cpu: 0,
  memory: 0,
  lastCheck: new Date(),
}

export default function Dashboard() {
  const [status, setStatus] = useState<GatewayStatus>(defaultStatus)
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  // Simulated status check - in real app, this would call Gateway API
  const checkStatus = async () => {
    setLoading(true)
    try {
      // Simulated response - replace with actual API call
      const response = await fetch('http://localhost:18789/api/status')
      if (response.ok) {
        const data = await response.json()
        setStatus({
          ...data,
          lastCheck: new Date(),
        })
      } else {
        setStatus(prev => ({ ...prev, running: false, lastCheck: new Date() }))
      }
    } catch {
      setStatus(prev => ({ ...prev, running: false, lastCheck: new Date() }))
    }
    setLoading(false)
  }

  // Start Gateway
  const startGateway = async () => {
    setActionLoading('start')
    try {
      // In real app, this would trigger the actual start command
      // For now, simulate the action
      await new Promise(resolve => setTimeout(resolve, 1500))
      setStatus(prev => ({ 
        ...prev, 
        running: true, 
        uptime: '0h 0m',
        lastCheck: new Date() 
      }))
    } catch (error) {
      console.error('Failed to start Gateway:', error)
    }
    setActionLoading(null)
  }

  // Stop Gateway
  const stopGateway = async () => {
    setActionLoading('stop')
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      setStatus(prev => ({ ...prev, running: false }))
    } catch (error) {
      console.error('Failed to stop Gateway:', error)
    }
    setActionLoading(null)
  }

  // Restart Gateway
  const restartGateway = async () => {
    setActionLoading('restart')
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      setStatus(prev => ({ 
        ...prev, 
        uptime: '0h 0m',
        lastCheck: new Date() 
      }))
    } catch (error) {
      console.error('Failed to restart Gateway:', error)
    }
    setActionLoading(null)
  }

  useEffect(() => {
    checkStatus()
    // Auto-refresh every 10 seconds
    const interval = setInterval(checkStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <motion.div
      className="dashboard"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Header */}
      <motion.div className="page-header" variants={itemVariants}>
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">Monitor and control your OpenClaw Gateway</p>
      </motion.div>

      {/* Gateway Control Card */}
      <motion.div className="card gateway-card" variants={itemVariants}>
        <div className="gateway-header">
          <div className="gateway-status">
            <div className={`status-indicator-large ${status.running ? 'online' : 'offline'}`}>
              <div className="status-pulse" />
            </div>
            <div className="status-info">
              <h2 className="gateway-title">Gateway {status.running ? 'Running' : 'Stopped'}</h2>
              <p className="gateway-subtitle">
                {status.running 
                  ? `v${status.version} • Port ${status.port} • Uptime ${status.uptime}`
                  : 'Click Start to launch the Gateway'
                }
              </p>
            </div>
          </div>
          <div className="gateway-actions">
            {!status.running ? (
              <motion.button
                className="btn btn-primary btn-lg"
                onClick={startGateway}
                disabled={actionLoading === 'start'}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {actionLoading === 'start' ? (
                  <div className="spinner" />
                ) : (
                  <Play size={18} />
                )}
                Start Gateway
              </motion.button>
            ) : (
              <>
                <motion.button
                  className="btn btn-secondary"
                  onClick={restartGateway}
                  disabled={actionLoading === 'restart'}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {actionLoading === 'restart' ? (
                    <div className="spinner" />
                  ) : (
                    <RefreshCw size={16} className={actionLoading === 'restart' ? 'spin' : ''} />
                  )}
                  Restart
                </motion.button>
                <motion.button
                  className="btn btn-danger"
                  onClick={stopGateway}
                  disabled={actionLoading === 'stop'}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {actionLoading === 'stop' ? (
                    <div className="spinner" />
                  ) : (
                    <Square size={16} />
                  )}
                  Stop
                </motion.button>
              </>
            )}
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <motion.div className="grid grid-4" variants={itemVariants}>
        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <Cpu size={20} />
            </div>
            <span className={`badge ${status.cpu < 50 ? 'badge-success' : status.cpu < 80 ? 'badge-warning' : 'badge-error'}`}>
              {status.cpu}%
            </span>
          </div>
          <div className="stat-value">{status.cpu}%</div>
          <div className="stat-label">CPU Usage</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <HardDrive size={20} />
            </div>
            <span className={`badge ${status.memory < 60 ? 'badge-success' : status.memory < 85 ? 'badge-warning' : 'badge-error'}`}>
              {status.memory}%
            </span>
          </div>
          <div className="stat-value">{status.memory}%</div>
          <div className="stat-label">Memory</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <Activity size={20} />
            </div>
            <span className={`badge ${status.running ? 'badge-success' : 'badge-error'}`}>
              {status.running ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="stat-value">{status.running ? 'Up' : 'Down'}</div>
          <div className="stat-label">Gateway Status</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon">
              <Clock size={20} />
            </div>
          </div>
          <div className="stat-value" style={{ fontSize: '18px' }}>{status.uptime}</div>
          <div className="stat-label">Uptime</div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants}>
        <h3 className="section-title">Quick Actions</h3>
        <div className="quick-actions">
          <motion.button
            className="quick-action-btn"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <Zap size={24} className="quick-action-icon" />
            <span className="quick-action-label">Run Doctor</span>
            <span className="quick-action-desc">Diagnose system issues</span>
          </motion.button>

          <motion.button
            className="quick-action-btn"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <Server size={24} className="quick-action-icon" />
            <span className="quick-action-label">Open Control UI</span>
            <span className="quick-action-desc">Access built-in dashboard</span>
          </motion.button>

          <motion.button
            className="quick-action-btn"
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <AlertCircle size={24} className="quick-action-icon" />
            <span className="quick-action-label">Security Audit</span>
            <span className="quick-action-desc">Check configuration security</span>
          </motion.button>

          <motion.button
            className="quick-action-btn"
            onClick={checkStatus}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <RefreshCw size={24} className={`quick-action-icon ${loading ? 'spin' : ''}`} />
            <span className="quick-action-label">Refresh Status</span>
            <span className="quick-action-desc">Update current metrics</span>
          </motion.button>
        </div>
      </motion.div>

      {/* System Info */}
      <motion.div className="card system-info-card" variants={itemVariants}>
        <div className="card-header">
          <h3 className="card-title">System Information</h3>
        </div>
        <div className="system-info-grid">
          <div className="info-row">
            <span className="info-label">Version</span>
            <span className="info-value mono">v{status.version}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Port</span>
            <span className="info-value mono">{status.port}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Last Check</span>
            <span className="info-value mono">
              {status.lastCheck.toLocaleTimeString()}
            </span>
          </div>
          <div className="info-row">
            <span className="info-label">Platform</span>
            <span className="info-value mono">Windows</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
