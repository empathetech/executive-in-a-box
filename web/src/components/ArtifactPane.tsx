/**
 * Inline artifact split pane — shows alongside ChatPanel when artifacts are open.
 * Tabbed view for multiple open artifacts; Expand button launches ArtifactModal.
 */

import { useEffect, useState } from 'react'
import type { ArtifactMeta } from '../types/api'
import { getArtifact } from '../lib/api'

interface Props {
  openArtifacts: ArtifactMeta[]
  activeArtifactId: string | null
  onSetActive: (id: string) => void
  onClose: (id: string) => void
  onExpand: (artifact: ArtifactMeta) => void
}

export function ArtifactPane({ openArtifacts, activeArtifactId, onSetActive, onClose, onExpand }: Props) {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const activeArtifact = openArtifacts.find(a => a.id === activeArtifactId) ?? openArtifacts[0] ?? null

  useEffect(() => {
    if (!activeArtifact) {
      setContent(null)
      return
    }
    setLoading(true)
    setContent(null)
    getArtifact(activeArtifact.session_id, activeArtifact.filename)
      .then(r => setContent(r.content))
      .catch(() => setContent('Failed to load artifact.'))
      .finally(() => setLoading(false))
  }, [activeArtifact?.id])

  if (openArtifacts.length === 0) return null

  return (
    <div
      className="w-80 flex-shrink-0 flex flex-col border-l border-[#2A2A44] bg-[#0D0D15] overflow-hidden"
      role="complementary"
      aria-label="Artifact viewer"
    >
      {/* Tab bar */}
      <div className="flex items-center border-b border-[#2A2A44] bg-[#12121A] overflow-x-auto flex-shrink-0">
        {openArtifacts.map(artifact => (
          <div
            key={artifact.id}
            className={[
              'flex items-center gap-1 px-2 py-1.5 font-mono text-[10px] flex-shrink-0 cursor-pointer border-r border-[#2A2A44] transition-colors',
              artifact.id === activeArtifact?.id
                ? 'bg-[#0D0D15] text-[#00F5FF]'
                : 'text-[#8888AA] hover:text-[#F0F0FF] hover:bg-[#1A1A2E]',
            ].join(' ')}
            onClick={() => onSetActive(artifact.id)}
            role="tab"
            aria-selected={artifact.id === activeArtifact?.id}
          >
            <span className="truncate max-w-[80px]" title={artifact.filename}>
              {artifact.filename}
            </span>
            <button
              onClick={(e) => { e.stopPropagation(); onClose(artifact.id) }}
              className="text-[#444466] hover:text-[#FF2D78] transition-colors ml-1 flex-shrink-0"
              aria-label={`Close ${artifact.filename}`}
              title="Close"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Header with expand button */}
      {activeArtifact && (
        <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#2A2A44] flex-shrink-0 bg-[#12121A]">
          <span className="font-mono text-[10px] text-[#8888AA] truncate flex-1">
            {activeArtifact.filename}
          </span>
          <button
            onClick={() => onExpand(activeArtifact)}
            className="text-[#8888AA] hover:text-[#00F5FF] font-mono text-xs transition-colors ml-2 flex-shrink-0"
            aria-label="Expand to fullscreen"
            title="Expand"
          >
            ⊞
          </button>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto p-3">
        {loading ? (
          <p className="text-[#8888AA] font-mono text-xs animate-pulse">Loading...</p>
        ) : content !== null ? (
          <pre className="font-mono text-xs text-[#F0F0FF] whitespace-pre-wrap leading-relaxed">
            {content}
          </pre>
        ) : (
          <p className="text-[#444466] font-mono text-xs text-center mt-8">Select an artifact to view.</p>
        )}
      </div>
    </div>
  )
}
