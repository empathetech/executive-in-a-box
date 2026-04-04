import { useEffect, useReducer } from 'react'
import type { ConfigResponse, Job, ArtifactMeta, SessionResponse } from './types/api'
import { getConfig } from './lib/api'
import { ArtifactPanel } from './components/ArtifactPanel'
import { ChatPanel } from './components/ChatPanel'
import { RightPanel } from './components/RightPanel'
import { CeoStrip } from './components/CeoStrip'
import { AnnounceModal } from './components/AnnounceModal'

// ---- State ----

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  response?: SessionResponse
  timestamp: string
}

export interface CeoState {
  slug: string
  history: ChatMessage[]
  autonomyLevel: 1 | 2 | 3 | 4
  activeJob: Job | null
}

interface AppState {
  config: ConfigResponse | null
  loading: boolean
  error: string | null
  activeCeoSlug: string
  ceos: Record<string, CeoState>
  artifacts: ArtifactMeta[]
  rightPane: 'dashboard' | 'artifact'
  selectedArtifact: ArtifactMeta | null
  announceOpen: boolean
}

type AppAction =
  | { type: 'SET_CONFIG'; config: ConfigResponse }
  | { type: 'SET_ERROR'; error: string }
  | { type: 'SET_ACTIVE_CEO'; slug: string }
  | { type: 'ADD_MESSAGE'; slug: string; message: ChatMessage }
  | { type: 'SET_JOB'; slug: string; job: Job | null }
  | { type: 'SET_ARTIFACTS'; artifacts: ArtifactMeta[] }
  | { type: 'SET_RIGHT_PANE'; pane: 'dashboard' | 'artifact'; artifact?: ArtifactMeta }
  | { type: 'SET_AUTONOMY'; slug: string; level: 1 | 2 | 3 | 4 }
  | { type: 'TOGGLE_ANNOUNCE' }

function buildCeoState(slug: string, autonomyLevel: 1 | 2 | 3 | 4 = 1): CeoState {
  return { slug, history: [], autonomyLevel, activeJob: null }
}

function reducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CONFIG': {
      const ceos: Record<string, CeoState> = {}
      for (const a of action.config.archetypes) {
        ceos[a.slug] = buildCeoState(
          a.slug,
          a.slug === action.config.archetype_slug
            ? (action.config.autonomy_level as 1 | 2 | 3 | 4)
            : 1,
        )
      }
      return {
        ...state,
        config: action.config,
        activeCeoSlug: action.config.archetype_slug,
        ceos,
        loading: false,
        error: null,
      }
    }
    case 'SET_ERROR':
      return { ...state, loading: false, error: action.error }
    case 'SET_ACTIVE_CEO':
      return { ...state, activeCeoSlug: action.slug }
    case 'ADD_MESSAGE': {
      const ceo = state.ceos[action.slug]
      if (!ceo) return state
      return {
        ...state,
        ceos: {
          ...state.ceos,
          [action.slug]: { ...ceo, history: [...ceo.history, action.message] },
        },
      }
    }
    case 'SET_JOB': {
      const ceo = state.ceos[action.slug]
      if (!ceo) return state
      return {
        ...state,
        ceos: {
          ...state.ceos,
          [action.slug]: { ...ceo, activeJob: action.job },
        },
      }
    }
    case 'SET_ARTIFACTS':
      return { ...state, artifacts: action.artifacts }
    case 'SET_RIGHT_PANE':
      return {
        ...state,
        rightPane: action.pane,
        selectedArtifact: action.artifact ?? state.selectedArtifact,
      }
    case 'SET_AUTONOMY': {
      const ceo = state.ceos[action.slug]
      if (!ceo) return state
      return {
        ...state,
        ceos: {
          ...state.ceos,
          [action.slug]: { ...ceo, autonomyLevel: action.level },
        },
      }
    }
    case 'TOGGLE_ANNOUNCE':
      return { ...state, announceOpen: !state.announceOpen }
    default:
      return state
  }
}

const initialState: AppState = {
  config: null,
  loading: true,
  error: null,
  activeCeoSlug: '',
  ceos: {},
  artifacts: [],
  rightPane: 'dashboard',
  selectedArtifact: null,
  announceOpen: false,
}

// ---- Component ----

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)

  useEffect(() => {
    getConfig()
      .then((config) => dispatch({ type: 'SET_CONFIG', config }))
      .catch((e: Error) => dispatch({ type: 'SET_ERROR', error: e.message }))
  }, [])

  if (state.loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="neon-cyan font-mono text-lg animate-pulse">
          Booting Executive in a Box...
        </p>
      </div>
    )
  }

  if (state.error || !state.config) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4 p-8">
        <h1 className="neon-magenta font-mono text-2xl">Connection Error</h1>
        <p className="text-[var(--text-muted)] font-mono text-sm max-w-md text-center">
          {state.error ?? 'Could not load configuration.'}
        </p>
        <p className="text-[var(--text-muted)] font-mono text-xs">
          Make sure the server is running:{' '}
          <code className="neon-cyan">exec-in-a-box web</code>
        </p>
      </div>
    )
  }

  const activeCeo = state.ceos[state.activeCeoSlug]

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#0A0A0F]">
      {/* Announce modal */}
      {state.announceOpen && (
        <AnnounceModal
          archetypes={state.config.archetypes}
          activeCeoSlug={state.activeCeoSlug}
          onClose={() => dispatch({ type: 'TOGGLE_ANNOUNCE' })}
        />
      )}

      {/* Top nav */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#2A2A44] bg-[#0A0A0F]">
        <h1 className="font-mono text-sm text-[#00F5FF] tracking-widest uppercase neon-cyan">
          Executive in a Box
        </h1>
        <button
          onClick={() => dispatch({ type: 'TOGGLE_ANNOUNCE' })}
          className="px-3 py-1 font-mono text-xs rounded border border-[#7FFF00] text-[#7FFF00] hover:shadow-lg transition-all"
          style={{ boxShadow: '0 0 6px #7FFF0033' }}
          aria-label="Open Slack announcement composer"
        >
          Announce ↗
        </button>
      </div>

      {/* CEO portrait strip */}
      <CeoStrip
        archetypes={state.config.archetypes}
        ceos={state.ceos}
        activeCeoSlug={state.activeCeoSlug}
        onSelectCeo={(slug) => dispatch({ type: 'SET_ACTIVE_CEO', slug })}
        onSetAutonomy={(slug, level) =>
          dispatch({ type: 'SET_AUTONOMY', slug, level })
        }
      />

      {/* Three-pane layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left pane — artifact explorer */}
        <ArtifactPanel
          artifacts={state.artifacts}
          onRefresh={(artifacts) => dispatch({ type: 'SET_ARTIFACTS', artifacts })}
          onOpen={(artifact) =>
            dispatch({ type: 'SET_RIGHT_PANE', pane: 'artifact', artifact })
          }
        />

        {/* Center pane — chat */}
        {activeCeo ? (
          <ChatPanel
            ceo={activeCeo}
            config={state.config}
            onMessage={(msg) =>
              dispatch({ type: 'ADD_MESSAGE', slug: activeCeo.slug, message: msg })
            }
            onJobChange={(job) =>
              dispatch({ type: 'SET_JOB', slug: activeCeo.slug, job })
            }
          />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-[#8888AA] font-mono">Select a CEO to begin.</p>
          </div>
        )}

        {/* Right pane — dashboard or artifact viewer */}
        <RightPanel
          mode={state.rightPane}
          artifact={state.selectedArtifact}
          config={state.config}
        />
      </div>
    </div>
  )
}
