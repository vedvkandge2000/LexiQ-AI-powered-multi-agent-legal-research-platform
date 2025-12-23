import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 180000, // 3 minutes for long analysis requests
})

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// =============================================================================
// Auth API
// =============================================================================

export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  getUser: async (username) => {
    const response = await api.get(`/auth/user/${username}`)
    return response.data
  },
}

// =============================================================================
// Analysis API
// =============================================================================

export const analysisAPI = {
  // Full analysis with all agents
  analyzeCase: async (caseText, options = {}) => {
    const response = await api.post('/analyze', {
      case_text: caseText,
      num_precedents: options.numPrecedents || 5,
      enable_statutes: options.enableStatutes ?? true,
      enable_news: options.enableNews ?? true,
      enable_bench: options.enableBench ?? true,
      user_id: options.userId,
    })
    return response.data
  },

  // Quick search without full analysis
  quickSearch: async (caseText, k = 10) => {
    const formData = new FormData()
    formData.append('case_text', caseText)
    formData.append('k', k)
    
    const response = await api.post('/analyze/quick-search', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  // Analyze PDF file
  analyzePDF: async (file, options = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('num_precedents', options.numPrecedents || 5)
    if (options.userId) formData.append('user_id', options.userId)

    const response = await api.post('/analyze/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  // Individual agent endpoints
  analyzeStatutes: async (caseText) => {
    const formData = new FormData()
    formData.append('case_text', caseText)
    const response = await api.post('/agents/statutes', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  analyzeNews: async (caseText, maxArticles = 5) => {
    const formData = new FormData()
    formData.append('case_text', caseText)
    formData.append('max_articles', maxArticles)
    const response = await api.post('/agents/news', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

// =============================================================================
// Chat API
// =============================================================================

export const chatAPI = {
  startChat: async (userId, caseText, caseTitle, similarCases) => {
    const response = await api.post('/chat/start', {
      user_id: userId,
      case_text: caseText,
      case_title: caseTitle,
      similar_cases: similarCases,
    })
    return response.data
  },

  sendMessage: async (sessionId, message, useRag = true) => {
    const response = await api.post('/chat/message', {
      session_id: sessionId,
      message,
      use_rag: useRag,
    })
    return response.data
  },

  getHistory: async (sessionId, limit = 50) => {
    const response = await api.get(`/chat/history/${sessionId}`, {
      params: { limit },
    })
    return response.data
  },

  getUserSessions: async (userId, limit = 20) => {
    const response = await api.get(`/chat/sessions/${userId}`, {
      params: { limit },
    })
    return response.data
  },

  deleteChat: async (sessionId) => {
    const response = await api.delete(`/chat/${sessionId}`)
    return response.data
  },

  exportChat: async (sessionId, format = 'markdown') => {
    const response = await api.get(`/chat/export/${sessionId}`, {
      params: { format },
    })
    return response.data
  },
}

// =============================================================================
// Report API
// =============================================================================

export const reportAPI = {
  generate: async (caseText, analysis) => {
    const formData = new FormData()
    formData.append('case_text', caseText)
    if (analysis.precedents) formData.append('precedents', analysis.precedents.analysis)
    if (analysis.statutes) formData.append('statutes', analysis.statutes.explanation)
    if (analysis.news) formData.append('news', analysis.news.analysis)
    if (analysis.bench) formData.append('bench', analysis.bench.analysis)

    const response = await api.post('/report/generate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export default api

