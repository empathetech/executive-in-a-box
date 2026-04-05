/**
 * Pure SVG radar chart showing CEO archetype personality profiles.
 *
 * When feedback adjustments exist, BOTH polygons are always visible:
 *   - Baseline: archetype color, dimmed/dashed
 *   - Adjusted: complementary color, solid/bright
 *
 * The toggle button switches which personality the LLM uses for future
 * requests (active = adjusted, inactive = baseline). Defaults to adjusted.
 *
 * Six axes (0–1, defined in archetypes.py TRAIT_LABELS):
 *   Risk Appetite, People Focus, Long-term Horizon,
 *   Innovation Drive, Data Reliance, Decisiveness
 */

import type { ArchetypeInfo } from '../types/api'

// Per-archetype complementary color for the adjusted overlay
const CEO_COLORS: Record<string, string> = {
  operator:  '#FF2D78',
  visionary: '#8B5CF6',
  advocate:  '#7FFF00',
  analyst:   '#00F5FF',
}

const ADJUSTED_COLORS: Record<string, string> = {
  operator:  '#FFE600',   // yellow on pink
  visionary: '#00F5FF',   // cyan on purple
  advocate:  '#FF2D78',   // pink on green (high contrast)
  analyst:   '#FFE600',   // yellow on cyan
}

const AXES = [
  'Risk Appetite',
  'People Focus',
  'Long-term Horizon',
  'Innovation Drive',
  'Data Reliance',
  'Decisiveness',
] as const

const AXIS_SHORT: Record<string, string> = {
  'Risk Appetite':     'RISK',
  'People Focus':      'PEOPLE',
  'Long-term Horizon': 'HORIZON',
  'Innovation Drive':  'DRIVE',
  'Data Reliance':     'DATA',
  'Decisiveness':      'DECISIVE',
}

const N = AXES.length
// Generous viewBox so bold uppercase labels never clip at any axis angle.
// Left axis (DECISIVE, ~210°): label right-edge at x≈54, starts at x≈14 ✓
// Right axis (HORIZON/PEOPLE, ~30°): label left-edge at x≈266, ends at x≈301 ✓
const CX = 160
const CY = 145
const R  = 85
const LABEL_R = 122

function axisAngle(i: number): number {
  return (-Math.PI / 2) + (2 * Math.PI * i) / N
}

function polar(r: number, angle: number): [number, number] {
  return [CX + r * Math.cos(angle), CY + r * Math.sin(angle)]
}

function buildPolygonPoints(traits: Record<string, number>): string {
  return AXES.map((axis, i) => {
    const v = Math.max(0, Math.min(1, traits[axis] ?? 0))
    const [x, y] = polar(R * v, axisAngle(i))
    return `${x},${y}`
  }).join(' ')
}

function adjustedTraits(
  base: Record<string, number>,
  adjustments: Record<string, number>
): Record<string, number> {
  const result: Record<string, number> = {}
  for (const axis of AXES) {
    result[axis] = Math.max(0, Math.min(1, (base[axis] ?? 0) + (adjustments[axis] ?? 0)))
  }
  return result
}

interface Props {
  archetypes: ArchetypeInfo[]
  traitAdjustments?: Record<string, number>  // delta values from feedback
  isAdjustedActive: boolean                  // true = LLM uses adjusted personality
  onToggleActive: () => void                 // flip which personality the LLM uses
}

