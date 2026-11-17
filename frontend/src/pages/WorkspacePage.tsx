import React, { useState } from 'react'
import { Plus, Layers, Building2, Users, Calendar, ArrowRight, Check } from 'lucide-react'
import { useWorkspace } from '../context/WorkspaceContext'
import { useAuth } from '../context/AuthContext'
import { workspacesApi } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'

export function WorkspacePage() {
  const { workspaces, currentWorkspace, setCurrentWorkspace, refreshWorkspaces, isDemoMode, setDemoMode } = useWorkspace()
  const { isAuthenticated } = useAuth()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const created = await workspacesApi.create({ name, description })
      await refreshWorkspaces()
      setCurrentWorkspace(created)
      setDemoMode(false)
      setShowCreateModal(false)
      setName('')
      setDescription('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workspace. Are you logged in?')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Building2 className="h-6 w-6 text-teal-600 dark:text-teal-400" />
            Business Workspaces
          </h1>
          <p className="text-sm text-muted-foreground">
            Manage multi-tenant business units and data boundaries
          </p>
        </div>
        <Button
          variant="teal"
          className="gap-2 shrink-0"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="h-4 w-4" />
          New Workspace
        </Button>
      </div>

      {/* Workspace List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workspaces.map((ws) => {
          const isSelected = currentWorkspace?.id === ws.id
          return (
            <Card
              key={ws.id}
              className={`relative overflow-hidden transition-all ${
                isSelected
                  ? 'border-teal-500 shadow-md ring-1 ring-teal-500'
                  : 'hover:border-muted-foreground/30'
              }`}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="p-2.5 rounded-lg bg-navy-50 dark:bg-navy-900 text-navy-800 dark:text-teal-400">
                    <Layers className="h-5 w-5" />
                  </div>
                  {isSelected && (
                    <Badge variant="teal" className="gap-1">
                      <Check className="h-3 w-3" />
                      Active
                    </Badge>
                  )}
                </div>
                <CardTitle className="pt-2 text-lg font-bold">{ws.name}</CardTitle>
                <CardDescription className="line-clamp-2">
                  {ws.description || 'No description provided.'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border pt-3">
                  <span className="flex items-center gap-1">
                    <Users className="h-3.5 w-3.5" />
                    {ws.member_count} Member{ws.member_count !== 1 ? 's' : ''}
                  </span>
                  <span className="flex items-center gap-1 font-mono text-[11px]">
                    <Calendar className="h-3.5 w-3.5" />
                    {new Date(ws.created_at).toLocaleDateString()}
                  </span>
                </div>

                <Button
                  variant={isSelected ? 'outline' : 'secondary'}
                  size="sm"
                  className="w-full gap-1.5"
                  onClick={() => {
                    setCurrentWorkspace(ws)
                    if (ws.id === 'demo-workspace-01') {
                      setDemoMode(true)
                    } else {
                      setDemoMode(false)
                    }
                  }}
                >
                  {isSelected ? 'Currently Selected' : 'Switch Workspace'}
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Create Modal Dialog */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <Card className="w-full max-w-md shadow-2xl">
            <CardHeader>
              <CardTitle>Create New Workspace</CardTitle>
              <CardDescription>
                Define a new isolated business domain for your company or client
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateWorkspace} className="space-y-4">
                {error && (
                  <div className="p-3 text-xs rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
                    {error}
                  </div>
                )}
                {!isAuthenticated && (
                  <div className="p-3 text-xs rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-400">
                    You are in guest mode. Sign in to save workspaces to the database.
                  </div>
                )}
                <div className="space-y-1">
                  <label className="text-xs font-medium text-foreground">Workspace Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Apex Industrial Europe"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-foreground">Description (Optional)</label>
                  <textarea
                    rows={3}
                    placeholder="Brief description of operations, regional territories, or suppliers..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
                <div className="flex items-center justify-end gap-2 pt-2">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setShowCreateModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="teal"
                    isLoading={isLoading}
                  >
                    Create Workspace
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
