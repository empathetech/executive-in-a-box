/**
 * DecisionBar — action buttons shown below each assistant response.
 * Allows the user to adopt, reject, modify, or announce a CEO position.
 *
 * Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Decision Flow
 */

import { useState } from 'react'
import type { SessionResponse } from '../types/api'
import { sendDecision } from '../lib/api'

interface Props {
  response: SessionResponse
  activeCeoSlug: string
  onAnnounce: (prefillMessage: string, archetype_slug: string) => void
}

export function DecisionBar({ response, activeCeoSlug, onAnnounce }: Props) {
  const [showModifyInput, setShowModifyInput] = useState(false)
  const [modifyText, setModifyText] = useState('')
  const [logging, setLogging] = useState(false)
  const [logged, setLogged] = useState(false)

  async function logDecision(decisionValue: string, modification?: string) {
    setLogging(true)
    try {
      await sendDecision({
        archetype_slug: activeCeoSlug,
        question: response.questions_for_user[0] ?? '',
        position: response.position,
        confidence: response.confidence,
        ambition_level: response.ambition_level,
        decision: decisionValue,
        modification,
      })
      setLogged(true)
    } catch {
      // silently fail — decision logging is best-effort
      setLogged(true)
    } finally {
      setLogging(false)
    }
  }

  function handleAdopt() {
    void logDecision('adopted')
  }

  function handleReject() {
    void logDecision('rejected')
  }

  function handleModifyConfirm() {
    if (!modifyText.trim()) return
    void logDecision('modified', modifyText.trim())
    setShowModifyInput(false)
  }

  function handleAnnounce() {
    onAnnounce(response.position, activeCeoSlug)
  }

  if (logged) {
    return (
      <div className="mt-1 pl-1 font-mono text-[10px] text-[#444466]">
        ✓ logged to decisions.md
      </div>
    )
  }

  return (
    <div className="mt-2 flex flex-col gap-1">
      {!showModifyInput ? (
        <div className="flex gap-1 flex-wrap">
          <button
            onClick={handleAdopt}
            disabled={logging}
            className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#7FFF00]/50 text-[#7FFF00] hover:border-[#7FFF00] transition-colors disabled:opacity-40"
            aria-label="Adopt this position"
          >
            ✓ Adopt
          </button>
          <button
            onClick={handleReject}
            disabled={logging}
            className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#FF2D78]/50 text-[#FF2D78] hover:border-[#FF2D78] transition-colors disabled:opacity-40"
            aria-label="Reject this position"
          >
            ✗ Reject
          </button>
          <button
            onClick={() => setShowModifyInput(true)}
            disabled={logging}
            className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#FFE600]/50 text-[#FFE600] hover:border-[#FFE600] transition-colors disabled:opacity-40"
            aria-label="Modify this position"
          >
            ~ Modify
          </button>
          <button
            onClick={handleAnnounce}
            disabled={logging}
            className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#00F5FF]/50 text-[#00F5FF] hover:border-[#00F5FF] transition-colors disabled:opacity-40"
            aria-label="Announce this position to Slack"
          >
            ↗ Announce
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-1">
          <textarea
            value={modifyText}
            onChange={(e) => setModifyText(e.target.value)}
            placeholder="Describe your modification..."
            rows={2}
            aria-label="Modification text"
            className="w-full bg-[#0A0A0F] border border-[#FFE600]/40 rounded px-2 py-1 font-mono text-[10px] text-[#F0F0FF] placeholder:text-[#8888AA] resize-none focus:outline-none focus:border-[#FFE600]"
          />
          <div className="flex gap-1">
            <button
              onClick={handleModifyConfirm}
              disabled={!modifyText.trim() || logging}
              className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#FFE600]/50 text-[#FFE600] hover:border-[#FFE600] transition-colors disabled:opacity-40"
              aria-label="Confirm modification"
            >
              Confirm
            </button>
            <button
              onClick={() => { setShowModifyInput(false); setModifyText('') }}
              className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#F0F0FF] transition-colors"
              aria-label="Cancel modification"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
