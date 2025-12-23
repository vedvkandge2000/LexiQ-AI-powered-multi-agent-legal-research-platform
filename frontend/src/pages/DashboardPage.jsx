import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  HiOutlineScale, 
  HiOutlineNewspaper,
  HiOutlineBookOpen,
  HiOutlineUserGroup,
  HiOutlineSearch,
  HiOutlineAdjustments,
  HiOutlineShieldCheck,
  HiOutlineExclamation,
  HiOutlineDownload,
  HiOutlineChat,
  HiOutlineChevronDown
} from 'react-icons/hi'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import { useNavigate } from 'react-router-dom'
import { analysisAPI, chatAPI, reportAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { useAnalysisStore } from '../store/analysisStore'

// Tabs for results
const TABS = [
  { id: 'precedents', label: 'Precedents', icon: HiOutlineScale },
  { id: 'statutes', label: 'Statutes', icon: HiOutlineBookOpen },
  { id: 'news', label: 'News', icon: HiOutlineNewspaper },
  { id: 'bench', label: 'Bench', icon: HiOutlineUserGroup },
]

function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { 
    currentAnalysis, 
    setCurrentAnalysis, 
    isLoading, 
    setLoading,
    agents,
    setAgentEnabled,
    settings,
    setNumPrecedents
  } = useAnalysisStore()

  const [caseText, setCaseText] = useState('')
  const [activeTab, setActiveTab] = useState('precedents')
  const [showSettings, setShowSettings] = useState(false)
  const [startingChat, setStartingChat] = useState(false)

  const handleAnalyze = async () => {
    if (!caseText.trim()) {
      toast.error('Please enter case details to analyze')
      return
    }

    if (caseText.trim().length < 50) {
      toast.error('Please provide more details about the case (at least 50 characters)')
      return
    }

    setLoading(true)
    
    try {
      const result = await analysisAPI.analyzeCase(caseText, {
        numPrecedents: settings.numPrecedents,
        enableStatutes: agents.statutes,
        enableNews: agents.news,
        enableBench: agents.bench,
        userId: user?.username
      })
      
      if (result.success) {
        setCurrentAnalysis({ ...result, caseText })
        toast.success(`Analysis complete! Found ${result.precedents?.num_similar_cases || 0} similar cases.`)
      } else {
        toast.error(result.error || 'Analysis failed. Please try again.')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      toast.error('Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleStartChat = async () => {
    if (!currentAnalysis) return

    setStartingChat(true)
    try {
      const result = await chatAPI.startChat(
        user?.username,
        currentAnalysis.caseText,
        currentAnalysis.caseText?.substring(0, 100),
        currentAnalysis.precedents?.similar_cases
      )
      
      if (result.success) {
        toast.success('Chat session started!')
        navigate(`/chat/${result.session_id}`)
      } else {
        toast.error('Failed to start chat session')
      }
    } catch (error) {
      toast.error('Failed to start chat session')
    } finally {
      setStartingChat(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!currentAnalysis) return

    try {
      const result = await reportAPI.generate(currentAnalysis.caseText, {
        precedents: currentAnalysis.precedents,
        statutes: currentAnalysis.statutes,
        news: currentAnalysis.news,
        bench: currentAnalysis.bench
      })
      
      if (result.success) {
        // Create and download file
        const blob = new Blob([result.report], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = result.filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        toast.success('Report downloaded!')
      }
    } catch (error) {
      toast.error('Failed to generate report')
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Page header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-display font-semibold text-white">
            Case Analysis
          </h1>
          <p className="text-gray-400 mt-1">
            Enter your case details to find relevant precedents and insights
          </p>
        </div>
        
        {/* Quick stats */}
        {currentAnalysis && (
          <div className="flex items-center gap-4">
            <div className="badge badge-gold">
              {currentAnalysis.precedents?.num_similar_cases || 0} Precedents
            </div>
            {currentAnalysis.statutes?.num_provisions > 0 && (
              <div className="badge badge-success">
                {currentAnalysis.statutes.num_provisions} Statutes
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input section */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <HiOutlineSearch className="w-5 h-5 text-primary-500" />
            Case Details
          </h2>
          
          {/* Settings toggle */}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="btn btn-ghost text-sm"
          >
            <HiOutlineAdjustments className="w-5 h-5" />
            <span>Settings</span>
            <HiOutlineChevronDown className={`w-4 h-4 transition-transform ${showSettings ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Settings panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="pb-6 mb-6 border-b border-navy-700/50">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Number of precedents */}
                  <div>
                    <label className="input-label">Precedents to Find</label>
                    <select
                      value={settings.numPrecedents}
                      onChange={(e) => setNumPrecedents(Number(e.target.value))}
                      className="input text-sm"
                    >
                      {[3, 5, 7, 10].map(n => (
                        <option key={n} value={n}>{n} precedents</option>
                      ))}
                    </select>
                  </div>

                  {/* Agent toggles */}
                  {TABS.slice(1).map(tab => (
                    <div key={tab.id}>
                      <label className="input-label">Enable {tab.label}</label>
                      <button
                        onClick={() => setAgentEnabled(tab.id, !agents[tab.id])}
                        className={`w-full px-4 py-3 rounded-lg border transition-all ${
                          agents[tab.id]
                            ? 'bg-primary-500/10 border-primary-500/50 text-primary-400'
                            : 'bg-navy-800/50 border-navy-600 text-gray-400'
                        }`}
                      >
                        <div className="flex items-center justify-center gap-2">
                          <tab.icon className="w-5 h-5" />
                          <span>{agents[tab.id] ? 'Enabled' : 'Disabled'}</span>
                        </div>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Text input */}
        <textarea
          value={caseText}
          onChange={(e) => setCaseText(e.target.value)}
          placeholder="Describe your case facts, legal issues, parties involved, and any relevant details...

Example:
Case Title: Tech Company vs. State Government

Facts:
- Client is a tech company operating a social media platform
- State government passed a new law requiring pre-approval of all posts
- Law claims to prevent misinformation

Legal Issues:
- Is pre-approval/censorship constitutional?
- What are reasonable restrictions under Article 19(2)?"
          className="input min-h-[250px] resize-y text-base leading-relaxed"
          disabled={isLoading}
        />

        {/* Character count and analyze button */}
        <div className="flex items-center justify-between mt-4">
          <span className="text-sm text-gray-500">
            {caseText.length} characters
          </span>
          
          <button
            onClick={handleAnalyze}
            disabled={isLoading || !caseText.trim()}
            className="btn btn-primary"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <HiOutlineSearch className="w-5 h-5" />
                <span>Analyze Case</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Security notice */}
      {currentAnalysis?.security_check && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`card p-4 flex items-center gap-4 ${
            currentAnalysis.security_check.pii_detected 
              ? 'border-yellow-500/30 bg-yellow-500/5'
              : 'border-green-500/30 bg-green-500/5'
          }`}
        >
          {currentAnalysis.security_check.pii_detected ? (
            <>
              <HiOutlineExclamation className="w-6 h-6 text-yellow-500 flex-shrink-0" />
              <div>
                <p className="text-yellow-400 font-medium">Privacy Protection Active</p>
                <p className="text-sm text-gray-400">
                  {currentAnalysis.security_check.num_redactions} personal information item(s) were automatically redacted for privacy.
                </p>
              </div>
            </>
          ) : (
            <>
              <HiOutlineShieldCheck className="w-6 h-6 text-green-500 flex-shrink-0" />
              <div>
                <p className="text-green-400 font-medium">Security Check Passed</p>
                <p className="text-sm text-gray-400">No personal information detected in the case text.</p>
              </div>
            </>
          )}
        </motion.div>
      )}

      {/* Results section */}
      {currentAnalysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Results header with actions */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <h2 className="text-2xl font-display font-semibold text-white">Analysis Results</h2>
            <div className="flex items-center gap-3">
              <button
                onClick={handleStartChat}
                disabled={startingChat}
                className="btn btn-secondary"
              >
                {startingChat ? (
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <HiOutlineChat className="w-5 h-5" />
                )}
                <span>Start Chat</span>
              </button>
              <button
                onClick={handleDownloadReport}
                className="btn btn-secondary"
              >
                <HiOutlineDownload className="w-5 h-5" />
                <span>Download Report</span>
              </button>
            </div>
          </div>

          {/* Hallucination warning */}
          {currentAnalysis.hallucination_check?.has_hallucinations && (
            <div className="card p-4 border-orange-500/30 bg-orange-500/5">
              <div className="flex items-start gap-3">
                <HiOutlineExclamation className="w-6 h-6 text-orange-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-orange-400 font-medium">Verification Notice</p>
                  <p className="text-sm text-gray-400 mt-1">
                    {currentAnalysis.hallucination_check.num_suspected} reference(s) could not be verified against our database. 
                    Please verify these citations independently.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="border-b border-navy-700/50">
            <nav className="flex gap-1 overflow-x-auto pb-px">
              {TABS.map((tab) => {
                const hasData = currentAnalysis[tab.id]
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    disabled={!hasData}
                    className={`
                      flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap
                      border-b-2 transition-all duration-200
                      ${activeTab === tab.id
                        ? 'border-primary-500 text-primary-400'
                        : hasData
                          ? 'border-transparent text-gray-400 hover:text-white hover:border-gray-600'
                          : 'border-transparent text-gray-600 cursor-not-allowed'
                      }
                    `}
                  >
                    <tab.icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                    {tab.id === 'precedents' && currentAnalysis.precedents && (
                      <span className="ml-1 px-1.5 py-0.5 text-xs rounded bg-primary-500/20 text-primary-400">
                        {currentAnalysis.precedents.num_similar_cases}
                      </span>
                    )}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Tab content */}
          <div className="card p-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {activeTab === 'precedents' && currentAnalysis.precedents && (
                  <PrecedentsTab data={currentAnalysis.precedents} />
                )}
                {activeTab === 'statutes' && currentAnalysis.statutes && (
                  <StatutesTab data={currentAnalysis.statutes} />
                )}
                {activeTab === 'news' && currentAnalysis.news && (
                  <NewsTab data={currentAnalysis.news} />
                )}
                {activeTab === 'bench' && currentAnalysis.bench && (
                  <BenchTab data={currentAnalysis.bench} />
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </div>
  )
}

// Tab Components
function PrecedentsTab({ data }) {
  const [expandedCase, setExpandedCase] = useState(null)

  return (
    <div className="space-y-6">
      {/* AI Analysis */}
      <div className="markdown-content">
        <ReactMarkdown>{data.analysis}</ReactMarkdown>
      </div>

      {/* Similar Cases List */}
      {data.similar_cases && data.similar_cases.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-white mb-4">Referenced Cases</h3>
          <div className="space-y-3">
            {data.similar_cases.map((caseItem, index) => (
              <div
                key={index}
                className="card-hover p-4 cursor-pointer"
                onClick={() => setExpandedCase(expandedCase === index ? null : index)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-white">{caseItem.case_title}</h4>
                    <p className="text-sm text-gray-400 mt-1">{caseItem.citation}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className="text-xs text-gray-500">Case No: {caseItem.case_number}</span>
                      {caseItem.page_number && (
                        <span className="text-xs text-gray-500">Page: {caseItem.page_number}</span>
                      )}
                    </div>
                  </div>
                  <HiOutlineChevronDown 
                    className={`w-5 h-5 text-gray-400 transition-transform ${expandedCase === index ? 'rotate-180' : ''}`} 
                  />
                </div>
                
                <AnimatePresence>
                  {expandedCase === index && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-4 pt-4 border-t border-navy-700/50">
                        <p className="text-sm text-gray-400 leading-relaxed">
                          {caseItem.content_preview}
                        </p>
                        {caseItem.s3_url && (
                          <a
                            href={caseItem.s3_url.replace('s3://', 'https://').replace(/\/(.+?)\//, '.s3.amazonaws.com/')}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 mt-3 text-sm text-primary-400 hover:text-primary-300"
                            onClick={(e) => e.stopPropagation()}
                          >
                            📄 View Full PDF
                          </a>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StatutesTab({ data }) {
  return (
    <div className="space-y-6">
      {/* Provisions count */}
      <div className="flex items-center gap-4 pb-4 border-b border-navy-700/50">
        <div className="p-3 rounded-lg bg-primary-500/10">
          <HiOutlineBookOpen className="w-6 h-6 text-primary-500" />
        </div>
        <div>
          <p className="text-2xl font-semibold text-white">{data.num_provisions}</p>
          <p className="text-sm text-gray-400">Legal Provisions Found</p>
        </div>
      </div>

      {/* Provisions list */}
      {data.provisions_list && data.provisions_list.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-400 mb-3">Extracted Provisions:</h4>
          <div className="flex flex-wrap gap-2">
            {data.provisions_list.map((provision, index) => (
              <span key={index} className="badge badge-gold">
                {provision}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Explanations */}
      <div className="markdown-content">
        <ReactMarkdown>{data.explanation}</ReactMarkdown>
      </div>
    </div>
  )
}

function NewsTab({ data }) {
  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-4 border-b border-navy-700/50">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-800/30">
          <HiOutlineNewspaper className="w-6 h-6 text-primary-500" />
          <div>
            <p className="text-xl font-semibold text-white">{data.num_articles}</p>
            <p className="text-xs text-gray-400">Articles Found</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-800/30">
          <HiOutlineSearch className="w-6 h-6 text-primary-500" />
          <div>
            <p className="text-xl font-semibold text-white">{data.keywords?.length || 0}</p>
            <p className="text-xs text-gray-400">Keywords Used</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-800/30">
          <p className="text-sm text-gray-400">Search Period: <span className="text-white">7 days</span></p>
        </div>
      </div>

      {/* Keywords */}
      {data.keywords && data.keywords.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-400 mb-3">Search Keywords:</h4>
          <div className="flex flex-wrap gap-2">
            {data.keywords.map((keyword, index) => (
              <span key={index} className="badge badge-gold">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Analysis */}
      <div className="markdown-content">
        <ReactMarkdown>{data.analysis}</ReactMarkdown>
      </div>

      {/* Articles */}
      {data.articles && data.articles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-semibold text-white mb-4">News Articles</h4>
          <div className="space-y-4">
            {data.articles.map((article, index) => (
              <a
                key={index}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block card-hover p-4"
              >
                <h5 className="font-medium text-white hover:text-primary-400 transition-colors">
                  {article.title}
                </h5>
                <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                  <span>{article.publisher}</span>
                  <span>•</span>
                  <span>{article.published_date}</span>
                </div>
                <p className="text-sm text-gray-400 mt-2 line-clamp-2">
                  {article.description}
                </p>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function BenchTab({ data }) {
  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-4 border-b border-navy-700/50">
        <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-800/30">
          <HiOutlineUserGroup className="w-6 h-6 text-primary-500" />
          <div>
            <p className="text-xl font-semibold text-white">{data.num_judges}</p>
            <p className="text-xs text-gray-400">Judges Analyzed</p>
          </div>
        </div>
        {data.top_judges && data.top_judges.length > 0 && (
          <div className="flex items-center gap-3 p-3 rounded-lg bg-navy-800/30">
            <div>
              <p className="text-sm text-gray-400">Most Active Judge:</p>
              <p className="text-white font-medium">{data.top_judges[0]}</p>
            </div>
          </div>
        )}
      </div>

      {/* Analysis */}
      <div className="markdown-content">
        <ReactMarkdown>{data.analysis}</ReactMarkdown>
      </div>

      {/* Judge statistics */}
      {data.judges && Object.keys(data.judges).length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-semibold text-white mb-4">Judge Statistics</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(data.judges)
              .sort((a, b) => b[1].num_cases - a[1].num_cases)
              .map(([judgeName, info]) => (
                <div key={judgeName} className="card-hover p-4">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-white">Justice {judgeName}</p>
                    <span className="badge badge-gold">{info.num_cases} cases</span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage

