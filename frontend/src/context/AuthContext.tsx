import React, { createContext, useContext, useState, useEffect } from 'react'
import type { User } from '../types'
import { authApi } from '../services/api'

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('insightforge_user')
    return saved ? JSON.parse(saved) : null
  })
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('insightforge_token')
  })
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const verifyAuth = async () => {
      const storedToken = localStorage.getItem('insightforge_token')
      if (storedToken) {
        try {
          const currentUser = await authApi.getMe()
          setUser(currentUser)
          localStorage.setItem('insightforge_user', JSON.stringify(currentUser))
        } catch (e) {
          // Token invalid or expired
          logout()
        }
      }
      setIsLoading(false)
    }

    verifyAuth()
  }, [])

  const login = (newToken: string, newUser: User) => {
    setToken(newToken)
    setUser(newUser)
    localStorage.setItem('insightforge_token', newToken)
    localStorage.setItem('insightforge_user', JSON.stringify(newUser))
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('insightforge_token')
    localStorage.removeItem('insightforge_user')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}
