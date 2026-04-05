/**
 * Center pane — tabbed: Chat conversation + open artifact viewers.
 * The input bar is always visible regardless of which tab is active,
 * so the user can continue chatting while reading an artifact.
 *
 * Reference: hacky-hours/02-design/USER_JOURNEYS.md § Ask the CEO a Question
 */

import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ArtifactMeta, ConfigResponse, Job, SessionResponse } from '../types/api'
import type { CeoState, ChatMessage } from '../App'
import { getArtifact, sendMessage, subscribeToJob, getJob } from '../lib/api'
import { DecisionBar } from './DecisionBar'

interface Props {
  ceo: CeoState
  config: ConfigResponse
  onMessage: (msg: ChatMessage) => void
  onJobChange: (job: Job | null) => void
  onArtifactCreated?: () => void
  onAnnounce: (prefillMessage: string, archetype_slug: string) => void
  onSendingChange: (sending: boolean) => void
  onDecision: (msgIndex: number, decision: 'adopted' | 'rejected' | 'modified', modification?: string) => void
  // Artifact tabs
  openArtifacts: ArtifactMeta[]
  activeArtifactId: string | null   // null = Chat tab active
  onSetActiveArtifact: (id: string | null) => void
  onCloseArtifact: (id: string) => void
  onExpandArtifact: (artifact: ArtifactMeta) => void
}

export const ARCHETYPE_COLORS: Record<string, string> = {
  operator:  '#FF2D78',
  visionary: '#8B5CF6',
  advocate:  '#7FFF00',
  analyst:   '#00F5FF',
}

export function formatResponse(r: SessionResponse): string {
  const parts = [r.position]
  if (r.reasoning) parts.push('', `— reasoning —`, r.reasoning)
  if (r.pros.length > 0 || r.cons.length > 0) {
    parts.push('')
    if (r.pros.length > 0) parts.push(`Pros:\n${r.pros.map((p) => `  + ${p}`).join('\n')}`)
    if (r.cons.length > 0) parts.push(`Cons:\n${r.cons.map((c) => `  – ${c}`).join('\n')}`)
  }
  if (r.flags.length > 0) parts.push('', `Flags:\n${r.flags.map((f) => `  ⚠ ${f}`).join('\n')}`)
  if (r.questions_for_user.length > 0) parts.push('', `Questions:\n${r.questions_for_user.map((q) => `  ? ${q}`).join('\n')}`)
  return parts.join('\n')
}

function MessageBubble({ msg, accentColor }: { msg: ChatMessage; accentColor: string }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={[
          'max-w-[85%] rounded px-4 py-3 font-mono text-sm leading-relaxed',
          isUser
            ? 'bg-[#1A1A2E] text-[#F0F0FF] border border-[#2A2A44] whitespace-pre-wrap'
            : 'bg-[#12121A] text-[#F0F0FF] border',
        ].join(' ')}
        style={!isUser ? { borderColor: `${accentColor}66` } : undefined}
        role="article"
        aria-label={isUser ? 'Your message' : 'CEO response'}
      >
        {isUser ? (
          msg.content
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Style markdown elements to match the dark theme
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              strong: ({ children }) => <strong className="font-bold text-[#F0F0FF]">{children}</strong>,
              em: ({ children }) => <em className="italic text-[#D0D0EE]">{children}</em>,
              h1: ({ children }) => <h1 className="text-lg font-bold mb-2 mt-1" style={{ color: accentColor }}>{children}</h1>,
              h2: ({ children }) => <h2 className="text-base font-bold mb-1.5 mt-1" style={{ color: accentColor }}>{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-bold mb-1 mt-1 text-[#F0F0FF]">{children}</h3>,
              ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-0.5">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-0.5">{children}</ol>,
              li: ({ children }) => <li className="text-[#F0F0FF]">{children}</li>,
              code: ({ children, className }) => {
                const isBlock = className?.includes('language-')
                return isBlock
                  ? <code className="block bg-[#0A0A0F] border border-[#2A2A44] rounded px-3 py-2 text-xs my-2 overflow-x-auto whitespace-pre">{children}</code>
                  : <code className="bg-[#1A1A2E] border border-[#2A2A44] rounded px-1 text-xs" style={{ color: accentColor }}>{children}</code>
              },
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 pl-3 my-2 italic text-[#D0D0EE]" style={{ borderColor: accentColor }}>
                  {children}
                </blockquote>
              ),
              hr: () => <hr className="border-[#2A2A44] my-3" />,
              table: ({ children }) => <table className="border-collapse text-xs my-2 w-full">{children}</table>,
              th: ({ children }) => <th className="border border-[#2A2A44] px-2 py-1 text-left text-[#8888AA] font-bold">{children}</th>,
              td: ({ children }) => <td className="border border-[#2A2A44] px-2 py-1">{children}</td>,
            }}
          >
            {msg.content}
          </ReactMarkdown>
        )}
        {msg.response && (
          <div className="mt-2 pt-2 border-t border-[#2A2A44] text-[10px] text-[#8888AA]">
            {msg.response.model} · {msg.response.input_tokens + msg.response.output_tokens} tokens
          </div>
        )}
      </div>
    </div>
  )
}

