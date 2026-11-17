import axios, { AxiosError } from 'axios'
import type {
  AuthResponse, User, Workspace, Dataset, DatasetPreview,
  QualityReport, AnalyticsResponse, KPISummary,
  ForecastResponse, AnomalyResponse,
  KnowledgeDocument, RetrievalResponse
} from '../types'

const API_BASE = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('insightforge_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('insightforge_token')
      localStorage.removeItem('insightforge_user')
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: async (data: { email: string; full_name: string; password: string }): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>('/auth/register', data)
    return res.data
  },
  login: async (data: { email: string; password: string }): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>('/auth/login', data)
    return res.data
  },
  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me')
    return res.data
  },
}

// Workspaces API
export const workspacesApi = {
  list: async (): Promise<Workspace[]> => {
    const res = await api.get<Workspace[]>('/workspaces/')
    return res.data
  },
  create: async (data: { name: string; description?: string }): Promise<Workspace> => {
    const res = await api.post<Workspace>('/workspaces/', data)
    return res.data
  },
  get: async (id: string): Promise<Workspace> => {
    const res = await api.get<Workspace>(`/workspaces/${id}`)
    return res.data
  },
  update: async (id: string, data: { name?: string; description?: string }): Promise<Workspace> => {
    const res = await api.put<Workspace>(`/workspaces/${id}`, data)
    return res.data
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/workspaces/${id}`)
  },
}

// Datasets API
export const datasetsApi = {
  list: async (workspaceId: string): Promise<Dataset[]> => {
    const res = await api.get<Dataset[]>(`/workspaces/${workspaceId}/datasets/`)
    return res.data
  },
  upload: async (workspaceId: string, file: File, name?: string): Promise<Dataset> => {
    const formData = new FormData()
    formData.append('file', file)
    if (name) formData.append('name', name)
    const res = await api.post<Dataset>(`/workspaces/${workspaceId}/datasets/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
  get: async (workspaceId: string, datasetId: string): Promise<Dataset> => {
    const res = await api.get<Dataset>(`/workspaces/${workspaceId}/datasets/${datasetId}`)
    return res.data
  },
  preview: async (workspaceId: string, datasetId: string, rows = 50): Promise<DatasetPreview> => {
    const res = await api.get<DatasetPreview>(`/workspaces/${workspaceId}/datasets/${datasetId}/preview?rows=${rows}`)
    return res.data
  },
  updateMapping: async (workspaceId: string, datasetId: string, mapping: Record<string, string>): Promise<Dataset> => {
    const res = await api.put<Dataset>(`/workspaces/${workspaceId}/datasets/${datasetId}/mapping`, { column_mapping: mapping })
    return res.data
  },
  getQuality: async (workspaceId: string, datasetId: string): Promise<QualityReport> => {
    const res = await api.get<QualityReport>(`/workspaces/${workspaceId}/datasets/${datasetId}/quality`)
    return res.data
  },
  delete: async (workspaceId: string, datasetId: string): Promise<void> => {
    await api.delete(`/workspaces/${workspaceId}/datasets/${datasetId}`)
  },
}

// Analytics API
export const analyticsApi = {
  getFull: async (workspaceId: string, datasetId: string): Promise<AnalyticsResponse> => {
    const res = await api.get<AnalyticsResponse>(`/workspaces/${workspaceId}/analytics/${datasetId}`)
    return res.data
  },
  getSummary: async (workspaceId: string, datasetId: string): Promise<KPISummary> => {
    const res = await api.get<KPISummary>(`/workspaces/${workspaceId}/analytics/${datasetId}/summary`)
    return res.data
  },
}

// Prompt Engineering API
export const promptsApi = {
  execute: async (
    workspaceId: string,
    datasetId: string,
    promptVersion: 'v1' | 'v2' = 'v2',
    providerType: string = 'local_demo'
  ): Promise<any> => {
    const res = await api.post(`/workspaces/${workspaceId}/prompts/execute`, {
      dataset_id: datasetId,
      prompt_version: promptVersion,
      provider_type: providerType,
    })
    return res.data
  },
  compare: async (
    workspaceId: string,
    datasetId: string,
    providerType: string = 'local_demo'
  ): Promise<any> => {
    const res = await api.post(`/workspaces/${workspaceId}/prompts/compare`, {
      dataset_id: datasetId,
      provider_type: providerType,
    })
    return res.data
  },
  getTemplates: async (workspaceId: string): Promise<any> => {
    const res = await api.get(`/workspaces/${workspaceId}/prompts/templates`)
    return res.data
  },
  getEvaluation: async (workspaceId: string): Promise<any> => {
    const res = await api.get(`/workspaces/${workspaceId}/prompts/evaluation`)
    return res.data
  },
  triggerEvaluation: async (workspaceId: string): Promise<any> => {
    const res = await api.post(`/workspaces/${workspaceId}/prompts/evaluate`)
    return res.data
  },
}

// Stage 6: Machine Learning Intelligence API
export const mlApi = {
  getForecast: async (
    workspaceId: string,
    datasetId: string,
    periods: number = 6
  ): Promise<ForecastResponse> => {
    const res = await api.get<ForecastResponse>(
      `/workspaces/${workspaceId}/analytics/${datasetId}/forecast?periods=${periods}`
    )
    return res.data
  },
  getAnomalies: async (
    workspaceId: string,
    datasetId: string,
    contamination: number = 0.03
  ): Promise<AnomalyResponse> => {
    const res = await api.get<AnomalyResponse>(
      `/workspaces/${workspaceId}/analytics/${datasetId}/anomalies?contamination=${contamination}`
    )
    return res.data
  },
}

// Stage 7: Knowledge Base RAG API
export const knowledgeApi = {
  upload: async (workspaceId: string, file: File, title?: string): Promise<KnowledgeDocument> => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    const res = await api.post<KnowledgeDocument>(
      `/workspaces/${workspaceId}/knowledge/upload`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return res.data
  },

  list: async (workspaceId: string): Promise<KnowledgeDocument[]> => {
    const res = await api.get<KnowledgeDocument[]>(`/workspaces/${workspaceId}/knowledge/`)
    return res.data
  },

  get: async (workspaceId: string, documentId: string): Promise<KnowledgeDocument> => {
    const res = await api.get<KnowledgeDocument>(`/workspaces/${workspaceId}/knowledge/${documentId}`)
    return res.data
  },

  delete: async (workspaceId: string, documentId: string): Promise<void> => {
    await api.delete(`/workspaces/${workspaceId}/knowledge/${documentId}`)
  },

  search: async (workspaceId: string, query: string, topK = 5): Promise<RetrievalResponse> => {
    const res = await api.post<RetrievalResponse>(`/workspaces/${workspaceId}/knowledge/search`, {
      query,
      top_k: topK,
    })
    return res.data
  },
}


// Stage 8: AI Copilot Agent API
export const agentApi = {
  chat: async (
    workspaceId: string,
    payload: {
      message: string
      dataset_id: string
      session_id?: string | null
      provider_type?: string
    }
  ): Promise<import('../types').AgentChatResponse> => {
    const res = await api.post(
      `/workspaces/${workspaceId}/agent/chat`,
      {
        message: payload.message,
        dataset_id: payload.dataset_id,
        session_id: payload.session_id || undefined,
        provider_type: payload.provider_type || 'local_demo',
        include_trace: true,
      }
    )
    return res.data
  },

  listSessions: async (
    workspaceId: string
  ): Promise<import('../types').ConversationSessionSummary[]> => {
    const res = await api.get(`/workspaces/${workspaceId}/agent/sessions`)
    return res.data
  },

  getSession: async (
    workspaceId: string,
    sessionId: string
  ): Promise<{ session_id: string; messages: import('../types').AgentChatResponse[] }> => {
    const res = await api.get(`/workspaces/${workspaceId}/agent/sessions/${sessionId}`)
    return res.data
  },
}


// Stage 9: Executive Reports API
export const reportsApi = {
  generate: async (
    workspaceId: string,
    payload: import('../types').ReportGenerateRequest
  ): Promise<import('../types').ReportDetail> => {
    const res = await api.post(
      `/workspaces/${workspaceId}/reports/generate`,
      payload
    )
    return res.data
  },

  list: async (
    workspaceId: string
  ): Promise<import('../types').ReportSummary[]> => {
    const res = await api.get(`/workspaces/${workspaceId}/reports/`)
    return res.data
  },

  get: async (
    workspaceId: string,
    reportId: string
  ): Promise<import('../types').ReportDetail> => {
    const res = await api.get(`/workspaces/${workspaceId}/reports/${reportId}`)
    return res.data
  },

  delete: async (
    workspaceId: string,
    reportId: string
  ): Promise<void> => {
    await api.delete(`/workspaces/${workspaceId}/reports/${reportId}`)
  },

  getDownloadUrl: (workspaceId: string, reportId: string): string => {
    return `/api/v1/workspaces/${workspaceId}/reports/${reportId}/download`
  },
}
