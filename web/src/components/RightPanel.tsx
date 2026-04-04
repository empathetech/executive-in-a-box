/**
 * Right pane — CRT panel treatment.
 * Dashboard tab: job history + CEO stats (radar + decision history).
 * Artifact mode: artifact content viewer.
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 *            hacky-hours/02-design/STYLE_GUIDE.md § CRT Panel Treatment
 */

import { useEffect, useState } from 'react'
import type { ArtifactMeta, ConfigResponse, Job, StatsResponse } from '../types/api'
import { getArtifact, getStats, listJobs } from '../lib/api'
import { RadarChart } from './RadarChart'

interface Props {
  mode: 'dashboard' | 'artifact'
  artifact: ArtifactMeta | null
  config: ConfigResponse
  activeCeoSlug: string
}

// ---- Jobs Tab ----

function JobsTab() {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    listJobs().then(setJobs).catch(() => {})
  }, [])

  const recentJobs = jobs.slice(0, 5)

  return (
    <div className="flex flex-col gap-4 p-4 h-full overflow-y-auto">
      {recentJobs.length === 0 ? (
        <p className="text-[#8888AA] font-mono text-xs">
          No jobs yet. Use Executize ⚡ for deep work.
        </p>
      ) : (
        <div className="space-y-2">
          {recentJobs.map((job) => (
            <div
              key={job.id}
              className="bg-[#1A1A2E] rounded border border-[#2A2A44] p-2 font-mono text-xs"
            >
              <div className="flex justify-between items-center">
                <span className="text-[#8888AA]">{job.archetype}</span>
                <JobStatusBadge status={job.status} />
              </div>
              <p className="text-[#F0F0FF] truncate mt-1">
                {job.prompt.slice(0, 60)}{job.prompt.length > 60 ? '…' : ''}
              </p>
            </div>
          ))}
        </div>
      )}
      <div className="mt-auto">
        <p className="font-mono text-[10px] text-[#8888AA] text-center">
          All data stored locally · No cloud sync
        </p>
      </div>
    </div>
  )
}

function JobStatusBadge({ status }: { status: Job['status'] }) {
  const styles: Record<string, string> = {
    queued:   'text-[#FFE600]',
    running:  'text-[#00F5FF] animate-pulse',
    complete: 'text-[#7FFF00]',
    failed:   'text-[#FF2D78]',
  }
  const labels: Record<string, string> = {
    queued: '⏳ queued',
    running: '⚡ running',
    complete: '✓ done',
    failed: '✗ failed',
  }
  return (
    <span className={styles[status] ?? 'text-[#8888AA]'}>
      {labels[status] ?? status}
    </span>
  )
}

// ---- CEO Stats Tab ----

