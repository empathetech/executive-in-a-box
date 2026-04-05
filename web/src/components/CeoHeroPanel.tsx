/**
 * CEO Hero Panel — full-width top panel replacing CeoStrip.
 * Shows active CEO portrait, blurb, personality radar, A/R/M stats,
 * mini icons for switching CEOs, and autonomy toggles.
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 */

import { useEffect, useMemo, useState } from 'react'
import type { ArchetypeInfo, ConfigResponse, FeedbackResponse, StatsResponse } from '../types/api'
import type { CeoState } from '../App'
import { getStats, setAutonomy, getFeedback, setFeedbackActive } from '../lib/api'
import { RadarChart } from './RadarChart'
import { ScorecardPanel } from './ScorecardPanel'
import { IntegrationsPanel } from './IntegrationsPanel'

const ARCHETYPE_COLORS: Record<string, string> = {
  operator:  '#FF2D78',
  visionary: '#8B5CF6',
  advocate:  '#7FFF00',
  analyst:   '#00F5FF',
}

const EXECUTIZING_VERB: Record<string, string> = {
  operator:  'Strategizing',
  visionary: 'Envisioning',
  advocate:  'Empathizing',
  analyst:   'Analyzing',
}

const AUTONOMY_LABELS: Record<number, string> = {
  1: 'Advisor',
  2: 'Recommender',
  3: 'Delegated',
  4: 'Autonomous',
}

const AUTONOMY_DESCRIPTIONS: Record<number, string> = {
  1: 'Reviews and advises. You make all final decisions.',
  2: 'Provides structured recommendations. You approve before anything happens.',
  3: 'Acts with your approval on defined tasks. (Coming soon)',
  4: 'Full delegation within set boundaries. (Coming soon)',
}

const AUTONOMY_TOOLTIPS: Record<number, string> = {
  1: 'Level 1 — Advisor: The CEO gives you a position and reasoning. You decide what to do with it.',
  2: 'Level 2 — Recommender: The CEO structures a recommendation for you to approve or modify before acting.',
  3: 'Level 3 — Delegated: The CEO can execute on defined tasks with your approval. (Coming soon)',
  4: 'Level 4 — Autonomous: Full delegation within boundaries you set. (Coming soon)',
}

interface Props {
  archetypes: ArchetypeInfo[]
  ceos: Record<string, CeoState>
  activeCeoSlug: string
  config: ConfigResponse
  statsVersion?: number   // incremented by App on each decision to trigger stats refresh
  onSelectCeo: (slug: string) => void
  onSetAutonomy: (slug: string, level: 1 | 2 | 3 | 4) => void
}

