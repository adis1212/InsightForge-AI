import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Moon, Sun, Layers, Database, LogOut, User as UserIcon, Sparkles } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import { useWorkspace } from '../../context/WorkspaceContext'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'

export function Navbar() {
  const { theme, toggleTheme } = useTheme()
  const { user, isAuthenticated, logout } = useAuth()
  const { currentWorkspace, isDemoMode, setDemoMode } = useWorkspace()
  const navigate = useNavigate()

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-card/80 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-navy-900 dark:bg-teal-600 text-white shadow-sm transition-transform group-hover:scale-105">
              <Sparkles className="h-5 w-5 text-teal-400 dark:text-navy-950" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold tracking-tight text-base text-foreground flex items-center gap-1.5">
                InsightForge <span className="text-teal-600 dark:text-teal-400 font-extrabold text-xs px-1.5 py-0.5 rounded bg-teal-500/10">AI</span>
              </span>
              <span className="text-[10px] text-muted-foreground hidden sm:inline -mt-0.5">Augmented Analytics</span>
            </div>
          </Link>

          {/* Current Workspace Pill */}
          <div className="hidden lg:flex items-center gap-2 ml-4 pl-4 border-l border-border text-xs">
            <Layers className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="font-medium text-foreground">{currentWorkspace?.name}</span>
            {isDemoMode && (
              <Badge variant="teal" className="text-[10px] uppercase font-bold tracking-wider py-0 px-1.5">
                Benchmark Demo
              </Badge>
            )}
          </div>
        </div>

        {/* Right Action Icons */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* Demo Mode Toggle */}
          <button
            onClick={() => setDemoMode(!isDemoMode)}
            className={`hidden sm:flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-md border transition-colors ${
              isDemoMode
                ? 'bg-teal-500/10 border-teal-500/30 text-teal-700 dark:text-teal-400'
                : 'border-border text-muted-foreground hover:bg-muted'
            }`}
            title="Toggle Benchmark Demo Data vs Live Connected Database"
          >
            <Database className="h-3.5 w-3.5" />
            <span>{isDemoMode ? 'Demo Active' : 'Live DB Mode'}</span>
          </button>

          {/* Theme Toggle Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label="Toggle visual theme"
            className="text-muted-foreground hover:text-foreground h-9 w-9"
          >
            {theme === 'dark' ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4" />}
          </Button>

          {/* User Profile or Sign In */}
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex flex-col items-end text-xs">
                <span className="font-medium text-foreground">{user?.full_name}</span>
                <span className="text-muted-foreground text-[10px]">{user?.email}</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  logout()
                  navigate('/')
                }}
                title="Sign out"
                className="h-9 w-9 text-muted-foreground hover:text-destructive"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <Link to="/auth">
              <Button variant="primary" size="sm" className="gap-1.5">
                <UserIcon className="h-3.5 w-3.5" />
                <span>Sign In</span>
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
