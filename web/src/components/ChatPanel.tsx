/**
 * Center pane — conversational chat window per CEO archetype.
 * Handles direct responses and Executize job dispatch.
 * Typewriter effect simulates streaming on long responses.
 *
 * Reference: hacky-hours/02-design/USER_JOURNEYS.md § Ask the CEO a Question
 */

import { useEffect, useRef, useState } from 'react'
import type { ConfigResponse, Job, SessionResponse } from '../types/api'
import type { CeoState, ChatMessage } from '../App'
import { sendMessage, subscribeToJob, getJob } from '../lib/api'

interface Props {
  ceo: CeoState
  config: ConfigResponse
  onMessage: (msg: ChatMessage) => void
  onJobChange: (job: Job | null) => void
}

const ARCHETYPE_COLORS: Record<string, string> = {
  operator:  '#FF2D78',
  visionary: '#3D00CC',
  advocate:  '#7FFF00',
  analyst:   '#00F5FF',
}

function formatResponse(r: SessionResponse): string {
  const parts = [
    `**Position:** ${r.position}`,
    '',
    `**Reasoning:** ${r.reasoning}`,
    '',
    `**Pros:**\n${r.pros.map((p) => `  • ${p}`).join('\n')}`,
    `**Cons:**\n${r.cons.map((c) => `  • ${c}`).join('\n')}`,
  ]
  if (r.flags.length > 0) {
    parts.push('', `**Flags:**\n${r.flags.map((f) => `  ⚠ ${f}`).join('\n')}`)
  }
  if (r.questions_for_user.length > 0) {
    parts.push('', `**Questions for you:**\n${r.questions_for_user.map((q) => `  ? ${q}`).join('\n')}`)
  }
  return parts.join('\n')
}

function MessageBubble({ msg, accentColor }: { msg: ChatMessage; accentColor: string }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={[
          'max-w-[80%] rounded px-4 py-3 font-mono text-sm whitespace-pre-wrap leading-relaxed',
          isUser
            ? 'bg-[#1A1A2E] text-[#F0F0FF] border border-[#2A2A44]'
            : 'bg-[#12121A] text-[#F0F0FF] border',
        ].join(' ')}
        style={!isUser ? { borderColor: `${accentColor}66` } : undefined}
        role="article"
        aria-label={isUser ? 'Your message' : 'CEO response'}
      >
        {msg.content}
        {msg.response && (
          <div className="mt-2 pt-2 border-t border-[#2A2A44] text-[10px] text-[#8888AA]">
            {msg.response.model} · {msg.response.input_tokens + msg.response.output_tokens} tokens
          </div>
        )}
      </div>
    </div>
  )
}

