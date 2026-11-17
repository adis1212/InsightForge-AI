import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  UploadCloud,
  FileSpreadsheet,
  TrendingUp,
  Settings,
  Layers,
  ChevronRight,
  BookOpen,
  Sparkles,
  Cpu,
  Bot,
  FileText,
} from 'lucide-react'
import { cn } from '../../lib/utils'

export function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'AI Copilot', path: '/copilot', icon: Bot, badge: 'Stage 8' },
    { name: 'Executive Reports', path: '/reports', icon: FileText, badge: 'Stage 9' },
    { name: 'ML Intelligence', path: '/ml', icon: Cpu, badge: 'Stage 6' },
    { name: 'Knowledge Base', path: '/knowledge', icon: BookOpen, badge: 'Stage 7' },
    { name: 'Prompt Studio', path: '/prompt-studio', icon: Sparkles, badge: 'Stage 5' },
    { name: 'Datasets', path: '/datasets/upload', icon: UploadCloud },
    { name: 'Data Preview & Quality', path: '/datasets/preview', icon: FileSpreadsheet },
    { name: 'Business Analytics', path: '/analytics', icon: TrendingUp },
    { name: 'Workspaces', path: '/workspaces', icon: Layers },
    { name: 'Settings', path: '/settings', icon: Settings },
  ]

  return (
    <aside className="hidden md:flex flex-col w-64 border-r border-border bg-card shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="flex flex-col flex-1 p-4 space-y-6">
        {/* Navigation Group */}
        <div>
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-2">
            Intelligence Suite
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group',
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-sm dark:bg-teal-600/20 dark:text-teal-400 dark:border dark:border-teal-500/30'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  )
                }
              >
                <item.icon className="h-4 w-4 shrink-0 transition-transform group-hover:scale-110" />
                <span className="flex-1">{item.name}</span>
                {item.badge && (
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-teal-500/15 text-teal-700 dark:text-teal-400 border border-teal-500/20">
                    {item.badge}
                  </span>
                )}
                <ChevronRight className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Course Architecture Banner */}
        <div className="mt-auto p-3.5 rounded-xl bg-navy-50 dark:bg-navy-950/60 border border-navy-100 dark:border-navy-900 text-xs space-y-2">
          <div className="flex items-center gap-2 text-navy-800 dark:text-teal-400 font-semibold">
            <Cpu className="h-4 w-4 text-teal-600 dark:text-teal-400" />
            <span>ML + RAG (Stage 6–7)</span>
          </div>
          <p className="text-muted-foreground text-[11px] leading-relaxed">
            XGBoost forecasting, Isolation Forest screening, document RAG, and 3-stage grounded prompt chains.
          </p>
          <div className="pt-1 flex items-center justify-between text-[10px] text-muted-foreground border-t border-border/50">
            <span>Stage 1–7</span>
            <span className="font-mono text-teal-600 dark:text-teal-400 font-bold">ACTIVE</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