export function RadarChart({ archetypes, traitAdjustments, isAdjustedActive, onToggleActive }: Props) {
  const hasAdjustments = traitAdjustments != null &&
    Object.values(traitAdjustments).some(v => Math.abs(v) > 0.001)

  return (
    <div className="flex flex-col items-center gap-1 w-full">
      <svg
        viewBox="0 0 320 290"
        className="w-full max-w-[220px]"
        aria-label="CEO personality profile radar chart"
        role="img"
      >
        {/* Grid rings at 25%, 50%, 75%, 100% */}
        {[0.25, 0.5, 0.75, 1.0].map((t) => (
          <polygon
            key={t}
            points={Array.from({ length: N }, (_, i) => {
              const [x, y] = polar(R * t, axisAngle(i))
              return `${x},${y}`
            }).join(' ')}
            fill="none"
            stroke="#2A2A44"
            strokeWidth={t === 1.0 ? 1 : 0.5}
          />
        ))}

        {/* Axis spokes */}
        {AXES.map((_, i) => {
          const [x, y] = polar(R, axisAngle(i))
          return (
            <line key={i} x1={CX} y1={CY} x2={x} y2={y} stroke="#2A2A44" strokeWidth={0.5} />
          )
        })}

        {/* Baseline polygons — dimmed/dashed when adjusted is the active mode */}
        {archetypes.map((arch) => {
          const color = CEO_COLORS[arch.slug] ?? '#8888AA'
          const hasTraits = Object.keys(arch.traits).length > 0
          const dimmed = hasAdjustments && isAdjustedActive
          return (
            <polygon
              key={`base-${arch.slug}`}
              points={buildPolygonPoints(arch.traits)}
              fill={color}
              fillOpacity={hasTraits ? (dimmed ? 0.04 : 0.14) : 0}
              stroke={color}
              strokeWidth={dimmed ? 1 : 1.5}
              strokeOpacity={hasTraits ? (dimmed ? 0.25 : 0.85) : 0.15}
              strokeDasharray={dimmed ? '4 3' : undefined}
            />
          )
        })}

        {/* Adjusted overlay — always visible when adjustments exist */}
        {hasAdjustments && archetypes.map((arch) => {
          const adjColor = ADJUSTED_COLORS[arch.slug] ?? '#FFE600'
          const adj = adjustedTraits(arch.traits, traitAdjustments!)
          const active = isAdjustedActive
          return (
            <polygon
              key={`adj-${arch.slug}`}
              points={buildPolygonPoints(adj)}
              fill={adjColor}
              fillOpacity={active ? 0.15 : 0.04}
              stroke={adjColor}
              strokeWidth={active ? 2 : 1}
              strokeOpacity={active ? 0.95 : 0.25}
              strokeDasharray={active ? undefined : '4 3'}
            />
          )
        })}

        {/* Axis labels — uppercase bold, generous spacing prevents clipping */}
        {AXES.map((axis, i) => {
          const angle = axisAngle(i)
          const [lx, ly] = polar(LABEL_R, angle)
          const cosA = Math.cos(angle)
          const anchor: 'middle' | 'start' | 'end' =
            Math.abs(cosA) < 0.25 ? 'middle' : cosA > 0 ? 'start' : 'end'

          return (
            <text
              key={axis}
              x={lx}
              y={ly + 3}
              textAnchor={anchor}
              fontSize={8}
              fontWeight="bold"
              fill="#8888AA"
              fontFamily="monospace"
            >
              {AXIS_SHORT[axis]}
            </text>
          )
        })}

        {/* Center dot */}
        <circle cx={CX} cy={CY} r={1.5} fill="#2A2A44" />
      </svg>

      {/* Toggle — only shown when feedback adjustments exist */}
      {hasAdjustments && (
        <button
          onClick={onToggleActive}
          className={[
            'font-mono text-[9px] px-2 py-0.5 rounded border transition-colors',
            isAdjustedActive
              ? 'border-[#FFE600] text-[#FFE600] bg-[#FFE60011]'
              : 'border-[#2A2A44] text-[#8888AA] hover:text-[#F0F0FF]',
          ].join(' ')}
          title={isAdjustedActive
            ? 'LLM using adjusted personality — click to revert to baseline'
            : 'LLM using baseline personality — click to use adjusted'}
        >
          {isAdjustedActive ? '◈ Adjusted Active' : '◇ Baseline Active'}
        </button>
      )}
    </div>
  )
}
