import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Bot,
  Cpu,
  BookOpen,
  TrendingUp,
} from 'lucide-react'
import { cn } from '../../lib/utils'

export function BottomNav() {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Copilot', path: '/copilot', icon: Bot },
    { name: 'ML', path: '/ml', icon: Cpu },
    { name: 'Knowledge', path: '/knowledge', icon: BookOpen },
    { name: 'Analytics', path: '/analytics', icon: TrendingUp },
  ]

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card/95 backdrop-blur-md pb-safe">
      <div className="grid grid-cols-5 h-16">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors',
                isActive
                  ? 'text-teal-600 dark:text-teal-400 font-semibold'
                  : 'text-muted-foreground hover:text-foreground'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={cn('h-5 w-5', isActive && 'scale-110 transition-transform')} />
                <span>{item.name}</span>
                {isActive && (
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-600 dark:bg-teal-400 absolute top-1.5" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
