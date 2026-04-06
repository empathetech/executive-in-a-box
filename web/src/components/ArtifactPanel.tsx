/**
 * Left pane — artifact explorer.
 * Lists session artifacts, click to open in right pane.
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 */

import { useEffect } from 'react'
import type { ArtifactMeta } from '../types/api'
import { listArtifacts } from '../lib/api'

interface Props {
  artifacts: ArtifactMeta[]
  onRefresh: (artifacts: ArtifactMeta[]) => void
  onOpen: (artifact: ArtifactMeta) => void
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`
  return `${(bytes / 1024).toFixed(1)}KB`
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function ArtifactPanel({ artifacts, onRefresh, onOpen }: Props) {
  useEffect(() => {
    listArtifacts()
      .then(onRefresh)
      .catch(() => {/* silently ignore on first load */})
  }, [])

  return (
    <div
      className="w-52 flex-shrink-0 flex flex-col border-r border-[#2A2A44] bg-[#12121A] overflow-hidden"
      role="complementary"
      aria-label="Artifact explorer"
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#2A2A44]">
        <span className="font-mono text-xs text-[#00F5FF] tracking-widest uppercase">
          Artifacts
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

      <div className="flex-1 overflow-y-auto">
        {artifacts.length === 0 ? (
          <div className="p-4">
            <p className="text-[#8888AA] font-mono text-xs text-center leading-relaxed">
              No artifacts yet.{'\n'}Use Executize to create documents.
            </p>
          </div>
        ) : (
          <ul role="list" className="py-1">
            {artifacts.map((artifact) => (
              <li key={artifact.id}>
                <button
                  onClick={() => onOpen(artifact)}
                  className={[
                    'w-full text-left px-3 py-2 hover:bg-[#1A1A2E] transition-colors',
                    'border-b border-[#2A2A44] last:border-0',
                  ].join(' ')}
                  aria-label={`Open artifact: ${artifact.filename}`}
                >
                  <p className="font-mono text-xs text-[#F0F0FF] truncate">
                    {artifact.filename}
                  </p>
                  <p className="font-mono text-[10px] text-[#8888AA]">
                    {formatDate(artifact.modified_at)} · {formatSize(artifact.size_bytes)}
                  </p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
