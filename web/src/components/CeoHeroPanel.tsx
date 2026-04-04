/**
 * CEO Hero Panel — full-width top panel replacing CeoStrip.
 * Shows active CEO portrait, blurb, personality radar, A/R/M stats,
 * mini icons for switching CEOs, and autonomy toggles.
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 */

import { useEffect, useMemo, useState } from 'react'
import type { ArchetypeInfo, ConfigResponse, StatsResponse } from '../types/api'
import type { CeoState } from '../App'
import { getStats, setAutonomy } from '../lib/api'
import { RadarChart } from './RadarChart'

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

interface Props {
  archetypes: ArchetypeInfo[]
  ceos: Record<string, CeoState>
  activeCeoSlug: string
  config: ConfigResponse
  onSelectCeo: (slug: string) => void
  onSetAutonomy: (slug: string, level: 1 | 2 | 3 | 4) => void
}

export function CeoHeroPanel({ archetypes, ceos, activeCeoSlug, config, onSelectCeo, onSetAutonomy }: Props) {
  const [stats, setStats] = useState<StatsResponse | null>(null)

  useEffect(() => {
    getStats().then(setStats).catch(() => {})
  }, [])

  const activeArchetype = archetypes.find(a => a.slug === activeCeoSlug)
  const activeCeo = ceos[activeCeoSlug]
  const accentColor = ARCHETYPE_COLORS[activeCeoSlug] ?? '#00F5FF'
  const isExecutizing = activeCeo?.activeJob != null && activeCeo.activeJob.status === 'running'
  const verb = EXECUTIZING_VERB[activeCeoSlug] ?? 'Thinking'

  const ceoStats = stats?.ceos.find(c => c.slug === activeCeoSlug)
  const total = ceoStats?.total ?? 0
  const adopted = ceoStats?.adopted ?? 0
  const modified = ceoStats?.modified ?? 0
  const rejected = ceoStats?.rejected ?? 0
  const agreementRate = ceoStats ? Math.round(ceoStats.agreement_rate * 100) : null

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

  return (
    <div
      className="flex-shrink-0 border-b border-[#2A2A44] bg-[#12121A] overflow-hidden"
      style={{ minHeight: '180px', maxHeight: '200px' }}
      role="banner"
      aria-label="Active CEO overview"
    >
      <div className="flex h-full">
        {/* === LEFT 45% — portrait + blurb + mini icons === */}
        <div className="flex flex-col" style={{ width: '45%', minWidth: '45%' }}>
          <div className="flex flex-1 gap-3 px-4 pt-3 pb-2 overflow-hidden">
            {/* Portrait + name */}
            <div className="flex flex-col items-center gap-1 flex-shrink-0">
              <div className="relative flex-shrink-0" style={{ width: 96, height: 96 }} aria-hidden="true">
                {/* Pulsing glow ring when active CEO is thinking/executizing */}
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
              <div className="text-center">
                {isExecutizing ? (
                  <p
                    className="font-mono text-xs animate-pulse"
                    style={{ color: accentColor }}
                    aria-live="polite"
                  >
                    {verb}...
                  </p>
                ) : (
                  <p className="font-mono text-xs text-[#F0F0FF]">
                    {activeArchetype?.name.replace('The ', '') ?? activeCeoSlug}
                  </p>
                )}
              </div>

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
                      style={{ width: 32, height: 32 }}
                    >
                      {/* Pulsing ring for busy mini icons */}
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

            {/* Blurb + autonomy */}
            <div className="flex flex-col gap-2 flex-1 min-w-0 pt-1">
              {activeArchetype && (
                <p className="font-mono text-[10px] leading-relaxed" style={{ color: `${accentColor}BB` }}>
                  {activeArchetype.response_style_blurb}
                </p>
              )}
              <p className="font-mono text-[9px] text-[#8888AA]">
                {activeArchetype?.one_line}
              </p>

              {/* Autonomy toggles */}
              {activeCeo && (
                <div className="flex gap-1 mt-auto" role="group" aria-label="Autonomy level">
                  {([1, 2, 3, 4] as const).map((level) => (
                    <button
                      key={level}
                      onClick={(e) => {
                        e.stopPropagation()
                        if (level > 2) return
                        setAutonomy(level).then(() => onSetAutonomy(activeCeoSlug, level))
                      }}
                      disabled={level > 2}
                      title={`Level ${level}: ${AUTONOMY_LABELS[level]}${level > 2 ? ' (coming soon)' : ''}`}
                      aria-label={`Autonomy level ${level}: ${AUTONOMY_LABELS[level]}`}
                      aria-pressed={activeCeo.autonomyLevel === level}
                      className={[
                        'w-6 h-6 font-mono text-[10px] rounded transition-all',
                        activeCeo.autonomyLevel === level
                          ? 'text-[#0A0A0F] font-bold'
                          : level > 2
                          ? 'opacity-30 cursor-not-allowed text-[#8888AA] border border-[#2A2A44]'
                          : 'text-[#8888AA] border border-[#2A2A44] hover:border-[#00F5FF]',
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
              )}
            </div>
          </div>
        </div>

        {/* === RIGHT 60% — three equal columns === */}
        <div className="flex flex-1 border-l border-[#2A2A44] overflow-hidden divide-x divide-[#2A2A44]">

          {/* Column 1 — Radar chart */}
          <div className="flex-1 flex flex-col items-center justify-center p-2 min-w-0">
            <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase mb-1">
              Personality
            </p>
            {activeArchetype && (
              <RadarChart archetypes={[activeArchetype]} />
            )}
          </div>

          {/* Column 2 — Session stats (A/R/M) */}
          <div className="flex-1 flex flex-col gap-2 p-3 min-w-0 justify-center">
            <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase">
              Agreement
            </p>
            <div>
              {agreementRate !== null ? (
                <p className="font-mono text-2xl font-bold leading-none" style={{ color: accentColor }}>
                  {agreementRate}%
                </p>
              ) : (
                <p className="font-mono text-2xl font-bold leading-none text-[#444466]">—</p>
              )}
              <p className="font-mono text-[10px] text-[#8888AA] mt-0.5">
                {total > 0 ? `${total} session${total !== 1 ? 's' : ''}` : 'no sessions yet'}
              </p>
            </div>
            {total > 0 && (
              <div className="flex flex-col gap-1">
                {[
                  { label: 'Adopted', count: adopted, color: '#7FFF00' },
                  { label: 'Modified', count: modified, color: '#FFE600' },
                  { label: 'Rejected', count: rejected, color: '#FF2D78' },
                ].map(({ label, count, color }) => (
                  <div key={label}>
                    <div className="flex justify-between font-mono text-[9px] mb-0.5">
                      <span style={{ color }}>{label}</span>
                      <span className="text-[#8888AA]">
                        {count} · {Math.round((count / total) * 100)}%
                      </span>
                    </div>
                    <div className="h-1 bg-[#1A1A2E] rounded-full overflow-hidden">
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

          {/* Column 3 — API info */}
          <div className="flex-1 flex flex-col gap-2 p-3 min-w-0 justify-center">
            <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase">
              API
            </p>
            <div className="font-mono text-[10px] space-y-1.5">
              <div>
                <p className="text-[#8888AA] text-[9px]">Provider</p>
                <p className="text-[#F0F0FF]">{config.provider_name}</p>
              </div>
              <div>
                <p className="text-[#8888AA] text-[9px]">Model</p>
                <p className="text-[#F0F0FF] truncate" title={currentModel ?? undefined}>
                  {currentModel ?? <span className="text-[#444466]">—</span>}
                </p>
              </div>
              <div>
                <p className="text-[#8888AA] text-[9px]">Session tokens</p>
                <p className="text-[#F0F0FF]">
                  {sessionTokens > 0
                    ? sessionTokens.toLocaleString()
                    : <span className="text-[#444466]">—</span>}
                </p>
              </div>
              <div>
                <p className="text-[#8888AA] text-[9px]">API key</p>
                <p className={config.api_key_set ? 'text-[#7FFF00]' : 'text-[#FF2D78]'}>
                  {config.api_key_set ? '✓ set' : '✗ missing'}
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
