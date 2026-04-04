/**
 * Right pane — CRT panel treatment.
 * Default mode: LLM usage/cost dashboard.
 * Artifact mode: artifact content viewer.
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 *            hacky-hours/02-design/STYLE_GUIDE.md § CRT Panel Treatment
 */

import { useEffect, useState } from 'react'
import type { ArtifactMeta, ConfigResponse, Job } from '../types/api'
import { getArtifact, listJobs } from '../lib/api'

interface Props {
  mode: 'dashboard' | 'artifact'
  artifact: ArtifactMeta | null
  config: ConfigResponse
}

// ---- Usage Dashboard ----

function UsageDashboard({ config }: { config: ConfigResponse }) {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    listJobs().then(setJobs).catch(() => {})
  }, [])

  const recentJobs = jobs.slice(0, 5)

  return (
    <div className="flex flex-col gap-4 p-4 h-full overflow-y-auto">
      <div>
        <h2 className="font-mono text-xs text-[#00F5FF] tracking-widest uppercase mb-2">
          Configuration
        </h2>
        <div className="bg-[#1A1A2E] rounded border border-[#2A2A44] p-3 font-mono text-xs space-y-1">
          <div className="flex justify-between">
            <span className="text-[#8888AA]">Archetype</span>
            <span className="text-[#F0F0FF]">{config.archetype_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-[#8888AA]">Provider</span>
            <span className="text-[#F0F0FF]">{config.provider_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-[#8888AA]">API Key</span>
            <span className={config.api_key_set ? 'text-[#7FFF00]' : 'text-[#FF2D78]'}>
              {config.api_key_set ? '✓ Set' : '✗ Missing'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-[#8888AA]">Slack</span>
            <span className={config.slack_configured ? 'text-[#7FFF00]' : 'text-[#8888AA]'}>
              {config.slack_configured ? '✓ Configured' : '—'}
            </span>
          </div>
        </div>
      </div>

      <div>
        <h2 className="font-mono text-xs text-[#00F5FF] tracking-widest uppercase mb-2">
          Recent Jobs
        </h2>
        {recentJobs.length === 0 ? (
          <p className="text-[#8888AA] font-mono text-xs">
            No jobs yet. Use Executize for deep work.
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
      </div>

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

export function RightPanel({ mode, artifact, config }: Props) {
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
        <UsageDashboard config={config} />
      )}
    </div>
  )
}
