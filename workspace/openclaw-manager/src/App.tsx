import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Brain,
  Puzzle,
  Settings,
  Shield,
  Server,
  Menu,
  X,
  Zap,
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Models from './pages/Models'
import Skills from './pages/Skills'
import System from './pages/System'
import './App.css'

type Page = 'dashboard' | 'models' | 'skills' | 'system'

const navItems = [
  { id: 'dashboard' as Page, label: 'Dashboard', icon: LayoutDashboard },
  { id: 'models' as Page, label: 'Models', icon: Brain },
  { id: 'skills' as Page, label: 'Skills', icon: Puzzle },
  { id: 'system' as Page, label: 'System', icon: Settings },
]

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="app">
      {/* Sidebar */}
      <motion.aside
        className="sidebar"
        initial={{ width: 240 }}
        animate={{ width: sidebarOpen ? 240 : 72 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      >
        <div className="sidebar-header">
          <motion.div
            className="logo"
            animate={{ opacity: sidebarOpen ? 1 : 0 }}
            transition={{ duration: 0.2 }}
          >
            {sidebarOpen && (
              <>
                <Zap className="logo-icon" />
                <span className="logo-text">OpenClaw</span>
              </>
            )}
          </motion.div>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        <nav className="nav">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentPage === item.id
            return (
              <motion.button
                key={item.id}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id)}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon size={20} className="nav-icon" />
                <AnimatePresence>
                  {sidebarOpen && (
                    <motion.span
                      className="nav-label"
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            )
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <div className="status-dot online" />
            {sidebarOpen && <span className="status-text">Connected</span>}
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="main">
        <AnimatePresence mode="wait">
          {currentPage === 'dashboard' && <Dashboard key="dashboard" />}
          {currentPage === 'models' && <Models key="models" />}
          {currentPage === 'skills' && <Skills key="skills" />}
          {currentPage === 'system' && <System key="system" />}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
