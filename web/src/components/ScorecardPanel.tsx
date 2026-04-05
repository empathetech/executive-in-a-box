/**
 * ScorecardPanel — AGREEMENT stats + FEEDBACK synthesis, tabbed.
 *
 * AGREEMENT: adoption/modification/rejection rates + overall agreement %.
 * FEEDBACK: AI-synthesised calibration summary (1-2 sentences, first person)
 *   with a refresh button. The summary drives the system_prompt_addon injected
 *   into every future prompt — this is the grading feedback loop.
 */

import { useState } from 'react'
import type { CeoStats, FeedbackResponse } from '../types/api'
import { refreshFeedback, clearFeedback } from '../lib/api'

type Tab = 'agreement' | 'feedback'

// ---- Agreement Tab ----

function AgreementTab({
  stats,
  accentColor,
}: {
  stats: CeoStats | undefined
  accentColor: string
}) {
  const total = stats?.total ?? 0
  const adopted = stats?.adopted ?? 0
  const modified = stats?.modified ?? 0
  const rejected = stats?.rejected ?? 0
  const agreementRate = stats ? Math.round(stats.agreement_rate * 100) : null

  return (
    <div className="flex flex-col gap-2 h-full overflow-y-auto">
      <div>
        {agreementRate !== null ? (
          <p className="font-mono text-3xl font-bold leading-none" style={{ color: accentColor }}>
            {agreementRate}%
          </p>
        ) : (
          <p className="font-mono text-3xl font-bold leading-none text-[#444466]">—</p>
        )}
        <p className="font-mono text-xs text-[#8888AA] mt-0.5">
          {total > 0 ? `${total} session${total !== 1 ? 's' : ''}` : 'no sessions yet'}
        </p>
      </div>
      {total > 0 && (
        <div className="flex flex-col gap-1.5">
          {[
            { label: 'Adopted', count: adopted, color: '#7FFF00' },
            { label: 'Modified', count: modified, color: '#FFE600' },
            { label: 'Rejected', count: rejected, color: '#FF2D78' },
          ].map(({ label, count, color }) => (
            <div key={label}>
              <div className="flex justify-between font-mono text-[10px] mb-0.5">
                <span style={{ color }}>{label}</span>
                <span className="text-[#8888AA]">
                  {count} · {Math.round((count / total) * 100)}%
                </span>
              </div>
              <div className="h-1.5 bg-[#1A1A2E] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${(count / total) * 100}%`, backgroundColor: color }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ---- Feedback Tab ----

function FeedbackTab({
  slug,
  feedback,
  onFeedbackUpdated,
}: {
  slug: string
  feedback: FeedbackResponse | null
  onFeedbackUpdated: (f: FeedbackResponse) => void
}) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [clearing, setClearing] = useState(false)

  async function handleRefresh() {
    setLoading(true)
    setError(null)
    try {
      const result = await refreshFeedback(slug)
      onFeedbackUpdated(result)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Refresh failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleClear() {
    setClearing(true)
    try {
      await clearFeedback(slug)
      onFeedbackUpdated({
        slug,
        summary: null,
        trait_adjustments: {},
        system_prompt_addon: null,
        updated_at: null,
        decision_count: 0,
      })
    } catch {
      // silently ignore
    } finally {
      setClearing(false)
    }
  }

  const hasFeedback = feedback?.summary != null && feedback.summary.length > 0
  const decisionCount = feedback?.decision_count ?? 0

  return (
    <div className="flex flex-col gap-2 h-full overflow-y-auto">
      {/* Summary */}
      {hasFeedback ? (
        <div className="font-mono text-xs text-[#F0F0FF] leading-relaxed italic">
          {feedback!.summary}
        </div>
      ) : (
        <p className="font-mono text-[10px] text-[#444466] leading-relaxed">
          {decisionCount > 0
            ? `${decisionCount} decision${decisionCount !== 1 ? 's' : ''} logged — click Update to synthesise.`
            : 'No decisions yet. Make some decisions first, then update feedback.'}
        </p>
      )}

      {error && (
        <p className="font-mono text-[10px] text-[#FF2D78]">{error}</p>
      )}

      {/* Updated at */}
      {feedback?.updated_at && (
        <p className="font-mono text-[9px] text-[#444466]">
          Updated {new Date(feedback.updated_at).toLocaleDateString()}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-1 mt-auto flex-wrap">
        <button
          onClick={() => void handleRefresh()}
          disabled={loading}
          className="px-2 py-0.5 font-mono text-[9px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#00F5FF] hover:border-[#00F5FF] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '⟳ Updating…' : '↻ Update Feedback'}
        </button>
        {hasFeedback && (
          <button
            onClick={() => void handleClear()}
            disabled={clearing}
            className="px-2 py-0.5 font-mono text-[9px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#FF2D78] hover:border-[#FF2D78] disabled:opacity-30 transition-colors"
            title="Clear feedback and revert to baseline"
          >
            ✕ Reset
          </button>
        )}
      </div>

      {/* Active badge */}
      {hasFeedback && (
        <p className="font-mono text-[9px] text-[#7FFF00]">
          ✓ Active — injected into future prompts
        </p>
      )}
    </div>
  )
}

// ---- Panel ----

interface Props {
  stats: CeoStats | undefined
  slug: string
  feedback: FeedbackResponse | null
  accentColor: string
  onFeedbackUpdated: (f: FeedbackResponse) => void
}

export function ScorecardPanel({ stats, slug, feedback, accentColor, onFeedbackUpdated }: Props) {
  const [tab, setTab] = useState<Tab>('agreement')

  return (
    <div className="flex flex-col h-full">
      {/* Tab strip */}
      <div className="flex border-b border-[#2A2A44] flex-shrink-0 mb-1.5">
        {([['agreement', 'Agreement'], ['feedback', 'Feedback']] as [Tab, string][]).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={[
              'flex-1 font-mono text-[9px] tracking-widest uppercase py-1 transition-colors',
              tab === key
                ? 'border-b border-[#00F5FF] text-[#00F5FF]'
                : 'text-[#8888AA] hover:text-[#F0F0FF]',
            ].join(' ')}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-hidden">
        {tab === 'agreement' && (
          <AgreementTab stats={stats} accentColor={accentColor} />
        )}
        {tab === 'feedback' && (
          <FeedbackTab
            slug={slug}
            feedback={feedback}
            onFeedbackUpdated={onFeedbackUpdated}
          />
        )}
      </div>
    </div>
  )
}