function StatsTab({ config, activeCeoSlug }: { config: ConfigResponse; activeCeoSlug: string }) {
  const [data, setData] = useState<StatsResponse | null>(null)
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    getStats()
      .then((d) => {
        setData(d)
        const top = [...d.ceos].sort((a, b) => b.total - a.total)[0]
        if (top && top.total > 0) setSelected(top.slug)
        else setSelected(config.archetypes[0]?.slug ?? null)
      })
      .catch(() => {})
  }, [config.archetypes])

  const selectedCeo = data?.ceos.find((c) => c.slug === selected)

  return (
    <div className="flex flex-col gap-4 p-3 h-full overflow-y-auto">

      {/* Personality radar — shows only the active CEO */}
      <div>
        <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase mb-2">
          Personality Profile
        </p>
        <RadarChart
          archetypes={config.archetypes.filter((a) => a.slug === activeCeoSlug)}
        />
      </div>

      {/* Session-derived stats — only shown if there's history */}
      {data && data.total_sessions > 0 ? (
        <>
          {/* Per-CEO agreement table */}
          <div>
            <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase mb-2">
              Agreement Rate
            </p>
            <div className="space-y-1">
              {data.ceos.map((ceo) => (
                <button
                  key={ceo.slug}
                  onClick={() => setSelected(ceo.slug === selected ? null : ceo.slug)}
                  className={`w-full text-left font-mono text-[10px] px-2 py-1 rounded border transition-colors ${
                    selected === ceo.slug
                      ? 'border-[#00F5FF]/40 bg-[#1A1A2E]'
                      : 'border-transparent hover:border-[#2A2A44]'
                  } ${ceo.total === 0 ? 'opacity-40 cursor-default' : 'cursor-pointer'}`}
                  disabled={ceo.total === 0}
                >
                  <div className="flex justify-between items-center">
                    <span className="text-[#F0F0FF]">{ceo.name}</span>
                    {ceo.total > 0 ? (
                      <span className="text-[#7FFF00]">
                        {Math.round(ceo.agreement_rate * 100)}%
                      </span>
                    ) : (
                      <span className="text-[#444466]">—</span>
                    )}
                  </div>
                  {ceo.total > 0 && (
                    <div className="flex gap-2 mt-0.5 text-[9px]">
                      <span className="text-[#7FFF00]">{ceo.adopted}✓</span>
                      <span className="text-[#FFE600]">{ceo.modified}~</span>
                      <span className="text-[#FF2D78]">{ceo.rejected}✗</span>
                      <span className="text-[#8888AA] ml-auto">{ceo.total} sessions</span>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Decision history for selected CEO */}
          {selectedCeo && selectedCeo.recent_decisions.length > 0 && (
            <div>
              <p className="font-mono text-[9px] text-[#8888AA] tracking-widest uppercase mb-2">
                Recent — {selectedCeo.name}
              </p>
              <div className="space-y-2">
                {selectedCeo.recent_decisions.map((rec, i) => {
                  const decStyle: Record<string, string> = {
                    Adopted:  'text-[#7FFF00]',
                    Rejected: 'text-[#FF2D78]',
                    Modified: 'text-[#FFE600]',
                  }
                  const decIcon: Record<string, string> = {
                    Adopted: '✓', Rejected: '✗', Modified: '~',
                  }
                  return (
                    <div
                      key={i}
                      className="bg-[#1A1A2E] rounded border border-[#2A2A44] p-2 font-mono text-[10px]"
                    >
                      <div className="flex justify-between items-start gap-1 mb-1">
                        <span className="text-[#8888AA] truncate flex-1">{rec.question}</span>
                        <span className={`flex-shrink-0 ${decStyle[rec.decision] ?? 'text-[#8888AA]'}`}>
                          {decIcon[rec.decision] ?? '?'} {rec.decision}
                        </span>
                      </div>
                      <p className="text-[#F0F0FF] text-[9px] leading-relaxed line-clamp-2">
                        {rec.position}
                      </p>
                      {rec.modification && (
                        <p className="text-[#FFE600] text-[9px] mt-1 italic">
                          → {rec.modification}
                        </p>
                      )}
                      <p className="text-[#444466] text-[9px] mt-1">{rec.timestamp}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </>
      ) : (
        <p className="text-[#444466] font-mono text-[10px] text-center">
          Session agreement stats appear here after your first conversation.
        </p>
      )}
    </div>
  )
}

// ---- Usage Dashboard (tabs wrapper) ----

type DashTab = 'jobs' | 'stats'

function UsageDashboard({ config, activeCeoSlug }: { config: ConfigResponse; activeCeoSlug: string }) {
  const [tab, setTab] = useState<DashTab>('jobs')

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Config strip */}
      <div className="px-3 py-2 border-b border-[#2A2A44] bg-[#0D0D1A]">
        <div className="font-mono text-[9px] text-[#8888AA] space-y-0.5">
          <div className="flex justify-between">
            <span>Archetype</span>
            <span className="text-[#F0F0FF]">{config.archetype_name}</span>
          </div>
          <div className="flex justify-between">
            <span>Provider</span>
            <span className="text-[#F0F0FF]">{config.provider_name}</span>
          </div>
          <div className="flex justify-between">
            <span>API Key</span>
            <span className={config.api_key_set ? 'text-[#7FFF00]' : 'text-[#FF2D78]'}>
              {config.api_key_set ? '✓' : '✗ Missing'}
            </span>
          </div>
        </div>
      </div>

      {/* Tab strip */}
      <div className="flex border-b border-[#2A2A44]">
        {(['jobs', 'stats'] as DashTab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 font-mono text-[9px] tracking-widest uppercase py-1.5 transition-colors ${
              tab === t
                ? 'text-[#00F5FF] border-b border-[#00F5FF] bg-[#0D0D1A]'
                : 'text-[#8888AA] hover:text-[#F0F0FF]'
            }`}
          >
            {t === 'jobs' ? 'Jobs' : 'CEO Stats'}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {tab === 'jobs' ? <JobsTab /> : <StatsTab config={config} activeCeoSlug={activeCeoSlug} />}
      </div>
    </div>
  )
}

// ---- Artifact Viewer ----

function ArtifactViewer({ artifact }: { artifact: ArtifactMeta }) {
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
    <div className="flex flex-col h-full overflow-hidden p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-mono text-xs text-[#00F5FF] tracking-widest uppercase truncate">
          {artifact.filename}
        </h2>
      </div>
      {loading ? (
        <p className="text-[#8888AA] font-mono text-xs animate-pulse">Loading...</p>
      ) : (
        <pre className="flex-1 overflow-auto font-mono text-xs text-[#F0F0FF] whitespace-pre-wrap leading-relaxed">
          {content}
        </pre>
      )}
    </div>
  )
}

// ---- Right Panel ----

export function RightPanel({ mode, artifact, config, activeCeoSlug }: Props) {
  return (
    <div
      className="w-72 flex-shrink-0 crt-panel border-l border-[#2A2A44] overflow-hidden"
      role="complementary"
      aria-label={mode === 'dashboard' ? 'Usage dashboard' : 'Artifact viewer'}
    >
      {/* CRT header bar */}
      <div className="px-3 py-2 border-b border-[#2A2A44] flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-[#FF2D78]" aria-hidden="true" />
        <div className="w-2 h-2 rounded-full bg-[#FFE600]" aria-hidden="true" />
        <div className="w-2 h-2 rounded-full bg-[#7FFF00]" aria-hidden="true" />
        <span className="ml-2 font-mono text-[10px] text-[#8888AA] tracking-widest">
          {mode === 'dashboard' ? 'DASHBOARD' : 'ARTIFACT'}
        </span>
      </div>

      {mode === 'artifact' && artifact ? (
        <ArtifactViewer artifact={artifact} />
      ) : (
        <UsageDashboard config={config} activeCeoSlug={activeCeoSlug} />
      )}
    </div>
  )
}
