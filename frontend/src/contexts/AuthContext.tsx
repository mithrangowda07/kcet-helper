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

  // Helper to persist user and tokens consistently
  const setAndPersistTokens = (t: { access: string; refresh: string }) => {
    setTokens(t)
    localStorage.setItem('tokens', JSON.stringify(t))
    authService.setTokens(t)
  }
  const setAndPersistUser = (u: Student) => {
    setUser(u)
    localStorage.setItem('user', JSON.stringify(u))
  }

  useEffect(() => {
    // Hydrate from localStorage, then (if tokens exist) fetch fresh /auth/me
    const init = async () => {
      try {
        const storedTokens = localStorage.getItem('tokens')
        const storedUser = localStorage.getItem('user')

        if (storedTokens) {
          const parsedTokens = JSON.parse(storedTokens)
          setAndPersistTokens(parsedTokens)
        }
        if (storedUser) {
          setUser(JSON.parse(storedUser))
        }

        // If we have tokens, prefer a fresh user from /auth/me (ensures name is present)
        if (storedTokens) {
          const me = await authService.me()
          setAndPersistUser(me)
        }
      } catch (e) {
        console.error('Error during auth init:', e)
        localStorage.removeItem('tokens')
        localStorage.removeItem('user')
        setUser(null)
        setTokens(null)
        authService.clearTokens()
      } finally {
        setLoading(false)
      }
    }
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password)
    const t = response.tokens ?? { access: response.access, refresh: response.refresh }
    setAndPersistTokens(t)
    // Prefer user data returned from login response to avoid an immediate /auth/me/ 401
    if (response.student) {
      setAndPersistUser(response.student)
    } else {
      const me = await authService.me()
      setAndPersistUser(me)
    }
  }

  // Registration should NOT log the user in automatically.
  // It just creates the account; user will log in explicitly afterwards.
  const register = async (data: any) => {
    await authService.register(data)
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
