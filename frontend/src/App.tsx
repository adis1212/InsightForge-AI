import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import { WorkspaceProvider } from './context/WorkspaceContext'
import { AppLayout } from './components/layout/AppLayout'

// Pages
import { LandingPage } from './pages/LandingPage'
import { AuthPage } from './pages/AuthPage'
import { WorkspacePage } from './pages/WorkspacePage'
import { DashboardOverviewPage } from './pages/DashboardOverviewPage'
import { DatasetUploadPage } from './pages/DatasetUploadPage'
import { DatasetPreviewPage } from './pages/DatasetPreviewPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { MLIntelligencePage } from './pages/MLIntelligencePage'
import { PromptStudioPage } from './pages/PromptStudioPage'
import { KnowledgeBasePage } from './pages/KnowledgeBasePage'
import { AICopilotPage } from './pages/AICopilotPage'
import { SettingsPage } from './pages/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <WorkspaceProvider>
            <BrowserRouter>
              <Routes>
                {/* Public standalone auth route */}
                <Route path="/auth" element={<AuthPage />} />

                {/* Main app wrapped in AppLayout */}
                <Route element={<AppLayout />}>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/dashboard" element={<DashboardOverviewPage />} />
                  <Route path="/prompt-studio" element={<PromptStudioPage />} />
                  <Route path="/workspaces" element={<WorkspacePage />} />
                  <Route path="/datasets/upload" element={<DatasetUploadPage />} />
                  <Route path="/datasets/preview" element={<DatasetPreviewPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/ml" element={<MLIntelligencePage />} />
                  <Route path="/ml-intelligence" element={<MLIntelligencePage />} />
                  <Route path="/knowledge" element={<KnowledgeBasePage />} />
                  <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
                  <Route path="/copilot" element={<AICopilotPage />} />
                  <Route path="/ai-copilot" element={<AICopilotPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Route>

                {/* Fallback redirect */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </WorkspaceProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
