/**
 * Left panel — tabbed: Artifacts | Jobs | History.
 * Width: 320px (w-80).
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 */

import { useEffect, useState } from 'react'
import type { ArtifactMeta, Job } from '../types/api'
import type { CeoState, ChatMessage } from '../App'
import { listArtifacts, listJobs, getArtifact, deleteArtifact, revealArtifact } from '../lib/api'
import { ChatHistoryModal } from './ChatHistoryModal'

const ARCHETYPE_COLORS: Record<string, string> = {
  operator:  '#FF2D78',
  visionary: '#8B5CF6',
  advocate:  '#7FFF00',
  analyst:   '#00F5FF',
}

type Tab = 'artifacts' | 'jobs' | 'history'
type HistoryFilter = 'all' | 'adopted' | 'modified' | 'rejected' | 'unresolved'

interface Props {
  artifacts: ArtifactMeta[]
  ceos: Record<string, CeoState>
  onRefresh: (artifacts: ArtifactMeta[]) => void
  onOpenArtifact: (artifact: ArtifactMeta) => void
}

// ---- Helpers ----

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`
  return `${(bytes / 1024).toFixed(1)}KB`
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// ---- Jobs Tab ----

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
    <span className={`font-mono text-[10px] ${styles[status] ?? 'text-[#8888AA]'}`}>
      {labels[status] ?? status}
    </span>
  )
}

function JobsTabContent() {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    listJobs().then(setJobs).catch(() => {})
  }, [])

  const recentJobs = jobs.slice(0, 5)

  return (
    <div className="flex flex-col gap-3 p-3 overflow-y-auto h-full">
      {recentJobs.length === 0 ? (
        <p className="text-[#8888AA] font-mono text-xs text-center mt-8">
          No jobs yet. Use Executize ⚡ for deep work.
        </p>
      ) : (
        recentJobs.map((job) => (
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
        ))
      )}
    </div>
  )
}

// ---- Artifacts Tab ----

function ArtifactsTabContent({ artifacts, onRefresh, onOpenArtifact }: {
  artifacts: ArtifactMeta[]
  onRefresh: (a: ArtifactMeta[]) => void
  onOpenArtifact: (a: ArtifactMeta) => void
}) {
  const [copyStates, setCopyStates] = useState<Record<string, boolean>>({})
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

  async function handleCopy(artifact: ArtifactMeta) {
    try {
      const detail = await getArtifact(artifact.session_id, artifact.filename)
      await navigator.clipboard.writeText(detail.content)
      setCopyStates(prev => ({ ...prev, [artifact.id]: true }))
      setTimeout(() => {
        setCopyStates(prev => ({ ...prev, [artifact.id]: false }))
      }, 1500)
    } catch {
      // silently fail
    }
  }

  async function handleReveal(artifact: ArtifactMeta) {
    try {
      await revealArtifact(artifact.session_id, artifact.filename)
    } catch {
      // silently fail
    }
  }

  async function handleDelete(artifact: ArtifactMeta) {
    try {
      await deleteArtifact(artifact.session_id, artifact.filename)
      const updated = await listArtifacts()
      onRefresh(updated)
    } catch {
      // silently fail
    } finally {
      setConfirmDelete(null)
    }
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#2A2A44] flex-shrink-0">
        <span className="font-mono text-[10px] text-[#8888AA]">
          {artifacts.length} artifact{artifacts.length !== 1 ? 's' : ''}
        </span>
        <button
          onClick={() => listArtifacts().then(onRefresh).catch(() => {})}
          className="text-[#8888AA] hover:text-[#00F5FF] font-mono text-xs transition-colors"
          aria-label="Refresh artifacts"
          title="Refresh"
        >
          ↻
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {artifacts.length === 0 ? (
          <p className="text-[#8888AA] font-mono text-xs text-center mt-8 px-4">
            No artifacts yet. Use Executize to create documents.
          </p>
        ) : (
          <ul role="list" className="py-1">
            {artifacts.map((artifact) => (
              <li key={artifact.id} className="border-b border-[#2A2A44] last:border-0">
                <div className="px-3 py-2 hover:bg-[#1A1A2E] transition-colors">
                  <button
                    onClick={() => onOpenArtifact(artifact)}
                    className="w-full text-left"
                    aria-label={`Open artifact: ${artifact.filename}`}
                  >
                    <p className="font-mono text-xs text-[#F0F0FF] truncate">{artifact.filename}</p>
                    <p className="font-mono text-[10px] text-[#8888AA]">
                      {formatDate(artifact.modified_at)} · {formatSize(artifact.size_bytes)}
                    </p>
                  </button>
                  <div className="flex gap-1 mt-1 flex-wrap">
                    <button
                      onClick={() => void handleCopy(artifact)}
                      className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#F0F0FF] hover:border-[#00F5FF] transition-colors"
                      aria-label={`Copy ${artifact.filename}`}
                    >
                      {copyStates[artifact.id] ? 'Copied!' : '⎘ Copy'}
                    </button>
                    <button
                      onClick={() => void handleReveal(artifact)}
                      className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#F0F0FF] hover:border-[#00F5FF] transition-colors"
                      aria-label={`Show ${artifact.filename} in Finder`}
                    >
                      📂 Finder
                    </button>
                    {confirmDelete === artifact.id ? (
                      <>
                        <button
                          onClick={() => void handleDelete(artifact)}
                          className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#FF2D78] text-[#FF2D78] hover:bg-[#FF2D7822] transition-colors"
                          aria-label="Confirm delete"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setConfirmDelete(null)}
                          className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#F0F0FF] transition-colors"
                          aria-label="Cancel delete"
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => setConfirmDelete(artifact.id)}
                        className="px-2 py-0.5 font-mono text-[10px] rounded border border-[#2A2A44] text-[#8888AA] hover:text-[#FF2D78] hover:border-[#FF2D78] transition-colors"
                        aria-label={`Delete ${artifact.filename}`}
                      >
                        ✕ Delete
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

// ---- History Tab ----

interface HistoryEntry {
  ceoSlug: string
  ceoName: string
  msgIndex: number
  msg: ChatMessage
}

function HistoryTabContent({ ceos }: { ceos: Record<string, CeoState> }) {
  const [filter, setFilter] = useState<HistoryFilter>('all')
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null)

  // Collect all assistant messages with a response across all CEOs
  const allEntries: HistoryEntry[] = []
  for (const [slug, ceo] of Object.entries(ceos)) {
    ceo.history.forEach((msg, i) => {
      if (msg.role === 'assistant' && msg.response) {
        allEntries.push({ ceoSlug: slug, ceoName: `The ${slug.charAt(0).toUpperCase()}${slug.slice(1)}`, msgIndex: i, msg })
      }
    })
  }

  // Try to get ceo name from history entry more accurately
  const filteredEntries = allEntries.filter(entry => {
    if (filter === 'all') return true
    if (filter === 'unresolved') return !entry.msg.decision
    return entry.msg.decision === filter
  })

  const filterButtons: { key: HistoryFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'adopted', label: '✓' },
    { key: 'modified', label: '~' },
    { key: 'rejected', label: '✗' },
    { key: 'unresolved', label: '?' },
  ]

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Filter buttons */}
      <div className="flex gap-1 px-3 py-1.5 border-b border-[#2A2A44] flex-shrink-0 flex-wrap">
        {filterButtons.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={[
              'px-2 py-0.5 font-mono text-[10px] rounded border transition-colors',
              filter === key
                ? 'border-[#00F5FF] text-[#00F5FF] bg-[#1A1A2E]'
                : 'border-[#2A2A44] text-[#8888AA] hover:text-[#F0F0FF]',
            ].join(' ')}
          >
            {label}
          </button>
        ))}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {filteredEntries.length === 0 ? (
          <p className="text-[#444466] font-mono text-xs text-center mt-8 px-4">
            No history entries yet.
          </p>
        ) : (
          <ul role="list" className="py-1">
            {filteredEntries.map((entry, i) => {
              const accentColor = ARCHETYPE_COLORS[entry.ceoSlug] ?? '#8888AA'
              const position = entry.msg.response?.position ?? entry.msg.content
              return (
                <li key={i}>
                  <button
                    onClick={() => setSelectedEntry(entry)}
                    className="w-full text-left px-3 py-2 hover:bg-[#1A1A2E] transition-colors border-b border-[#2A2A44] last:border-0"
                    aria-label={`View response from ${entry.ceoName}`}
                  >
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="font-mono text-[10px] font-bold" style={{ color: accentColor }}>
                        {entry.ceoName.replace('The ', '')}
                      </span>
                      {entry.msg.decision && (
                        <span className={`font-mono text-[10px] ${
                          entry.msg.decision === 'adopted' ? 'text-[#7FFF00]'
                          : entry.msg.decision === 'rejected' ? 'text-[#FF2D78]'
                          : 'text-[#FFE600]'
                        }`}>
                          {entry.msg.decision === 'adopted' ? '✓' : entry.msg.decision === 'rejected' ? '✗' : '~'}
                        </span>
                      )}
                    </div>
                    <p className="font-mono text-[10px] text-[#8888AA] truncate leading-relaxed">
                      {position.slice(0, 80)}{position.length > 80 ? '…' : ''}
                    </p>
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {/* Modal */}
      {selectedEntry && (
        <ChatHistoryModal
          msg={selectedEntry.msg}
          ceoName={selectedEntry.ceoName}
          accentColor={ARCHETYPE_COLORS[selectedEntry.ceoSlug] ?? '#8888AA'}
          onClose={() => setSelectedEntry(null)}
        />
      )}
    </div>
  )
}

// ---- Left Panel ----

export function LeftPanel({ artifacts, ceos, onRefresh, onOpenArtifact }: Props) {
  const [tab, setTab] = useState<Tab>('artifacts')

  useEffect(() => {
    listArtifacts().then(onRefresh).catch(() => {})
  }, [])

  const tabs: { key: Tab; label: string }[] = [
    { key: 'artifacts', label: 'Artifacts' },
    { key: 'jobs', label: 'Jobs' },
    { key: 'history', label: 'History' },
  ]

  return (
    <div
      className="w-80 flex-shrink-0 flex flex-col border-r border-[#2A2A44] bg-[#12121A] overflow-hidden"
      role="complementary"
      aria-label="Left panel"
    >
      {/* Tab strip */}
      <div className="flex border-b border-[#2A2A44] flex-shrink-0">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={[
              'flex-1 font-mono text-[10px] tracking-widest uppercase py-2 transition-colors',
              tab === key
                ? 'text-[#00F5FF] border-b border-[#00F5FF] bg-[#0D0D15]'
                : 'text-[#8888AA] hover:text-[#F0F0FF]',
            ].join(' ')}
            role="tab"
            aria-selected={tab === key}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {tab === 'artifacts' && (
          <ArtifactsTabContent
            artifacts={artifacts}
            onRefresh={onRefresh}
            onOpenArtifact={onOpenArtifact}
          />
        )}
        {tab === 'jobs' && <JobsTabContent />}
        {tab === 'history' && <HistoryTabContent ceos={ceos} />}
      </div>
    </div>
  )
}