function ArtifactTabContent({
  artifact,
  onExpand,
}: {
  artifact: ArtifactMeta
  onExpand: () => void
}) {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getArtifact(artifact.session_id, artifact.filename)
      .then((r) => setContent(r.content))
      .catch(() => setContent('Failed to load artifact.'))
      .finally(() => setLoading(false))
  }, [artifact.id])

  return (
    <div className="flex flex-col flex-1 overflow-hidden p-4">
      <div className="flex items-center justify-between mb-3 flex-shrink-0">
        <h2 className="font-mono text-xs text-[#00F5FF] tracking-widest uppercase truncate flex-1 mr-4">
          {artifact.filename}
        </h2>
        <button
          onClick={onExpand}
          className="font-mono text-xs text-[#8888AA] hover:text-[#F0F0FF] transition-colors px-2 py-1 border border-[#2A2A44] rounded hover:border-[#00F5FF]"
          title="Expand to fullscreen"
        >
          ⊞ Expand
        </button>
      </div>
      {loading ? (
        <p className="text-[#8888AA] font-mono text-xs animate-pulse">Loading…</p>
      ) : (
        <pre className="flex-1 overflow-auto font-mono text-sm text-[#F0F0FF] whitespace-pre-wrap leading-relaxed">
          {content}
        </pre>
      )}
    </div>
  )
}

