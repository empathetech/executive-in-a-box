/**
 * Announce modal — compose a Slack message, preview, and send.
 * Preview-before-send is enforced: the Send button only activates
 * after the user has clicked Preview.
 *
 * Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Slack Announce Flow
 */

import { useEffect, useState } from 'react'
import type { SlackChannel } from '../types/api'
import { getSlackChannels, sendSlack } from '../lib/api'

interface Props {
  activeCeoSlug: string
  prefillMessage?: string
  onClose: () => void
}

export function AnnounceModal({ activeCeoSlug, prefillMessage, onClose }: Props) {
  const [message, setMessage] = useState(prefillMessage ?? '')
  const [channels, setChannels] = useState<SlackChannel[]>([])
  const [channelsLoading, setChannelsLoading] = useState(true)
  const [selectedWorkspace, setSelectedWorkspace] = useState('')
  const [selectedChannelId, setSelectedChannelId] = useState('')
  const [previewed, setPreviewed] = useState(false)
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Sync message when prefill changes (e.g. opened from a different DecisionBar)
  useEffect(() => {
    setMessage(prefillMessage ?? '')
    setPreviewed(false)
  }, [prefillMessage])

  // Fetch channels on mount
  useEffect(() => {
    setChannelsLoading(true)
    getSlackChannels()
      .then((ch) => {
        setChannels(ch)
        if (ch.length > 0) {
          setSelectedWorkspace(ch[0].workspace)
          setSelectedChannelId(ch[0].id)
        }
      })
      .catch(() => {})
      .finally(() => setChannelsLoading(false))
  }, [])

  // When workspace changes, select first channel in that workspace
  function handleWorkspaceChange(ws: string) {
    setSelectedWorkspace(ws)
    const first = channels.find((c) => c.workspace === ws)
    setSelectedChannelId(first?.id ?? '')
    setPreviewed(false)
  }

  // Unique workspaces in order
  const workspaces = Array.from(new LinkedSet(channels.map((c) => c.workspace)))

  // Channels filtered by selected workspace
  const filteredChannels = channels.filter((c) => c.workspace === selectedWorkspace)
  const selectedChannel = channels.find((c) => c.id === selectedChannelId)

  async function handleSend() {
    if (!previewed || !message.trim() || !selectedChannelId || sending) return
    setSending(true)
    setError(null)
    try {
      await sendSlack({
        message,
        webhook_id: selectedChannelId,
        archetype_slug: activeCeoSlug,
      })
      setSent(true)
      setTimeout(onClose, 1500)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Send failed.')
    } finally {
      setSending(false)
    }
  }

  const noChannels = !channelsLoading && channels.length === 0

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
          {noChannels ? (
            <div
              className="border border-[#2A2A44] rounded p-3 bg-[#1A1A2E] font-mono text-xs text-[#8888AA] whitespace-pre-line"
              role="status"
            >
              No Slack webhooks configured.{'\n'}Run: exec-in-a-box slack setup
            </div>
          ) : (
            <>
              {/* Workspace selector */}
              <div>
                <label
                  className="block font-mono text-xs text-[#8888AA] mb-1"
                  htmlFor="announce-workspace"
                >
                  Workspace
                </label>
                <select
                  id="announce-workspace"
                  value={selectedWorkspace}
                  onChange={(e) => handleWorkspaceChange(e.target.value)}
                  disabled={channelsLoading}
                  className="w-full bg-[#0A0A0F] border border-[#2A2A44] rounded px-3 py-2 font-mono text-sm text-[#F0F0FF] focus:outline-none focus:border-[#00F5FF] disabled:opacity-50"
                >
                  {workspaces.map((ws) => (
                    <option key={ws} value={ws}>{ws}</option>
                  ))}
                </select>
              </div>

              {/* Channel selector */}
              <div>
                <label
                  className="block font-mono text-xs text-[#8888AA] mb-1"
                  htmlFor="announce-channel"
                >
                  Channel
                </label>
                <select
                  id="announce-channel"
                  value={selectedChannelId}
                  onChange={(e) => { setSelectedChannelId(e.target.value); setPreviewed(false) }}
                  disabled={channelsLoading}
                  className="w-full bg-[#0A0A0F] border border-[#2A2A44] rounded px-3 py-2 font-mono text-sm text-[#F0F0FF] focus:outline-none focus:border-[#00F5FF] disabled:opacity-50"
                >
                  {filteredChannels.map((c) => (
                    <option key={c.id} value={c.id}>{c.channel}</option>
                  ))}
                </select>
              </div>
            </>
          )}

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
                  {(selectedChannel?.channel ?? '#')[1]?.toUpperCase() ?? '?'}
                </div>
                <div>
                  <p className="font-mono text-xs font-bold text-[#F0F0FF]">
                    {selectedChannel ? `${selectedChannel.workspace} / ${selectedChannel.channel}` : 'Slack'}
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
            disabled={!message.trim() || noChannels}
            className={[
              'px-4 py-2 font-mono text-xs rounded border transition-all',
              !message.trim() || noChannels
                ? 'opacity-30 cursor-not-allowed border-[#2A2A44] text-[#8888AA]'
                : 'border-[#2A2A44] text-[#F0F0FF] hover:border-[#00F5FF] hover:text-[#00F5FF]',
            ].join(' ')}
          >
            Preview
          </button>
          <button
            onClick={() => void handleSend()}
            disabled={!previewed || !message.trim() || !selectedChannelId || sending || sent || noChannels}
            className={[
              'px-4 py-2 font-mono text-xs rounded border transition-all',
              !previewed || !message.trim() || !selectedChannelId || sending || sent || noChannels
                ? 'opacity-30 cursor-not-allowed border-[#2A2A44] text-[#8888AA]'
                : 'border-[#7FFF00] text-[#7FFF00] hover:shadow-lg',
            ].join(' ')}
            style={
              previewed && message.trim() && selectedChannelId && !sending && !sent && !noChannels
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

/** Order-preserving unique set helper. */
class LinkedSet<T> extends Set<T> {
  constructor(iterable?: Iterable<T>) {
    super(iterable)
  }
  [Symbol.iterator](): IterableIterator<T> {
    return super[Symbol.iterator]()
  }
}
