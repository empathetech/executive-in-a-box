/**
 * Announce modal — compose a Slack message, preview, and send.
 * Preview-before-send is enforced: the Send button only activates
 * after the user has clicked Preview.
 *
 * Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Slack Announce Flow
 */

import { useState } from 'react'
import type { ArchetypeInfo } from '../types/api'
import { sendSlack } from '../lib/api'

interface Props {
  archetypes: ArchetypeInfo[]
  activeCeoSlug: string
  onClose: () => void
}

export function AnnounceModal({ archetypes, activeCeoSlug, onClose }: Props) {
  const [message, setMessage] = useState('')
  const [selectedSlug, setSelectedSlug] = useState(activeCeoSlug)
  const [previewed, setPreviewed] = useState(false)
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectedArchetype = archetypes.find((a) => a.slug === selectedSlug)

  async function handleSend() {
    if (!previewed || !message.trim() || sending) return
    setSending(true)
    setError(null)
    try {
      await sendSlack({ message, archetype_slug: selectedSlug })
      setSent(true)
      setTimeout(onClose, 1500)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Send failed.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 bg-black/70"
      role="dialog"
      aria-modal="true"
      aria-label="Announce to Slack"
    >
      <div className="w-full max-w-lg mx-4 bg-[#12121A] border border-[#2A2A44] rounded overflow-hidden pixel-border">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#2A2A44]">
          <span className="font-mono text-sm text-[#00F5FF] tracking-widest uppercase">
            Announce to Slack
          </span>
          <button
            onClick={onClose}
            className="text-[#8888AA] hover:text-[#F0F0FF] font-mono text-sm transition-colors"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="p-4 space-y-4">
          {/* Archetype selector */}
          <div>
            <label className="block font-mono text-xs text-[#8888AA] mb-1" htmlFor="announce-ceo">
              Post as
            </label>
            <select
              id="announce-ceo"
              value={selectedSlug}
              onChange={(e) => { setSelectedSlug(e.target.value); setPreviewed(false) }}
              className="w-full bg-[#0A0A0F] border border-[#2A2A44] rounded px-3 py-2 font-mono text-sm text-[#F0F0FF] focus:outline-none focus:border-[#00F5FF]"
            >
              {archetypes.map((a) => (
                <option key={a.slug} value={a.slug}>{a.name}</option>
              ))}
            </select>
          </div>

          {/* Message textarea */}
          <div>
            <label className="block font-mono text-xs text-[#8888AA] mb-1" htmlFor="announce-msg">
              Message
            </label>
            <textarea
              id="announce-msg"
              value={message}
              onChange={(e) => { setMessage(e.target.value); setPreviewed(false) }}
              rows={5}
              placeholder="Write your announcement..."
              className="w-full bg-[#0A0A0F] border border-[#2A2A44] rounded px-3 py-2 font-mono text-sm text-[#F0F0FF] placeholder:text-[#8888AA] resize-none focus:outline-none focus:border-[#00F5FF]"
              aria-required="true"
            />
          </div>

          {/* Preview block */}
          {previewed && message.trim() && (
            <div
              className="border border-[#2A2A44] rounded p-3 bg-[#1A1A2E]"
              role="region"
              aria-label="Slack message preview"
            >
              <p className="font-mono text-[10px] text-[#8888AA] mb-2 uppercase tracking-widest">
                Preview
              </p>
              <div className="flex items-start gap-2">
                <div
                  className="w-8 h-8 rounded flex-shrink-0 flex items-center justify-center font-bold text-xs"
                  style={{ background: '#1A1A2E', border: '1px solid #2A2A44', color: '#F0F0FF' }}
                  aria-hidden="true"
                >
                  {selectedArchetype?.name[4] ?? '?'}
                </div>
                <div>
                  <p className="font-mono text-xs font-bold text-[#F0F0FF]">
                    {selectedArchetype?.name ?? 'CEO'}
                  </p>
                  <p className="font-mono text-xs text-[#F0F0FF] whitespace-pre-wrap leading-relaxed">
                    {message}
                  </p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <p className="font-mono text-xs text-[#FF2D78]" role="alert">{error}</p>
          )}

          {sent && (
            <p className="font-mono text-xs text-[#7FFF00]" role="status">Sent!</p>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-2 justify-end px-4 py-3 border-t border-[#2A2A44]">
          <button
            onClick={() => setPreviewed(true)}
            disabled={!message.trim()}
            className={[
              'px-4 py-2 font-mono text-xs rounded border transition-all',
              !message.trim()
                ? 'opacity-30 cursor-not-allowed border-[#2A2A44] text-[#8888AA]'
                : 'border-[#2A2A44] text-[#F0F0FF] hover:border-[#00F5FF] hover:text-[#00F5FF]',
            ].join(' ')}
          >
            Preview
          </button>
          <button
            onClick={() => void handleSend()}
            disabled={!previewed || !message.trim() || sending || sent}
            className={[
              'px-4 py-2 font-mono text-xs rounded border transition-all',
              !previewed || !message.trim() || sending || sent
                ? 'opacity-30 cursor-not-allowed border-[#2A2A44] text-[#8888AA]'
                : 'border-[#7FFF00] text-[#7FFF00] hover:shadow-lg',
            ].join(' ')}
            style={
              previewed && message.trim() && !sending && !sent
                ? { boxShadow: '0 0 8px #7FFF0044' }
                : undefined
            }
          >
            {sending ? 'Sending...' : 'Send to Slack'}
          </button>
        </div>
      </div>
    </div>
  )
}
