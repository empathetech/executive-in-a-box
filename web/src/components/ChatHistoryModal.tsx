/**
 * Chat History Modal — shows a single assistant message in full detail.
 * Includes position, reasoning, pros/cons/flags, and decision record.
 */

import { useEffect } from 'react'
import type { ChatMessage } from '../App'

interface Props {
  msg: ChatMessage
  ceoName: string
  accentColor: string
  onClose: () => void
}

export function ChatHistoryModal({ msg, ceoName, accentColor, onClose }: Props) {
  // Dismiss on Escape
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onClose])

  const r = msg.response

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
      role="dialog"
      aria-modal="true"
      aria-label="CEO response detail"
    >
      {/* Backdrop */}
      <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />

      {/* Modal card */}
      <div
        className="relative w-full max-w-2xl mx-4 flex flex-col bg-[#0D0D15] border rounded overflow-hidden"
        style={{ maxHeight: '85vh', borderColor: `${accentColor}66` }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#2A2A44] flex-shrink-0">
          <h2 className="font-mono text-sm tracking-widest uppercase" style={{ color: accentColor }}>
            {ceoName}
          </h2>
          <button
            onClick={onClose}
            className="text-[#8888AA] hover:text-[#F0F0FF] font-mono text-sm transition-colors px-1"
            aria-label="Close"
            title="Close (Esc)"
          >
            ✕
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-sm">
          {r ? (
            <>
              {/* Position */}
              <section>
                <p className="text-[9px] tracking-widest uppercase text-[#8888AA] mb-1">Position</p>
                <p className="text-[#F0F0FF] leading-relaxed whitespace-pre-wrap">{r.position}</p>
              </section>

              {/* Reasoning */}
              {r.reasoning && (
                <section>
                  <p className="text-[9px] tracking-widest uppercase text-[#8888AA] mb-1">Reasoning</p>
                  <p className="text-[#F0F0FF] leading-relaxed whitespace-pre-wrap">{r.reasoning}</p>
                </section>
              )}

              {/* Pros */}
              {r.pros.length > 0 && (
                <section>
                  <p className="text-[9px] tracking-widest uppercase text-[#8888AA] mb-1">Pros</p>
                  <ul className="space-y-0.5">
                    {r.pros.map((p, i) => (
                      <li key={i} className="text-[#7FFF00] text-xs">+ {p}</li>
                    ))}
                  </ul>
                </section>
              )}

              {/* Cons */}
              {r.cons.length > 0 && (
                <section>
                  <p className="text-[9px] tracking-widest uppercase text-[#8888AA] mb-1">Cons</p>
                  <ul className="space-y-0.5">
                    {r.cons.map((c, i) => (
                      <li key={i} className="text-[#FF2D78] text-xs">– {c}</li>
                    ))}
                  </ul>
                </section>
              )}

              {/* Flags */}
              {r.flags.length > 0 && (
                <section>
                  <p className="text-[9px] tracking-widest uppercase text-[#8888AA] mb-1">Flags</p>
                  <ul className="space-y-0.5">
                    {r.flags.map((f, i) => (
                      <li key={i} className="text-[#FFE600] text-xs">⚠ {f}</li>
                    ))}
                  </ul>
                </section>
              )}

              {/* Metadata */}
              <div className="pt-2 border-t border-[#2A2A44] text-[10px] text-[#8888AA] flex gap-4">
                <span>{r.model}</span>
                <span>{r.input_tokens + r.output_tokens} tokens</span>
                <span>confidence: {r.confidence}</span>
              </div>
            </>
          ) : (
            <p className="text-[#F0F0FF] whitespace-pre-wrap leading-relaxed">{msg.content}</p>
          )}

          {/* Decision */}
          <section className="pt-2 border-t border-[#2A2A44]">
            <p className="text-[9px] tracking-widest uppercase text-[#8888AA] mb-1">Decision</p>
            {msg.decision === 'adopted' && (
              <p className="text-[#7FFF00] text-xs">✓ Adopted</p>
            )}
            {msg.decision === 'rejected' && (
              <p className="text-[#FF2D78] text-xs">✗ Rejected</p>
            )}
            {msg.decision === 'modified' && (
              <p className="text-[#FFE600] text-xs">~ Modified{msg.modification ? `: ${msg.modification}` : ''}</p>
            )}
            {!msg.decision && (
              <p className="text-[#444466] text-xs">(no decision recorded)</p>
            )}
          </section>
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-[#2A2A44] flex-shrink-0">
          <p className="font-mono text-[10px] text-[#444466]">{msg.timestamp}</p>
        </div>
      </div>
    </div>
  )
}