export function ChatPanel({
  ceo,
  config,
  onMessage,
  onJobChange,
  onArtifactCreated,
  onAnnounce,
  onSendingChange,
  onDecision,
  openArtifacts,
  activeArtifactId,
  onSetActiveArtifact,
  onCloseArtifact,
  onExpandArtifact,
}: Props) {
  const [input, setInput] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const accentColor = ARCHETYPE_COLORS[ceo.slug] ?? '#00F5FF'
  const sending = ceo.sending

  const activeTab = activeArtifactId ?? 'chat'
  const activeArtifact = openArtifacts.find((a) => a.id === activeArtifactId) ?? null

  // Scroll to bottom on new messages (only when on chat tab)
  useEffect(() => {
    if (activeTab === 'chat') {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [ceo.history, activeTab])

  // Subscribe to active job via SSE.
  // Polls getJob() first so tab-switching doesn't leave a stale "Executizing" state.
  useEffect(() => {
    const job = ceo.activeJob
    if (!job || job.status === 'complete' || job.status === 'failed') return

    let cancelled = false
    let sseUnsub: (() => void) | null = null

    function handleJobUpdate(updatedJob: Job) {
      onJobChange(updatedJob)
      if (updatedJob.status === 'complete' && updatedJob.result) {
        try {
          const parsed = JSON.parse(updatedJob.result) as SessionResponse
          onMessage({ role: 'assistant', content: formatResponse(parsed), response: parsed, timestamp: new Date().toISOString() })
        } catch {
          onMessage({ role: 'assistant', content: updatedJob.result, timestamp: new Date().toISOString() })
        }
        setToast(`${config.archetypes.find((a) => a.slug === ceo.slug)?.name ?? 'CEO'} finished.`)
        setTimeout(() => setToast(null), 4000)
        onJobChange(null)
      } else if (updatedJob.status === 'failed') {
        setError(updatedJob.error ?? 'Job failed.')
        onJobChange(null)
      }
    }

    getJob(job.id).then((updatedJob) => {
      if (cancelled) return
      if (updatedJob.status === 'complete' || updatedJob.status === 'failed') {
        handleJobUpdate(updatedJob)
        return
      }
      sseUnsub = subscribeToJob(
        job.id,
        (sseJob) => { if (!cancelled) handleJobUpdate(sseJob) },
        (errMsg) => { if (!cancelled) { setError(errMsg); onJobChange(null) } },
      )
    }).catch(() => {})

    return () => { cancelled = true; sseUnsub?.() }
  }, [ceo.activeJob?.id])

  const isExecutizing = ceo.activeJob != null && ceo.activeJob.status === 'running'

  async function handleSend(executize: boolean) {
    const msg = input.trim()
    if (!msg || sending) return

    setInput('')
    setError(null)
    onSendingChange(true)

    // Switch to chat tab so user sees the response arrive
    onSetActiveArtifact(null)

    onMessage({ role: 'user', content: msg, timestamp: new Date().toISOString() })

    try {
      const result = await sendMessage({ message: msg, archetype_slug: ceo.slug, executize })

      if (executize && result.job_id) {
        const job = await getJob(result.job_id)
        onJobChange(job)
        onMessage({
          role: 'assistant',
          content: `On it. I'll work on this in the background (job ${result.job_id.slice(0, 8)}…). You can keep chatting or switch to another CEO.`,
          timestamp: new Date().toISOString(),
        })
      } else if (!executize) {
        onMessage({ role: 'assistant', content: formatResponse(result), response: result, timestamp: new Date().toISOString() })
        if (result.artifact) onArtifactCreated?.()
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      onSendingChange(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSend(false)
    }
  }

  const ceoName = config.archetypes.find((a) => a.slug === ceo.slug)?.name ?? 'the CEO'

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-[#0D0D15] border-x border-[#2A2A44]">

      {/* Tab bar — always visible so there's no layout shift when artifacts are added */}
      <div
        className="flex items-stretch border-b border-[#2A2A44] bg-[#0A0A0F] overflow-x-auto flex-shrink-0"
        role="tablist"
        aria-label="Content tabs"
      >
        {/* Chat tab */}
        <button
          role="tab"
          aria-selected={activeTab === 'chat'}
          onClick={() => onSetActiveArtifact(null)}
          className={[
            'px-4 py-2 font-mono text-xs tracking-widest uppercase transition-colors whitespace-nowrap border-b-2',
            activeTab === 'chat'
              ? 'text-[#F0F0FF] border-b-2'
              : 'text-[#8888AA] hover:text-[#F0F0FF] border-transparent',
          ].join(' ')}
          style={activeTab === 'chat' ? { borderColor: accentColor } : undefined}
        >
          1-on-1
        </button>

        {/* Artifact tabs — only rendered when artifacts are open */}
        {openArtifacts.map((artifact) => (
          <div
            key={artifact.id}
            className={[
              'flex items-center border-b-2 transition-colors',
              activeTab === artifact.id ? 'border-[#00F5FF]' : 'border-transparent',
            ].join(' ')}
          >
            <button
              role="tab"
              aria-selected={activeTab === artifact.id}
              onClick={() => onSetActiveArtifact(artifact.id)}
              className={[
                'px-3 py-2 font-mono text-xs transition-colors whitespace-nowrap',
                activeTab === artifact.id ? 'text-[#00F5FF]' : 'text-[#8888AA] hover:text-[#F0F0FF]',
              ].join(' ')}
            >
              {artifact.filename}
            </button>
            <button
              onClick={() => onCloseArtifact(artifact.id)}
              className="pr-2 pl-0 py-2 text-[#8888AA] hover:text-[#FF2D78] font-mono text-xs transition-colors"
              aria-label={`Close ${artifact.filename}`}
              title="Close tab"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Content area — switches between chat and artifact */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {activeTab === 'chat' ? (
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
            {ceo.history.map((msg, i) => {
              // Find the most recent user message before this assistant message
              let question = ''
              for (let j = i - 1; j >= 0; j--) {
                if (ceo.history[j].role === 'user') { question = ceo.history[j].content; break }
              }
              return (
                <div key={i} className="mb-2">
                  <MessageBubble msg={msg} accentColor={accentColor} />
                  {msg.response && (
                    <DecisionBar
                      response={msg.response}
                      activeCeoSlug={ceo.slug}
                      question={question}
                      isModifiedResponse={msg.isModifiedResponse}
                      slackConfigured={config.slack_configured}
                      onAnnounce={onAnnounce}
                      onMessage={(newMsg) => onMessage(newMsg)}
                      onDecision={(decision, modification) => onDecision(i, decision, modification)}
                    />
                  )}
                </div>
              )
            })}
            {(sending || isExecutizing) && (
              <div className="flex justify-start mb-4">
                <div
                  className="px-4 py-3 rounded border font-mono text-sm"
                  style={{ borderColor: `${accentColor}44`, color: accentColor }}
                  aria-live="polite"
                  aria-label="CEO is thinking"
                >
                  <span className="animate-pulse">
                    {isExecutizing ? 'Executizing…' : 'Thinking…'}
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
        ) : activeArtifact ? (
          <ArtifactTabContent
            artifact={activeArtifact}
            onExpand={() => onExpandArtifact(activeArtifact)}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-[#8888AA] font-mono text-xs">Artifact not found.</p>
          </div>
        )}
      </div>

      {/* Toast — always above input */}
      {toast && (
        <div
          className="mx-4 mb-2 px-4 py-2 rounded border font-mono text-sm animate-pulse flex-shrink-0"
          style={{ borderColor: accentColor, color: accentColor }}
          role="status"
          aria-live="polite"
        >
          ✓ {toast}
        </div>
      )}

      {/* Input bar — persistent across all tabs */}
      <div className="border-t border-[#2A2A44] p-4 bg-[#12121A] flex-shrink-0">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask ${ceoName} a question… (Enter to send, Shift+Enter for newline)`}
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
                : { borderColor: accentColor, color: accentColor, boxShadow: `0 0 8px ${accentColor}44` }
            }
          >
            Executize ⚡
          </button>
        </div>
      </div>
    </div>
  )
}
