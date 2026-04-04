/**
 * Pure SVG radar chart showing CEO archetype personality profiles.
 *
 * Six axes (all normalized 0–1, defined in archetypes.py TRAIT_LABELS):
 *   Risk Appetite    — bold/risky vs. cautious/safe
 *   People Focus     — human/equity lens vs. operational/metric lens
 *   Long-term Horizon— 2+ year vision vs. immediate execution
 *   Innovation Drive — disrupt/reframe vs. optimize existing
 *   Data Reliance    — evidence/quantification vs. intuition/values
 *   Decisiveness     — commits clearly vs. hedges or requests more info
 *
 * Scores are static personality traits baked into each archetype definition,
 * not derived from session history.
 *
 * Reference: hacky-hours/02-design/STYLE_GUIDE.md § CRT Panel Treatment
 */

import type { ArchetypeInfo } from '../types/api'

// Neon color per archetype slug
const CEO_COLORS: Record<string, string> = {
  operator:  '#00F5FF',  // electric cyan
  visionary: '#FF2D78',  // hot magenta
  advocate:  '#7FFF00',  // lime zap
  analyst:   '#FFE600',  // solar yellow
}

// Axis order must match archetypes.py TRAIT_LABELS
const AXES = [
  'Risk Appetite',
  'People Focus',
  'Long-term Horizon',
  'Innovation Drive',
  'Data Reliance',
  'Decisiveness',
] as const

// Short labels for display (space is tight at w-72)
const AXIS_SHORT: Record<string, string> = {
  'Risk Appetite':     'Risk',
  'People Focus':      'People',
  'Long-term Horizon': 'Horizon',
  'Innovation Drive':  'Innovation',
  'Data Reliance':     'Data',
  'Decisiveness':      'Decisiveness',
}

const N = AXES.length
const CX = 105
const CY = 110
const R  = 72
const LABEL_R = 92

function axisAngle(i: number): number {
  return (-Math.PI / 2) + (2 * Math.PI * i) / N
}

function polar(r: number, angle: number): [number, number] {
  return [CX + r * Math.cos(angle), CY + r * Math.sin(angle)]
}

function buildPolygon(archetype: ArchetypeInfo): string {
  return AXES.map((axis, i) => {
    const v = Math.max(0, Math.min(1, archetype.traits[axis] ?? 0))
    const [x, y] = polar(R * v, axisAngle(i))
    return `${x},${y}`
  }).join(' ')
}

interface Props {
  archetypes: ArchetypeInfo[]
}

export function RadarChart({ archetypes }: Props) {
  return (
    <div className="flex flex-col items-center gap-2">
      <svg
        viewBox="0 0 210 220"
        className="w-full max-w-[230px]"
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
            <line
              key={i}
              x1={CX}
              y1={CY}
              x2={x}
              y2={y}
              stroke="#2A2A44"
              strokeWidth={0.5}
            />
          )
        })}

        {/* CEO polygons — render all, dimmed if no traits */}
        {archetypes.map((arch) => {
          const color = CEO_COLORS[arch.slug] ?? '#8888AA'
          const hasTraits = Object.keys(arch.traits).length > 0
          return (
            <polygon
              key={arch.slug}
              points={buildPolygon(arch)}
              fill={color}
              fillOpacity={hasTraits ? 0.10 : 0}
              stroke={color}
              strokeWidth={1.5}
              strokeOpacity={hasTraits ? 0.80 : 0.15}
            />
          )
        })}

        {/* Axis labels */}
        {AXES.map((axis, i) => {
          const angle = axisAngle(i)
          const [lx, ly] = polar(LABEL_R, angle)
          const cosA = Math.cos(angle)
          const anchor =
            Math.abs(cosA) < 0.2 ? 'middle' : cosA > 0 ? 'start' : 'end'

          return (
            <text
              key={axis}
              x={lx}
              y={ly + 3}
              textAnchor={anchor}
              fontSize={6.5}
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

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-x-3 gap-y-1">
        {archetypes.map((arch) => {
          const color = CEO_COLORS[arch.slug] ?? '#8888AA'
          return (
            <div key={arch.slug} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
              <span className="font-mono text-[9px]" style={{ color }}>
                {arch.name.replace('The ', '')}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