export function CeoHeroPanel({ archetypes, ceos, activeCeoSlug, config, statsVersion = 0, onSelectCeo, onSetAutonomy }: Props) {
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [feedback, setFeedback] = useState<FeedbackResponse | null>(null)

  // Re-fetch stats whenever a decision is recorded (statsVersion bumped by App)
  useEffect(() => {
    getStats().then(setStats).catch(() => {})
  }, [statsVersion])

  // Reload feedback whenever the active CEO changes
  useEffect(() => {
    setFeedback(null)
    getFeedback(activeCeoSlug).then(setFeedback).catch(() => {})
  }, [activeCeoSlug])

  const activeArchetype = archetypes.find(a => a.slug === activeCeoSlug)
  const activeCeo = ceos[activeCeoSlug]
  const accentColor = ARCHETYPE_COLORS[activeCeoSlug] ?? '#00F5FF'
  const isExecutizing = activeCeo?.activeJob != null && activeCeo.activeJob.status === 'running'
  const verb = EXECUTIZING_VERB[activeCeoSlug] ?? 'Thinking'

  const ceoStats = stats?.ceos.find(c => c.slug === activeCeoSlug)

  // Session token total — sum input+output across all responses in current session
  const sessionTokens = useMemo(() => {
    return activeCeo?.history
      .filter(m => m.response)
      .reduce((sum, m) => sum + (m.response!.input_tokens + m.response!.output_tokens), 0) ?? 0
  }, [activeCeo?.history])

  // Most recent model name from any response in this session
  const currentModel = useMemo(() => {
    return activeCeo?.history
      .slice()
      .reverse()
      .find(m => m.response)
      ?.response?.model ?? null
  }, [activeCeo?.history])

  const otherArchetypes = archetypes.filter(a => a.slug !== activeCeoSlug)

  // Default to adjusted active (true); fall back to true when no feedback loaded yet
  const isAdjustedActive = feedback?.active !== false

  async function handleToggleActive() {
    if (!feedback) return
    try {
      const updated = await setFeedbackActive(activeCeoSlug, !isAdjustedActive)
      setFeedback(updated)
    } catch {
      // best-effort
    }
  }

  return (
    <div
      className="flex-shrink-0 border-b border-[#2A2A44] bg-[#12121A] overflow-hidden"
      style={{ minHeight: '240px', maxHeight: '265px' }}
      role="banner"
      aria-label="Active CEO overview"
    >
      <div className="flex h-full">
        {/* === (1) PROFILE — portrait / autonomy / mini icons / blurb === */}
        <div className="flex flex-col" style={{ width: '42%', minWidth: '42%' }}>
          <p className="font-mono text-[10px] text-[#8888AA] tracking-widest uppercase px-4 pt-2 flex-shrink-0">
            Profile
          </p>
          <div className="flex flex-1 gap-3 px-4 pt-1 pb-2 overflow-hidden">

            {/* Column A: portrait + name + autonomy buttons + mini icons */}
            <div className="flex flex-col items-center gap-1 flex-shrink-0">

              {/* Portrait */}
              <div className="relative flex-shrink-0" style={{ width: 80, height: 80 }} aria-hidden="true">
                {isExecutizing && (
                  <div
                    className="absolute inset-0 rounded animate-ping"
                    style={{ border: `2px solid ${accentColor}`, opacity: 0.6 }}
                  />
                )}
                <div
                  className="rounded overflow-hidden w-full h-full"
                  style={{
                    border: `2px solid ${accentColor}`,
                    boxShadow: isExecutizing
                      ? `0 0 20px ${accentColor}88, 0 0 40px ${accentColor}44`
                      : `0 0 12px ${accentColor}44`,
                    transition: 'box-shadow 0.3s ease',
                  }}
                >
                  <img
                    src={`/ceo-${activeCeoSlug}.png`}
                    alt={activeArchetype?.name ?? activeCeoSlug}
                    className={['w-full h-full object-cover transition-opacity', isExecutizing ? 'opacity-70' : 'opacity-100'].join(' ')}
                  />
                </div>
              </div>

              {/* Name / executizing verb */}
              <div className="text-center">
                {isExecutizing ? (
                  <p className="font-mono text-xs animate-pulse" style={{ color: accentColor }} aria-live="polite">
                    {verb}…
                  </p>
                ) : (
                  <p className="font-mono text-xs text-[#F0F0FF]">
                    {activeArchetype?.name.replace('The ', '') ?? activeCeoSlug}
                  </p>
                )}
              </div>

              {/* Autonomy level buttons */}
              {activeCeo && (
                <div className="flex flex-col items-center gap-0.5 mt-1">
                  <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase">Autonomy</p>
                  <div className="flex gap-1" role="group" aria-label="Autonomy level">
                    {([1, 2, 3, 4] as const).map((level) => (
                      <button
                        key={level}
                        onClick={(e) => {
                          e.stopPropagation()
                          if (level > 2) return
                          setAutonomy(level).then(() => onSetAutonomy(activeCeoSlug, level))
                        }}
                        disabled={level > 2}
                        title={AUTONOMY_TOOLTIPS[level]}
                        aria-label={`Autonomy level ${level}: ${AUTONOMY_LABELS[level]}`}
                        aria-pressed={activeCeo.autonomyLevel === level}
                        className={[
                          'w-6 h-6 font-mono text-xs rounded transition-all',
                          activeCeo.autonomyLevel === level
                            ? 'text-[#0A0A0F] font-bold'
                            : level > 2
                            ? 'opacity-30 cursor-not-allowed text-[#8888AA] border border-[#2A2A44]'
                            : 'text-[#8888AA] border border-[#2A2A44] hover:border-[#00F5FF] hover:text-[#F0F0FF]',
                        ].join(' ')}
                        style={
                          activeCeo.autonomyLevel === level
                            ? { background: accentColor, borderColor: accentColor }
                            : undefined
                        }
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Mini icons for other CEOs */}
              <div className="flex gap-1 mt-1 flex-wrap justify-center">
                {otherArchetypes.map(arch => {
                  const otherColor = ARCHETYPE_COLORS[arch.slug] ?? '#8888AA'
                  const otherCeo = ceos[arch.slug]
                  const otherExecutizing = otherCeo?.activeJob != null && otherCeo.activeJob.status === 'running'
                  return (
                    <button
                      key={arch.slug}
                      onClick={() => onSelectCeo(arch.slug)}
                      title={otherExecutizing ? `${arch.name} — thinking…` : arch.name}
                      aria-label={`Switch to ${arch.name}${otherExecutizing ? ' (thinking)' : ''}`}
                      className="relative flex-shrink-0 hover:opacity-90 transition-opacity"
                      style={{ width: 28, height: 28 }}
                    >
                      {otherExecutizing && (
                        <div
                          className="absolute inset-0 rounded-full animate-ping"
                          style={{ border: `2px solid ${otherColor}`, opacity: 0.7 }}
                        />
                      )}
                      <div
                        className="rounded-full overflow-hidden w-full h-full"
                        style={{
                          border: `2px solid ${otherColor}`,
                          boxShadow: otherExecutizing ? `0 0 8px ${otherColor}88` : undefined,
                        }}
                      >
                        <img
                          src={`/ceo-${arch.slug}.png`}
                          alt={arch.name}
                          className={['w-full h-full object-cover', otherExecutizing ? 'opacity-60' : ''].join(' ')}
                        />
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Column B: CEO identity (top) then autonomy description — both top-justified */}
            <div className="flex flex-col flex-1 min-w-0 pt-1 gap-2">
              {/* CEO identity — never moves */}
              <div className="flex flex-col gap-1">
                {activeArchetype && (
                  <p className="font-mono text-xs leading-relaxed" style={{ color: `${accentColor}CC` }}>
                    {activeArchetype.response_style_blurb}
                  </p>
                )}
                <p className="font-mono text-[11px] text-[#8888AA]">
                  {activeArchetype?.one_line}
                </p>
              </div>

              {/* Autonomy description — sits directly below CEO text, top-justified */}
              {activeCeo && (
                <div className="border-t border-[#2A2A44] pt-1">
                  <p className="font-mono text-[10px] text-[#8888AA] uppercase tracking-widest mb-0.5">
                    Level {activeCeo.autonomyLevel} — {AUTONOMY_LABELS[activeCeo.autonomyLevel]}
                  </p>
                  <p className="font-mono text-xs text-[#F0F0FF] leading-snug">
                    {AUTONOMY_DESCRIPTIONS[activeCeo.autonomyLevel]}
                  </p>
                </div>
              )}
            </div>

          </div>
        </div>

        {/* === RIGHT 60% — three labeled equal columns === */}
        <div className="flex flex-1 border-l border-[#2A2A44] overflow-hidden divide-x divide-[#2A2A44]">

          {/* (2) PERSONALITY — Radar chart */}
          <div className="flex-1 flex flex-col p-2 min-w-0 overflow-hidden">
            <p className="font-mono text-[10px] text-[#8888AA] tracking-widest uppercase mb-1 flex-shrink-0">
              Personality
            </p>
            {activeArchetype && (
              <RadarChart
                archetypes={[activeArchetype]}
                traitAdjustments={feedback?.trait_adjustments}
                isAdjustedActive={isAdjustedActive}
                onToggleActive={() => void handleToggleActive()}
              />
            )}
          </div>

          {/* (3) SCORECARD — Agreement + Feedback tabs */}
          <div className="flex-1 flex flex-col p-2 min-w-0 overflow-hidden">
            <p className="font-mono text-[10px] text-[#8888AA] tracking-widest uppercase mb-1 flex-shrink-0">
              Scorecard
            </p>
            <div className="flex-1 overflow-hidden">
              <ScorecardPanel
                stats={ceoStats}
                slug={activeCeoSlug}
                feedback={feedback}
                accentColor={accentColor}
                onFeedbackUpdated={setFeedback}
              />
            </div>
          </div>

          {/* (4) INTEGRATIONS — LLMs + Slack */}
          <div className="flex-1 flex flex-col p-2 min-w-0 overflow-hidden">
            <p className="font-mono text-[10px] text-[#8888AA] tracking-widest uppercase mb-1 flex-shrink-0">
              Integrations
            </p>
            <div className="flex-1 overflow-hidden">
              <IntegrationsPanel
                accentColor={accentColor}
                currentModel={currentModel}
                sessionTokens={sessionTokens}
                providerName={config.provider_name}
                apiKeySet={config.api_key_set}
              />
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
