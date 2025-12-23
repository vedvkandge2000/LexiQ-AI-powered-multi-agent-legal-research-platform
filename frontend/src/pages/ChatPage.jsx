import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  HiOutlinePaperAirplane, 
  HiOutlineTrash,
  HiOutlineDownload,
  HiOutlinePlus,
  HiOutlineChat,
  HiOutlineClock,
  HiOutlineChevronRight
} from 'react-icons/hi'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import { chatAPI } from '../services/api'
import { useAuthStore } from '../store/authStore'

function ChatPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [suggestedQuestions, setSuggestedQuestions] = useState([])
  const [showSidebar, setShowSidebar] = useState(true)

  // Load user sessions
  useEffect(() => {
    loadUserSessions()
  }, [user])

  // Load session when sessionId changes
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory(sessionId)
    } else {
      setCurrentSession(null)
      setMessages([])
    }
  }, [sessionId])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadUserSessions = async () => {
    if (!user?.username) return
    
    try {
      const result = await chatAPI.getUserSessions(user.username)
      if (result.success) {
        setSessions(result.sessions || [])
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  const loadSessionHistory = async (sid) => {
    setIsLoading(true)
    try {
      const result = await chatAPI.getHistory(sid)
      if (result.success) {
        setMessages(result.messages || [])
        setCurrentSession(sid)
      }
    } catch (error) {
      toast.error('Failed to load chat history')
      navigate('/chat')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !currentSession || isSending) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    
    // Add user message to UI immediately
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }])
    
    setIsSending(true)
    
    try {
      const result = await chatAPI.sendMessage(currentSession, userMessage)
      
      if (result.success) {
        // Add assistant response
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: result.response,
          metadata: { citations: result.precedent_citations }
        }])
        
        // Update suggested questions
        if (result.suggested_questions) {
          setSuggestedQuestions(result.suggested_questions)
        }
      } else {
        toast.error(result.error || 'Failed to get response')
      }
    } catch (error) {
      toast.error('Failed to send message')
      // Remove the user message if failed
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setIsSending(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleDeleteSession = async (sid) => {
    if (!window.confirm('Are you sure you want to delete this chat?')) return
    
    try {
      await chatAPI.deleteChat(sid)
      toast.success('Chat deleted')
      
      if (sid === currentSession) {
        navigate('/chat')
      }
      
      loadUserSessions()
    } catch (error) {
      toast.error('Failed to delete chat')
    }
  }

  const handleExportChat = async () => {
    if (!currentSession) return
    
    try {
      const result = await chatAPI.exportChat(currentSession, 'markdown')
      
      if (result.success) {
        const blob = new Blob([result.content], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `chat_${currentSession}.md`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        toast.success('Chat exported!')
      }
    } catch (error) {
      toast.error('Failed to export chat')
    }
  }

  const handleSuggestedQuestion = (question) => {
    setInputMessage(question)
    inputRef.current?.focus()
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex">
      {/* Sessions sidebar */}
      <aside className={`
        ${showSidebar ? 'w-72' : 'w-0'} 
        transition-all duration-300 overflow-hidden
        border-r border-navy-700/50 flex-shrink-0
        hidden md:block
      `}>
        <div className="w-72 h-full flex flex-col">
          {/* New chat button */}
          <div className="p-4 border-b border-navy-700/50">
            <button
              onClick={() => navigate('/dashboard')}
              className="btn btn-primary w-full"
            >
              <HiOutlinePlus className="w-5 h-5" />
              <span>New Analysis</span>
            </button>
          </div>

          {/* Sessions list */}
          <div className="flex-1 overflow-y-auto p-2">
            <p className="px-3 py-2 text-xs font-medium text-gray-500 uppercase">
              Recent Chats
            </p>
            
            {sessions.length === 0 ? (
              <p className="px-3 py-4 text-sm text-gray-500 text-center">
                No chat sessions yet.<br />
                Start by analyzing a case.
              </p>
            ) : (
              <div className="space-y-1">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`
                      group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer
                      transition-all duration-200
                      ${session.session_id === currentSession
                        ? 'bg-primary-500/10 text-primary-400 border border-primary-500/30'
                        : 'text-gray-400 hover:bg-navy-800/50 hover:text-white border border-transparent'
                      }
                    `}
                    onClick={() => navigate(`/chat/${session.session_id}`)}
                  >
                    <HiOutlineChat className="w-4 h-4 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {session.case_title || 'Untitled Chat'}
                      </p>
                      <p className="text-xs text-gray-500 flex items-center gap-1">
                        <HiOutlineClock className="w-3 h-3" />
                        {new Date(session.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteSession(session.session_id)
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 transition-opacity"
                    >
                      <HiOutlineTrash className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {currentSession ? (
          <>
            {/* Chat header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-navy-700/50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                  <HiOutlineChat className="w-5 h-5 text-primary-500" />
                </div>
                <div>
                  <h2 className="font-semibold text-white">Case Discussion</h2>
                  <p className="text-xs text-gray-500">AI Legal Assistant</p>
                </div>
              </div>
              <button
                onClick={handleExportChat}
                className="btn btn-ghost text-sm"
              >
                <HiOutlineDownload className="w-5 h-5" />
                <span className="hidden sm:inline">Export</span>
              </button>
            </div>

            {/* Messages area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <svg className="animate-spin h-8 w-8 mx-auto text-primary-500 mb-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <p className="text-gray-400">Loading chat history...</p>
                  </div>
                </div>
              ) : (
                <>
                  <AnimatePresence>
                    {messages.map((msg, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`
                          max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3
                          ${msg.role === 'user'
                            ? 'bg-primary-500 text-navy-950 rounded-br-md'
                            : 'bg-navy-800 text-gray-100 rounded-bl-md'
                          }
                        `}>
                          {msg.role === 'assistant' ? (
                            <div className="markdown-content text-sm">
                              <ReactMarkdown>{msg.content}</ReactMarkdown>
                            </div>
                          ) : (
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                          )}
                          
                          {/* Citations */}
                          {msg.role === 'assistant' && msg.metadata?.citations && msg.metadata.citations.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-navy-600/50">
                              <p className="text-xs text-gray-400 mb-2">Referenced Precedents:</p>
                              <div className="flex flex-wrap gap-1">
                                {msg.metadata.citations.map((cite, i) => (
                                  <span key={i} className="text-xs bg-navy-700/50 px-2 py-0.5 rounded text-primary-400">
                                    {cite}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  {/* Typing indicator */}
                  {isSending && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex justify-start"
                    >
                      <div className="bg-navy-800 rounded-2xl rounded-bl-md px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce animation-delay-100" />
                          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce animation-delay-200" />
                        </div>
                      </div>
                    </motion.div>
                  )}

                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Suggested questions */}
            {suggestedQuestions.length > 0 && (
              <div className="px-4 py-2 border-t border-navy-700/50">
                <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      className="text-xs px-3 py-1.5 rounded-full bg-navy-800/50 text-gray-300 
                               hover:bg-navy-700 hover:text-white transition-colors
                               flex items-center gap-1"
                    >
                      {question}
                      <HiOutlineChevronRight className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input area */}
            <div className="p-4 border-t border-navy-700/50">
              <div className="flex items-end gap-3">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about the case..."
                    className="input pr-12 resize-none min-h-[50px] max-h-[150px]"
                    rows={1}
                    disabled={isSending}
                  />
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isSending}
                  className="btn btn-primary h-[50px] px-4"
                >
                  <HiOutlinePaperAirplane className="w-5 h-5 rotate-90" />
                </button>
              </div>
            </div>
          </>
        ) : (
          /* Empty state */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md mx-auto p-8">
              <div className="w-20 h-20 rounded-2xl bg-primary-500/10 flex items-center justify-center mx-auto mb-6">
                <HiOutlineChat className="w-10 h-10 text-primary-500" />
              </div>
              <h2 className="text-2xl font-display font-semibold text-white mb-3">
                Start a Conversation
              </h2>
              <p className="text-gray-400 mb-6">
                Select a chat from the sidebar or start a new case analysis to begin discussing legal matters with AI.
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn btn-primary"
              >
                <HiOutlinePlus className="w-5 h-5" />
                <span>New Case Analysis</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatPage

