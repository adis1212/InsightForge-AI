import React, { useState, useEffect } from 'react'
import {
  Settings,
  Shield,
  Palette,
  Server,
  Database,
  Moon,
  Sun,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'
import { useWorkspace } from '../context/WorkspaceContext'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import axios from 'axios'

export function SettingsPage() {
  const { theme, toggleTheme } = useTheme()
  const { user } = useAuth()
  const { currentWorkspace, isDemoMode, setDemoMode } = useWorkspace()
  const [backendHealth, setBackendHealth] = useState<'checking' | 'healthy' | 'unreachable'>('checking')

  const checkHealth = async () => {
    setBackendHealth('checking')
    try {
      const res = await axios.get('/api/v1/health', { timeout: 3000 })
      if (res.data?.status === 'healthy') {
        setBackendHealth('healthy')
      } else {
        setBackendHealth('unreachable')
      }
    } catch {
      setBackendHealth('unreachable')
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Settings className="h-6 w-6 text-teal-600 dark:text-teal-400" />
          System Settings & Diagnostics
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Configure application visual preferences, workspace parameters, and verify backend API connectivity
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Palette className="h-5 w-5 text-teal-600 dark:text-teal-400" />
              Visual Theme Identity
            </CardTitle>
            <CardDescription className="text-xs">
              Navy/slate/teal theme system with full light and dark mode support
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-card">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-md bg-muted text-foreground">
                  {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground">
                    Current Theme: <span className="capitalize">{theme}</span>
                  </p>
                  <p className="text-[11px] text-muted-foreground">
                    Optimized for high-contrast readability
                  </p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={toggleTheme} className="text-xs">
                Switch to {theme === 'dark' ? 'Light' : 'Dark'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Backend Health Check */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Server className="h-5 w-5 text-navy-800 dark:text-teal-400" />
              FastAPI Backend Gateway
            </CardTitle>
            <CardDescription className="text-xs">
              Live connectivity status to the local Python FastAPI server
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-card">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-md bg-muted">
                  {backendHealth === 'healthy' ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  ) : backendHealth === 'checking' ? (
                    <RefreshCw className="h-4 w-4 text-muted-foreground animate-spin" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-amber-500" />
                  )}
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground">
                    Endpoint: <span className="font-mono text-[11px]">/api/v1/health</span>
                  </p>
                  <p className="text-[11px] text-muted-foreground">
                    {backendHealth === 'healthy'
                      ? 'FastAPI 0.115 + PostgreSQL ready'
                      : backendHealth === 'checking'
                      ? 'Probing backend service...'
                      : 'Backend offline (using offline demo benchmark)'}
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={checkHealth}
                className="text-xs gap-1"
              >
                <RefreshCw className="h-3 w-3" />
                Check
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Workspace & Role Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <Shield className="h-5 w-5 text-teal-600 dark:text-teal-400" />
            Active Workspace Scope & Membership
          </CardTitle>
          <CardDescription className="text-xs">
            Multi-tenant boundary isolating customer datasets and calculation caches
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-muted/40 border border-border">
              <span className="text-muted-foreground text-[11px]">Workspace Name</span>
              <p className="font-semibold text-foreground mt-0.5">{currentWorkspace?.name}</p>
            </div>
            <div className="p-3 rounded-lg bg-muted/40 border border-border">
              <span className="text-muted-foreground text-[11px]">Assigned Role</span>
              <p className="font-semibold text-foreground capitalize mt-0.5">
                {currentWorkspace?.user_role || 'Owner'}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-muted/40 border border-border">
              <span className="text-muted-foreground text-[11px]">Data Ingestion Mode</span>
              <div className="mt-0.5">
                {isDemoMode ? (
                  <Badge variant="teal" className="text-[10px]">
                    Benchmark Demo Active
                  </Badge>
                ) : (
                  <Badge variant="success" className="text-[10px]">
                    Live PostgreSQL DB
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
