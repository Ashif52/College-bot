import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bot,
  CheckCircle2,
  Loader2,
  LogOut,
  MessageSquare,
  Send,
  Sparkles,
  User,
  X,
} from 'lucide-react'

import {
  endChatbotSession,
  sendChatbotMessage,
  startChatbotSession,
} from '../../api/chatbot'

const Motion = motion

const SESSION_STEP_MAP = {
  AWAIT_FIRST_MSG: 1,
  COLLECT_NAME: 2,
  COLLECT_PHONE: 3,
  ANSWERING: 4,
  ENDED: 4,
}

const SESSION_STEPS = ['Chat', 'Name', 'Phone', 'Answers']

const generateId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`

function renderFormattedText(text) {
  const lines = String(text || '').split('\n')

  return lines.map((line, lineIndex) => {
    const parts = line.split(/(\*\*.*?\*\*)/g)

    return (
      <Fragment key={`${line}-${lineIndex}`}>
        {parts.map((part, partIndex) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={`${part}-${partIndex}`}>{part.slice(2, -2)}</strong>
          }

          return <Fragment key={`${part}-${partIndex}`}>{part}</Fragment>
        })}
        {lineIndex < lines.length - 1 ? <br /> : null}
      </Fragment>
    )
  })
}

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sessionState, setSessionState] = useState('IDLE')
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionEnded, setSessionEnded] = useState(false)
  const [followupQuestions, setFollowupQuestions] = useState([])
  const [saveSummary, setSaveSummary] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const scrollRef = useRef(null)

  const activeStep = SESSION_STEP_MAP[sessionState] || 1
  const canEndSession = sessionState === 'ANSWERING' && !sessionEnded && Boolean(sessionId)

  const statusLabel = useMemo(() => {
    if (sessionEnded) {
      return 'Session Saved'
    }
    if (isLoading && !sessionId) {
      return 'Connecting...'
    }
    if (isLoading) {
      return 'Thinking...'
    }
    if (sessionId) {
      return 'Live Session'
    }
    if (errorMessage) {
      return 'Offline'
    }
    return 'Ready'
  }, [errorMessage, isLoading, sessionEnded, sessionId])

  async function startSession() {
    try {
      setIsLoading(true)
      setErrorMessage('')
      const data = await startChatbotSession()
      setSessionId(data.session_id)
      setSessionState(data.state)
      setMessages([{ id: generateId(), text: data.greeting, sender: 'bot' }])
      setSessionEnded(false)
      setFollowupQuestions([])
      setSaveSummary(null)
    } catch (error) {
      setErrorMessage(error.message || 'Could not connect to the admissions assistant.')
      setMessages([
        {
          id: generateId(),
          text:
            "I'm having trouble connecting right now. Please make sure the chatbot API is running, then start a new inquiry.",
          sender: 'bot',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  function resetChatState() {
    setSessionId(null)
    setSessionState('IDLE')
    setMessages([])
    setInputValue('')
    setIsLoading(false)
    setSessionEnded(false)
    setFollowupQuestions([])
    setSaveSummary(null)
    setErrorMessage('')
  }

  function startNewInquiry() {
    resetChatState()
  }

  useEffect(() => {
    if (isOpen && !sessionId && messages.length === 0 && !isLoading && !sessionEnded) {
      void startSession()
    }
  }, [isLoading, isOpen, messages.length, sessionEnded, sessionId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [followupQuestions, isLoading, isOpen, messages, saveSummary])

  async function handleSendMessage(event) {
    event.preventDefault()

    if (!inputValue.trim() || !sessionId || isLoading || sessionEnded) {
      return
    }

    const userMessageText = inputValue.trim()
    const userMsg = { id: generateId(), text: userMessageText, sender: 'user' }

    setMessages((previous) => [...previous, userMsg])
    setInputValue('')
    setIsLoading(true)
    setErrorMessage('')

    try {
      const data = await sendChatbotMessage(sessionId, userMessageText)

      setSessionState(data.state)
      setMessages((previous) => [
        ...previous,
        { id: generateId(), text: data.reply, sender: 'bot' },
      ])

      if (data.session_ended) {
        setSessionEnded(true)
      }
    } catch (error) {
      setErrorMessage(error.message || 'Could not send your message.')
      setMessages((previous) => [
        ...previous,
        {
          id: generateId(),
          text: 'I lost my connection for a moment. Please try sending that again.',
          sender: 'bot',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  async function handleEndSession() {
    if (!sessionId || sessionEnded || isLoading) {
      return
    }

    setIsLoading(true)
    setErrorMessage('')

    try {
      const data = await endChatbotSession(sessionId)
      const savedMessage = data.excel_saved
        ? `Your enquiry has been saved for ${data.student_name || 'you'}.`
        : 'Your conversation ended, but saving the enquiry data needs attention.'

      setSessionState('ENDED')
      setSessionEnded(true)
      setFollowupQuestions(data.followup_questions || [])
      setSaveSummary(savedMessage)
      setMessages((previous) => [
        ...previous,
        {
          id: generateId(),
          text:
            'Session saved. Our admissions team will follow up soon. You can start a new inquiry anytime.',
          sender: 'bot',
        },
      ])
    } catch (error) {
      setErrorMessage(error.message || 'Could not save your session.')
      setMessages((previous) => [
        ...previous,
        {
          id: generateId(),
          text: 'I could not save the session just now. Please try the save button once more.',
          sender: 'bot',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-[100]">
      <Motion.button
        whileHover={{ scale: 1.08, rotate: 4 }}
        whileTap={{ scale: 0.92 }}
        onClick={() => setIsOpen((previous) => !previous)}
        className={`relative flex h-14 w-14 items-center justify-center overflow-hidden rounded-3xl text-white shadow-2xl transition-all duration-500 sm:h-16 sm:w-16 ${
          isOpen ? 'border border-white/10 bg-navy-900' : 'bg-primary-600'
        }`}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <Motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
            >
              <X className="h-6 w-6" />
            </Motion.div>
          ) : (
            <Motion.div
              key="chat"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
            >
              <MessageSquare className="h-6 w-6" />
            </Motion.div>
          )}
        </AnimatePresence>
        {!isOpen && <div className="absolute right-0 top-0 h-4 w-4 animate-pulse rounded-full border-4 border-navy-950 bg-green-400" />}
      </Motion.button>

      <AnimatePresence>
        {isOpen && (
          <Motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9, transformOrigin: 'bottom right' }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="absolute bottom-20 right-0 flex h-[560px] w-[340px] flex-col overflow-hidden rounded-[2rem] border border-white/10 bg-navy-950/95 shadow-2xl shadow-black/40 backdrop-blur-xl sm:w-[390px]"
          >
            <div className="shrink-0 bg-gradient-to-r from-primary-600/90 to-primary-800/90 p-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-accent-400 ring-1 ring-white/20">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold tracking-wide text-white">Nexus AI Assistant</h3>
                    <div className="mt-0.5 flex items-center gap-1.5">
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${
                          errorMessage ? 'bg-red-400' : sessionEnded ? 'bg-emerald-300' : sessionId ? 'bg-green-400' : 'bg-yellow-400'
                        } ${isLoading ? 'animate-pulse' : ''}`}
                      />
                      <span className="text-[10px] font-bold uppercase tracking-widest text-white/70">
                        {statusLabel}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    resetChatState()
                    setIsOpen(false)
                  }}
                  className="rounded-xl p-2 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                  title="Close and reset"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>

              <div className="mt-4 flex items-center gap-2 overflow-hidden">
                {SESSION_STEPS.map((label, index) => {
                  const stepNumber = index + 1
                  const isDone = stepNumber < activeStep
                  const isActive = stepNumber === activeStep

                  return (
                    <Fragment key={label}>
                      <div className={`flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${isDone ? 'text-emerald-200' : isActive ? 'text-white' : 'text-white/40'}`}>
                        <span
                          className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] ${
                            isDone
                              ? 'bg-emerald-400 text-navy-950'
                              : isActive
                                ? 'bg-white text-primary-700'
                                : 'bg-white/10 text-white/60'
                          }`}
                        >
                          {isDone ? <CheckCircle2 className="h-3.5 w-3.5" /> : stepNumber}
                        </span>
                        <span>{label}</span>
                      </div>
                      {stepNumber < SESSION_STEPS.length ? (
                        <div className="h-px flex-1 bg-white/10" />
                      ) : null}
                    </Fragment>
                  )
                })}
              </div>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto overflow-x-hidden bg-navy-950/40 p-4">
              <div className="space-y-3">
                {messages.map((message) => (
                  <Motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    className={`flex w-full items-end gap-2 ${
                      message.sender === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.sender === 'bot' ? (
                      <div className="mb-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary-600/20">
                        <Bot className="h-3.5 w-3.5 text-primary-400" />
                      </div>
                    ) : null}

                    <div
                      className={`max-w-[78%] break-words rounded-2xl px-4 py-2.5 text-[13px] leading-relaxed shadow-sm ${
                        message.sender === 'user'
                          ? 'rounded-br-none bg-primary-600 text-white'
                          : 'glass rounded-bl-none border border-white/5 text-white/95'
                      }`}
                      style={{ overflowWrap: 'anywhere', wordBreak: 'break-word' }}
                    >
                      {renderFormattedText(message.text)}
                    </div>

                    {message.sender === 'user' ? (
                      <div className="mb-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/5">
                        <User className="h-3.5 w-3.5 text-white/40" />
                      </div>
                    ) : null}
                  </Motion.div>
                ))}

                {isLoading ? (
                  <Motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2"
                  >
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-600/20">
                      <Bot className="h-4 w-4 text-primary-400" />
                    </div>
                    <div className="glass flex items-center gap-2 rounded-2xl border border-white/5 px-5 py-3 text-white/40">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-xs italic">Thinking...</span>
                    </div>
                  </Motion.div>
                ) : null}
              </div>
            </div>

            {canEndSession ? (
              <div className="shrink-0 border-t border-amber-300/20 bg-amber-200/10 px-4 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs leading-relaxed text-amber-100/90">
                    Done exploring? Save this enquiry so the admissions team can follow up.
                  </p>
                  <button
                    onClick={handleEndSession}
                    disabled={isLoading}
                    className="shrink-0 rounded-xl bg-amber-300 px-3 py-2 text-[11px] font-bold uppercase tracking-[0.14em] text-navy-950 transition hover:bg-amber-200 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    End & Save
                  </button>
                </div>
              </div>
            ) : null}

            {sessionEnded ? (
              <div className="shrink-0 border-t border-emerald-400/20 bg-emerald-500/10 px-4 py-3">
                <p className="text-sm font-semibold text-emerald-200">Enquiry completed</p>
                <p className="mt-1 text-xs leading-relaxed text-emerald-100/80">
                  {saveSummary || 'The session is closed and ready for follow-up.'}
                </p>

                {followupQuestions.length > 0 ? (
                  <div className="mt-3 space-y-2 rounded-2xl border border-white/10 bg-white/5 p-3">
                    <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-white/45">
                      Follow-Up Topics
                    </p>
                    {followupQuestions.map((question, index) => (
                      <div key={`${question}-${index}`} className="flex gap-2 text-xs leading-relaxed text-white/85">
                        <span className="font-bold text-accent-400">Q{index + 1}.</span>
                        <span>{question}</span>
                      </div>
                    ))}
                  </div>
                ) : null}

                <button
                  onClick={startNewInquiry}
                  className="mt-4 w-full rounded-2xl border border-emerald-300/30 bg-emerald-400/15 px-4 py-3 text-xs font-bold uppercase tracking-[0.16em] text-emerald-100 transition hover:bg-emerald-400/25"
                >
                  Start New Inquiry
                </button>
              </div>
            ) : null}

            {!sessionEnded ? (
              <div className="shrink-0 border-t border-white/10 bg-navy-950/60 p-4 backdrop-blur-xl">
                <form onSubmit={handleSendMessage} className="flex items-center gap-3">
                  <input
                    disabled={isLoading || !sessionId}
                    type="text"
                    placeholder="Ask about admissions..."
                    value={inputValue}
                    onChange={(event) => setInputValue(event.target.value)}
                    className="glass w-full min-w-0 rounded-2xl border border-white/5 px-4 py-3 text-sm text-white placeholder:text-white/30 transition-all focus:outline-none focus:ring-2 focus:ring-primary-600/50"
                  />
                  <Motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    type="submit"
                    disabled={!inputValue.trim() || isLoading || !sessionId}
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-600 text-white shadow-xl shadow-primary-600/30 transition-all disabled:opacity-50"
                  >
                    <Send className="h-5 w-5" />
                  </Motion.button>
                </form>

                <div className="mt-2 text-center">
                  <span className={`text-[10px] font-semibold tracking-[0.18em] ${errorMessage ? 'text-red-300/80' : 'text-white/35'}`}>
                    {errorMessage || 'NEXUS AI'}
                  </span>
                </div>
              </div>
            ) : null}
          </Motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
