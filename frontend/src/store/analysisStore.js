import { create } from 'zustand'

export const useAnalysisStore = create((set, get) => ({
  // Current analysis state
  currentAnalysis: null,
  isLoading: false,
  error: null,
  
  // Analysis history
  analysisHistory: [],

  // Agent toggles
  agents: {
    precedents: true,
    statutes: true,
    news: true,
    bench: true,
  },

  // Settings
  settings: {
    numPrecedents: 5,
  },

  // Actions
  setAgentEnabled: (agent, enabled) => {
    set((state) => ({
      agents: { ...state.agents, [agent]: enabled }
    }))
  },

  setNumPrecedents: (num) => {
    set((state) => ({
      settings: { ...state.settings, numPrecedents: num }
    }))
  },

  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),

  setCurrentAnalysis: (analysis) => {
    set({ currentAnalysis: analysis })
    // Add to history
    if (analysis) {
      set((state) => ({
        analysisHistory: [
          { ...analysis, timestamp: new Date().toISOString() },
          ...state.analysisHistory.slice(0, 9) // Keep last 10
        ]
      }))
    }
  },

  clearAnalysis: () => set({ currentAnalysis: null, error: null }),

  // Get analysis from history by ID
  getAnalysisById: (id) => {
    return get().analysisHistory.find(a => a.request_id === id)
  },
}))

