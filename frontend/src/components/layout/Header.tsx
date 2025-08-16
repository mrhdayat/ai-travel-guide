import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Menu, X, Brain, MessageCircle, Camera, Calendar, User, LogOut, Sparkles } from 'lucide-react'
import { Button } from '../ui/button'
import { useAuth } from '../../contexts/AuthContext'

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()
  const { user, logout, demoLogin, isLoading } = useAuth()

  const navigation = [
    { name: 'Home', href: '/', icon: Brain },
    { name: 'Trip Planner', href: '/plan', icon: Calendar },
    { name: 'Vision AI', href: '/vision', icon: Camera },
    { name: 'AI Assistant', href: '/chat', icon: MessageCircle },
  ]

  const handleDemoLogin = async () => {
    try {
      await demoLogin()
    } catch (error) {
      console.error('Demo login failed:', error)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/90 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-20 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-3"
            >
              <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center shadow-lg">
                <Brain className="h-7 w-7 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  AI Travel Guide
                </span>
                <span className="text-xs text-gray-500 font-medium">Powered by IBM watsonx</span>
              </div>
            </motion.div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href

              return (
                <Link key={item.name} to={item.href}>
                  <motion.div
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className={`flex items-center space-x-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                        : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </motion.div>
                </Link>
              )
            })}
          </nav>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                {user.is_demo && (
                  <span className="text-xs bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-3 py-1 rounded-full font-semibold shadow-sm">
                    <Sparkles className="h-3 w-3 inline mr-1" />
                    Demo Mode
                  </span>
                )}
                <div className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                  <User className="h-5 w-5" />
                  <span>{user.full_name || user.email}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-gray-500 hover:text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-5 w-5" />
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleDemoLogin}
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-3 font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <Sparkles className="h-5 w-5 mr-2" />
                {isLoading ? 'Loading...' : 'Try Demo'}
              </Button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t py-4"
          >
            <nav className="flex flex-col space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsMenuOpen(false)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
              
              <div className="pt-4 border-t">
                {user ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2 px-3 py-2 text-sm">
                      <User className="h-4 w-4" />
                      <span>{user.full_name || user.email}</span>
                      {user.is_demo && (
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                          Demo
                        </span>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={logout}
                      className="w-full justify-start text-muted-foreground hover:text-foreground"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Logout
                    </Button>
                  </div>
                ) : (
                  <Button
                    onClick={handleDemoLogin}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                  >
                    {isLoading ? 'Loading...' : 'Demo Mode'}
                  </Button>
                )}
              </div>
            </nav>
          </motion.div>
        )}
      </div>
    </header>
  )
}

export default Header
