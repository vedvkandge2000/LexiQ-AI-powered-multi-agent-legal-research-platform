import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAnalysisStore } from '../store/analysisStore'

// This page shows a specific analysis from history
// For now, redirect to dashboard as we handle everything there
function AnalysisPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { getAnalysisById, setCurrentAnalysis } = useAnalysisStore()

  useEffect(() => {
    if (id) {
      const analysis = getAnalysisById(id)
      if (analysis) {
        setCurrentAnalysis(analysis)
      }
    }
    navigate('/dashboard')
  }, [id])

  return null
}

export default AnalysisPage

