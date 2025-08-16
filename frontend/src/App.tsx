import { type FC } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Header from './components/layout/Header'
import Footer from './components/layout/Footer'
import HomePage from './pages/HomePage'
import PlanPage from './pages/PlanPage'
import VisionPage from './pages/VisionPage'
import ChatPage from './pages/ChatPage'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './components/ui/toast'

const App: FC = () => {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router>
          <div className="min-h-screen bg-background text-foreground">
            <Header />
            <motion.main
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="flex-1"
            >
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/plan" element={<PlanPage />} />
                <Route path="/vision" element={<VisionPage />} />
                <Route path="/chat" element={<ChatPage />} />
              </Routes>
            </motion.main>
            <Footer />
          </div>
        </Router>
      </ToastProvider>
    </AuthProvider>
  )
}

export default App