export function ChatPanel({ ceo, config, onMessage, onJobChange }: Props) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const accentColor = ARCHETYPE_COLORS[ceo.slug] ?? '#00F5FF'

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [ceo.history])

  // Subscribe to active job via SSE
  useEffect(() => {
    const job = ceo.activeJob
    if (!job || job.status === 'complete' || job.status === 'failed') return

    const unsub = subscribeToJob(
      job.id,
      (updatedJob) => {
        onJobChange(updatedJob)
        if (updatedJob.status === 'complete' && updatedJob.result) {
          try {
            const parsed = JSON.parse(updatedJob.result) as SessionResponse
            const content = formatResponse(parsed)
            onMessage({
              role: 'assistant',
              content,
              response: parsed,
              timestamp: new Date().toISOString(),
            })
          } catch {
            onMessage({
              role: 'assistant',
              content: updatedJob.result,
              timestamp: new Date().toISOString(),
            })
          }
          setToast(`${config.archetypes.find(a => a.slug === ceo.slug)?.name ?? 'CEO'} finished.`)
          setTimeout(() => setToast(null), 4000)
          onJobChange(null)
        } else if (updatedJob.status === 'failed') {
          setError(updatedJob.error ?? 'Job failed.')
          onJobChange(null)
        }
      },
      (errMsg) => {
        setError(errMsg)
        onJobChange(null)
      },
    )

    return unsub
  }, [ceo.activeJob?.id])

  const isExecutizing = ceo.activeJob != null && ceo.activeJob.status === 'running'

  async function handleSend(executize: boolean) {
    const msg = input.trim()
    if (!msg || sending) return

    setInput('')
    setError(null)
    setSending(true)

    onMessage({
      role: 'user',
      content: msg,
      timestamp: new Date().toISOString(),
    })

    try {
      const result = await sendMessage({
        message: msg,
        archetype_slug: ceo.slug,
        executize,
      })

      if (executize && result.job_id) {
        // Job dispatched — fetch initial state and set it
        const job = await getJob(result.job_id)
        onJobChange(job)
        onMessage({
          role: 'assistant',
          content: `On it. I'll work on this in the background (job ${result.job_id.slice(0, 8)}…). You can keep chatting or switch to another CEO.`,
          timestamp: new Date().toISOString(),
        })
      } else if (!executize) {
        const content = formatResponse(result)
        onMessage({
          role: 'assistant',
          content,
          response: result,
          timestamp: new Date().toISOString(),
        })
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSend(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#0D0D15] border-x border-[#2A2A44]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4" role="log" aria-label="Conversation" aria-live="polite">
        {ceo.history.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-[#8888AA] font-mono text-sm text-center max-w-sm">
              Ask your CEO a question, or hit{' '}
              <span style={{ color: accentColor }}>Executize</span> for deep work
              that runs in the background.
            </p>
          </div>
        )}
        {ceo.history.map((msg, i) => (
          <MessageBubble key={i} msg={msg} accentColor={accentColor} />
        ))}
        {(sending || isExecutizing) && (
          <div className="flex justify-start mb-4">
            <div
              className="px-4 py-3 rounded border font-mono text-sm"
              style={{ borderColor: `${accentColor}44`, color: accentColor }}
              aria-live="polite"
              aria-label="CEO is thinking"
            >
              <span className="animate-pulse">
                {isExecutizing ? 'Executizing...' : 'Thinking...'}
              </span>
            </div>
          </div>
        )}
        {error && (
          <div
            className="px-4 py-2 rounded border border-[#FF2D78] bg-[#FF2D7822] text-[#FF2D78] font-mono text-sm mb-4"
            role="alert"
          >
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Toast notification */}
      {toast && (
        <div
          className="mx-4 mb-2 px-4 py-2 rounded border font-mono text-sm animate-pulse"
          style={{ borderColor: accentColor, color: accentColor }}
          role="status"
          aria-live="polite"
        >
          ✓ {toast}
        </div>
      )}

      {/* Input area */}
      <div className="border-t border-[#2A2A44] p-4 bg-[#12121A]">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask ${config.archetypes.find(a => a.slug === ceo.slug)?.name ?? 'the CEO'} a question... (Enter to send, Shift+Enter for newline)`}
          disabled={sending || isExecutizing}
          rows={3}
          aria-label="Message input"
          className={[
            'w-full bg-[#0A0A0F] border rounded px-3 py-2 font-mono text-sm text-[#F0F0FF]',
            'placeholder:text-[#8888AA] resize-none focus:outline-none transition-colors',
            sending || isExecutizing ? 'opacity-50 cursor-not-allowed' : 'hover:border-[#00F5FF] focus:border-[#00F5FF]',
          ].join(' ')}
          style={{ borderColor: '#2A2A44' }}
        />
        <div className="flex gap-2 mt-2 justify-end">
          <button
            onClick={() => void handleSend(false)}
            disabled={!input.trim() || sending || isExecutizing}
            className={[
              'px-4 py-2 font-mono text-sm rounded border transition-all',
              !input.trim() || sending || isExecutizing
                ? 'opacity-30 cursor-not-allowed text-[#8888AA] border-[#2A2A44]'
                : 'text-[#F0F0FF] border-[#2A2A44] hover:border-[#00F5FF] hover:text-[#00F5FF]',
            ].join(' ')}
          >
            Ask
          </button>
          <button
            onClick={() => void handleSend(true)}
            disabled={!input.trim() || sending || isExecutizing}
            title="Executize: dispatch as a background deep-work job"
            className={[
              'px-4 py-2 font-mono text-sm rounded border transition-all',
              !input.trim() || sending || isExecutizing
                ? 'opacity-30 cursor-not-allowed border-[#2A2A44] text-[#8888AA]'
                : 'font-bold hover:shadow-lg',
            ].join(' ')}
            style={
              !input.trim() || sending || isExecutizing
                ? undefined
                : {
                    borderColor: accentColor,
                    color: accentColor,
                    boxShadow: `0 0 8px ${accentColor}44`,
                  }
            }
          >
            Executize ⚡
          </button>
        </div>
      </div>
    </div>
  )
}
