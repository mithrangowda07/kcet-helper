import React, { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/api'
import { Student } from '../types'

interface AuthContextType {
  user: Student | null
  tokens: { access: string; refresh: string } | null
  login: (email: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<Student | null>(null)
  const [tokens, setTokens] = useState<{ access: string; refresh: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load from localStorage on mount
    const storedTokens = localStorage.getItem('tokens')
    const storedUser = localStorage.getItem('user')
    
    if (storedTokens && storedUser) {
      try {
        setTokens(JSON.parse(storedTokens))
        setUser(JSON.parse(storedUser))
        authService.setTokens(JSON.parse(storedTokens))
      } catch (e) {
        console.error('Error loading auth data:', e)
        localStorage.removeItem('tokens')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password)
    setUser(response.student)
    setTokens(response.tokens)
    localStorage.setItem('tokens', JSON.stringify(response.tokens))
    localStorage.setItem('user', JSON.stringify(response.student))
    authService.setTokens(response.tokens)
  }

  const register = async (data: any) => {
    const response = await authService.register(data)
    setUser(response.student)
    setTokens(response.tokens)
    localStorage.setItem('tokens', JSON.stringify(response.tokens))
    localStorage.setItem('user', JSON.stringify(response.student))
    authService.setTokens(response.tokens)
  }

  const logout = () => {
    setUser(null)
    setTokens(null)
    localStorage.removeItem('tokens')
    localStorage.removeItem('user')
    authService.clearTokens()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        tokens,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

