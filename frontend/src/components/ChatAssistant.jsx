import React, { useState, useRef, useEffect } from 'react'
import { api } from '../utils/api'
import { Send, Bot, User, Loader2, AlertCircle, BarChart3 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function ChatAssistant({ sessionId }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m DataPilot AI assistant. Ask me anything about your dataset — trends, predictions, column details, or visualizations.' },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input.trim() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setSending(true)
    setError(null)

    try {
      const history = messages.slice(-10).map((m) => ({
        role: m.role,
        parts: [{ text: m.content }],
      }))

      const response = await api.askQuestion(sessionId, userMessage.content, history)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.reply, viz: response.viz_suggestion },
      ])
    } catch (err) {
      setError(err.message)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Sorry, I encountered an error: ${err.message}` },
      ])
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const suggestions = [
    'How many rows are in this dataset?',
    'What are the column names?',
    'Are there any missing values?',
    'Show me the top trends',
    'Which columns are most important?',
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-220px)]">
      <div>
        <h2 className="text-xl font-bold text-white">AI Data Chat Assistant</h2>
        <p className="text-sm text-gray-400 mt-1">Ask natural language questions about your data</p>
      </div>

      <div className="flex-1 card mt-4 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 px-2">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'
              }`}>
                {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-blue-400" />}
              </div>
              <div className={`max-w-[80%] rounded-xl px-4 py-3 ${
                msg.role === 'user' ? 'bg-blue-600/20 border border-blue-800' : 'bg-gray-800/50 border border-gray-700'
              }`}>
                <div className="prose prose-invert prose-sm max-w-none text-gray-200">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
                {msg.viz && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-blue-400">
                    <BarChart3 size={14} />
                    <span>Visualization suggested: {msg.viz}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                <Bot size={16} className="text-blue-400" />
              </div>
              <div className="bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3">
                <Loader2 size={16} className="text-blue-400 animate-spin" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="px-2 py-2 flex items-center gap-2 text-sm text-red-400">
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}

        {messages.length === 1 && (
          <div className="px-2 py-3">
            <p className="text-xs text-gray-500 mb-2">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => { setInput(s); setTimeout(() => document.getElementById('chat-input')?.focus(), 100) }}
                  className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 px-3 py-1.5 rounded-full transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-gray-800 pt-4 mt-4 flex gap-3">
          <input
            id="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your data..."
            className="input-field flex-1"
            disabled={sending}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="btn-primary flex items-center gap-2"
          >
            <Send size={16} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
      </div>
    </div>
  )
}
