/**
 * CEO portrait strip — top bar showing all archetypes with active/Executizing states,
 * autonomy level toggles, and portrait switching.
 *
 * Reference: hacky-hours/02-design/ARCHITECTURE.md § Interface Layer — Web App
 */

import type { ArchetypeInfo } from '../types/api'
import type { CeoState } from '../App'
import { setAutonomy } from '../lib/api'

// Executizing verb bank per archetype (from STYLE_GUIDE.md)
const EXECUTIZING_VERB: Record<string, string> = {
  operator:  'Strategizing',
  visionary: 'Envisioning',
  advocate:  'Empathizing',
  analyst:   'Analyzing',
}

// Portrait background colors per archetype
const ARCHETYPE_COLORS: Record<string, string> = {
  operator:  '#FF2D78',
  visionary: '#8B5CF6',
  advocate:  '#7FFF00',
  analyst:   '#00F5FF',
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
  onSelectCeo: (slug: string) => void
  onSetAutonomy: (slug: string, level: 1 | 2 | 3 | 4) => void
}

export function CeoStrip({ archetypes, ceos, activeCeoSlug, onSelectCeo, onSetAutonomy }: Props) {
  return (
    <div
      className="flex items-stretch border-b border-[#2A2A44] bg-[#12121A] overflow-x-auto"
      style={{ minHeight: '96px' }}
      role="tablist"
      aria-label="CEO archetypes"
    >
      {archetypes.map((archetype) => {
        const ceo = ceos[archetype.slug]
        const isActive = archetype.slug === activeCeoSlug
        const isExecutizing = ceo?.activeJob != null && ceo.activeJob.status === 'running'
        const verb = EXECUTIZING_VERB[archetype.slug] ?? 'Thinking'
        const color = ARCHETYPE_COLORS[archetype.slug] ?? '#00F5FF'

        return (
          <div
            key={archetype.slug}
            className={[
              'flex flex-col items-center gap-1 px-4 py-2 cursor-pointer select-none transition-all duration-150 min-w-[120px]',
              isActive
                ? 'border-b-2 bg-[#1A1A2E]'
                : 'border-b-2 border-transparent hover:bg-[#16161E]',
            ].join(' ')}
            style={isActive ? { borderColor: color } : undefined}
            onClick={() => onSelectCeo(archetype.slug)}
            title={archetype.response_style_blurb}
            role="tab"
            aria-selected={isActive}
            aria-label={`${archetype.name} — ${archetype.response_style_blurb}`}
          >
            {/* Portrait image */}
            <div
              className={[
                'w-12 h-12 rounded-full overflow-hidden flex-shrink-0 transition-opacity',
                isExecutizing ? 'opacity-40' : 'opacity-100',
              ].join(' ')}
              style={{ border: `2px solid ${color}` }}
              aria-hidden="true"
            >
              <img
                src={`/ceo-${archetype.slug}.png`}
                alt={archetype.name}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Name / Executizing state */}
            <div className="text-center">
              {isExecutizing ? (
                <p
                  className="font-mono text-xs animate-pulse"
                  style={{ color }}
                  aria-live="polite"
                  aria-label={`${archetype.name} is ${verb}`}
                >
                  {verb}...
                </p>
              ) : (
                <p
                  className="font-mono text-xs text-[#F0F0FF]"
                  aria-label={archetype.name}
                >
                  {archetype.name.replace('The ', '')}
                </p>
              )}
            </div>

            {/* Response style blurb — only shown for active CEO */}
            {isActive && (
              <p
                className="font-mono text-[9px] text-center leading-tight max-w-[140px]"
                style={{ color: `${color}99` }}
              >
                {archetype.response_style_blurb}
              </p>
            )}

            {/* Autonomy toggles — only shown for active CEO */}
            {isActive && ceo && (
              <div className="flex gap-1 mt-1" role="group" aria-label="Autonomy level">
                {([1, 2, 3, 4] as const).map((level) => (
                  <button
                    key={level}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (level > 2) return // levels 3/4 not available yet
                      setAutonomy(level).then(() => onSetAutonomy(archetype.slug, level))
                    }}
                    disabled={level > 2}
                    title={`Level ${level}: ${AUTONOMY_LABELS[level]}${level > 2 ? ' (coming soon)' : ''}`}
                    aria-label={`Autonomy level ${level}: ${AUTONOMY_LABELS[level]}`}
                    aria-pressed={ceo.autonomyLevel === level}
                    className={[
                      'w-5 h-5 font-mono text-[10px] rounded transition-all',
                      ceo.autonomyLevel === level
                        ? 'text-[#0A0A0F] font-bold'
                        : level > 2
                        ? 'opacity-30 cursor-not-allowed text-[#8888AA] border border-[#2A2A44]'
                        : 'text-[#8888AA] border border-[#2A2A44] hover:border-[--electric-cyan]',
                    ].join(' ')}
                    style={
                      ceo.autonomyLevel === level
                        ? { background: color, borderColor: color }
                        : undefined
                    }
                  >
                    {level}
                  </button>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
