import React, { createContext, useContext, useState, useEffect } from 'react'
import type { Workspace, Dataset } from '../types'
import { workspacesApi, datasetsApi } from '../services/api'
import { DEMO_WORKSPACE, DEMO_DATASET } from '../services/demoData'
import { useAuth } from './AuthContext'

interface WorkspaceContextType {
  workspaces: Workspace[]
  currentWorkspace: Workspace | null
  datasets: Dataset[]
  currentDataset: Dataset | null
  isDemoMode: boolean
  isLoading: boolean
  setCurrentWorkspace: (workspace: Workspace) => void
  setCurrentDataset: (dataset: Dataset | null) => void
  setDemoMode: (isDemo: boolean) => void
  refreshWorkspaces: () => Promise<void>
  refreshDatasets: () => Promise<void>
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined)

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [currentDataset, setCurrentDataset] = useState<Dataset | null>(null)
  const [isDemoMode, setIsDemoMode] = useState<boolean>(true)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const refreshWorkspaces = async () => {
    if (!isAuthenticated) return
    setIsLoading(true)
    try {
      const list = await workspacesApi.list()
      setWorkspaces(list)
      if (list.length > 0 && !currentWorkspace) {
        setCurrentWorkspace(list[0])
      }
    } catch (e) {
      console.warn('Could not fetch workspaces, falling back to demo mode:', e)
      setIsDemoMode(true)
      setCurrentWorkspace(DEMO_WORKSPACE)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshDatasets = async () => {
    if (isDemoMode || !currentWorkspace) {
      setDatasets([DEMO_DATASET])
      setCurrentDataset(DEMO_DATASET)
      return
    }
    try {
      const list = await datasetsApi.list(currentWorkspace.id)
      setDatasets(list)
      if (list.length > 0) {
        setCurrentDataset(list[0])
      } else {
        setCurrentDataset(null)
      }
    } catch (e) {
      console.warn('Could not fetch datasets:', e)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      refreshWorkspaces()
    } else {
      // In guest/demo state, set demo workspace
      setWorkspaces([DEMO_WORKSPACE])
      setCurrentWorkspace(DEMO_WORKSPACE)
      setDatasets([DEMO_DATASET])
      setCurrentDataset(DEMO_DATASET)
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (currentWorkspace && !isDemoMode) {
      refreshDatasets()
    }
  }, [currentWorkspace, isDemoMode])

  const setDemoMode = (val: boolean) => {
    setIsDemoMode(val)
    if (val) {
      setCurrentWorkspace(DEMO_WORKSPACE)
      setDatasets([DEMO_DATASET])
      setCurrentDataset(DEMO_DATASET)
    }
  }

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        currentWorkspace: currentWorkspace || DEMO_WORKSPACE,
        datasets,
        currentDataset: currentDataset || DEMO_DATASET,
        isDemoMode,
        isLoading,
        setCurrentWorkspace,
        setCurrentDataset,
        setDemoMode,
        refreshWorkspaces,
        refreshDatasets,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  )
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext)
  if (!context) throw new Error('useWorkspace must be used within a WorkspaceProvider')
  return context
}
