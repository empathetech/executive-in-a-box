/**
 * Full-screen artifact viewer modal.
 * Supports maximize (true fullscreen) toggle and keyboard dismiss (Escape).
 */

import { useEffect, useState } from 'react'
import type { ArtifactMeta } from '../types/api'
import { getArtifact } from '../lib/api'

interface Props {
  artifact: ArtifactMeta
  onClose: () => void
}

export function ArtifactModal({ artifact, onClose }: Props) {
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [maximized, setMaximized] = useState(false)

  useEffect(() => {
    setLoading(true)
    getArtifact(artifact.session_id, artifact.filename)
      .then((r) => setContent(r.content))
      .catch(() => setContent('Failed to load artifact.'))
      .finally(() => setLoading(false))
  }, [artifact.id])

  // Dismiss on Escape
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  const panelClass = maximized
    ? 'fixed inset-0 z-50 flex flex-col bg-[#0D0D15] border border-[#2A2A44]'
    : 'fixed inset-0 z-50 flex items-center justify-center bg-black/70'

  return (
    <div className={panelClass} role="dialog" aria-modal="true" aria-label={artifact.filename}>
      {maximized ? (
        // Full-screen: panel IS the modal
        <ModalContent
          artifact={artifact}
          content={content}
          loading={loading}
          maximized={maximized}
          onToggleMaximize={() => setMaximized(false)}
          onClose={onClose}
        />
      ) : (
        // Centered card: click backdrop to close
        <>
          <div
            className="absolute inset-0"
            onClick={onClose}
            aria-hidden="true"
          />
          <div className="relative w-full max-w-3xl mx-4 flex flex-col bg-[#0D0D15] border border-[#2A2A44] rounded overflow-hidden"
            style={{ maxHeight: '85vh' }}
          >
            <ModalContent
              artifact={artifact}
              content={content}
              loading={loading}
              maximized={maximized}
              onToggleMaximize={() => setMaximized(true)}
              onClose={onClose}
            />
          </div>
        </>
      )}
    </div>
  )
}

interface ContentProps {
  artifact: ArtifactMeta
  content: string | null
  loading: boolean
  maximized: boolean
  onToggleMaximize: () => void
  onClose: () => void
}

function ModalContent({ artifact, content, loading, maximized, onToggleMaximize, onClose }: ContentProps) {
  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#2A2A44] flex-shrink-0">
        <h2 className="font-mono text-sm text-[#00F5FF] tracking-widest uppercase truncate flex-1 mr-4">
          {artifact.filename}
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleMaximize}
            className="text-[#8888AA] hover:text-[#F0F0FF] font-mono text-sm transition-colors px-1"
            aria-label={maximized ? 'Restore' : 'Maximize'}
            title={maximized ? 'Restore (Esc)' : 'Maximize'}
          >
            {maximized ? '⊡' : '⊞'}
          </button>
          <button
            onClick={onClose}
            className="text-[#8888AA] hover:text-[#F0F0FF] font-mono text-sm transition-colors px-1"
            aria-label="Close"
            title="Close (Esc)"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <p className="text-[#8888AA] font-mono text-xs animate-pulse">Loading...</p>
        ) : (
          <pre className="font-mono text-sm text-[#F0F0FF] whitespace-pre-wrap leading-relaxed">
            {content}
          </pre>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-[#2A2A44] flex-shrink-0">
        <p className="font-mono text-[10px] text-[#8888AA]">
          Stored at: <span className="text-[#F0F0FF]">~/.executive-in-a-box/artifacts/…/{artifact.filename}</span>
        </p>
      </div>
    </>
  )
}
