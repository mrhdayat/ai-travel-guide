import React, { createContext, useContext, useState, useEffect } from 'react'

interface User {
  id: number
  email: string
  full_name?: string
  is_demo: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  demoLogin: () => Promise<void>
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      fetchUserInfo(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token is invalid
        localStorage.removeItem('token')
        setToken(null)
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      const data = await response.json()
      const authToken = data.access_token

      localStorage.setItem('token', authToken)
      setToken(authToken)
      
      await fetchUserInfo(authToken)
    } catch (error) {
      console.error('Login error:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const demoLogin = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/demo-login`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Demo login failed')
      }

      const data = await response.json()
      const authToken = data.access_token

      localStorage.setItem('token', authToken)
      setToken(authToken)
      
      await fetchUserInfo(authToken)
    } catch (error) {
      console.error('Demo login error:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    demoLogin,
    isLoading,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
