/**
 * Thin API client — wraps fetch calls to the FastAPI backend.
 * All requests go to /api/* (proxied to FastAPI in dev, served by FastAPI in prod).
 */

import type {
  AnnounceRequest,
  ArtifactDetail,
  ArtifactMeta,
  ArchetypeInfo as _ArchetypeInfo,
  ConfigResponse,
  Job,
  MessageRequest,
  SessionResponse,
  SlackChannel,
  StatsResponse,
} from '../types/api'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error((body as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

// ---- Config ----

export const getConfig = () => request<ConfigResponse>('/config')

export const setAutonomy = (level: number) =>
  request('/config/autonomy', {
    method: 'POST',
    body: JSON.stringify({ level }),
  })

export const setArchetype = (slug: string) =>
  request('/config/archetype', {
    method: 'POST',
    body: JSON.stringify({ slug }),
  })

// ---- Session ----

export const sendMessage = (body: MessageRequest) =>
  request<SessionResponse>('/session/message', {
    method: 'POST',
    body: JSON.stringify(body),
  })

// ---- Jobs ----

export const listJobs = () =>
  request<{ jobs: Job[] }>('/jobs').then((r) => r.jobs)

export const getJob = (id: string) => request<Job>(`/jobs/${id}`)

export const cancelJob = (id: string) =>
  request<{ cancelled: boolean }>(`/jobs/${id}`, { method: 'DELETE' })

/** Subscribe to SSE job state events. Returns a cleanup function. */
export function subscribeToJob(
  jobId: string,
  onState: (job: Job) => void,
  onError: (msg: string) => void,
): () => void {
  const es = new EventSource(`/api/stream/jobs/${jobId}`)
  es.addEventListener('state', (e: MessageEvent<string>) => {
    const job = JSON.parse(e.data) as Job
    onState(job)
  })
  es.addEventListener('error', (e: MessageEvent<string>) => {
    const data = JSON.parse(e.data) as { error: string }
    onError(data.error)
    es.close()
  })
  es.onerror = () => {
    es.close()
  }
  return () => es.close()
}

// ---- Artifacts ----

export const listArtifacts = () =>
  request<{ artifacts: ArtifactMeta[] }>('/artifacts').then((r) => r.artifacts)

export const getArtifact = (sessionId: string, filename: string) =>
  request<ArtifactDetail>(`/artifacts/${sessionId}/${filename}`)

export const deleteArtifact = (sessionId: string, filename: string) =>
  request<{ deleted: boolean }>(`/artifacts/${sessionId}/${filename}`, { method: 'DELETE' })

export const revealArtifact = (sessionId: string, filename: string) =>
  request<{ revealed: boolean }>(`/artifacts/${sessionId}/${filename}/reveal`, { method: 'POST' })

export const createArtifact = (body: {
  session_id?: string
  filename: string
  content: string
}) =>
  request<{ id: string; session_id: string; filename: string }>('/artifacts', {
    method: 'POST',
    body: JSON.stringify(body),
  })

// ---- Stats ----

export const getStats = () => request<StatsResponse>('/stats')

// ---- Slack ----

export const getSlackChannels = () =>
  request<{ channels: SlackChannel[] }>('/slack/channels').then((r) => r.channels)

export const getSlackDefault = () =>
  request<{ default_webhook_id: string | null }>('/slack/default').then((r) => r.default_webhook_id)

export const setSlackDefault = (webhook_id: string) =>
  request<{ default_webhook_id: string }>('/slack/default', {
    method: 'POST',
    body: JSON.stringify({ webhook_id }),
  })

export const sendSlack = (body: AnnounceRequest) =>
  request<{ sent: boolean }>('/slack/announce', {
    method: 'POST',
    body: JSON.stringify(body),
  })

// ---- Feedback ----

export const getFeedback = (slug: string) =>
  request<import('../types/api').FeedbackResponse>(`/feedback/${slug}`)

export const refreshFeedback = (slug: string) =>
  request<import('../types/api').FeedbackResponse>(`/feedback/${slug}/refresh`, { method: 'POST' })

export const clearFeedback = (slug: string) =>
  request<{ cleared: boolean }>(`/feedback/${slug}`, { method: 'DELETE' })

export const setFeedbackActive = (slug: string, active: boolean) =>
  request<import('../types/api').FeedbackResponse>(`/feedback/${slug}/active`, {
    method: 'POST',
    body: JSON.stringify({ active }),
  })

// ---- Session History ----

export const listSessions = () =>
  request<{ sessions: import('../types/api').SessionRecord[] }>('/sessions').then((r) => r.sessions)

// ---- Integrations ----

export const getLlmProviders = () =>
  request<{ providers: Array<{ slug: string; label: string; needs_key: boolean; key_set: boolean; active: boolean }> }>('/integrations/llm').then((r) => r.providers)

export const setActiveProvider = (provider: string) =>
  request<{ active: string }>('/integrations/llm/active', {
    method: 'POST',
    body: JSON.stringify({ provider }),
  })

// ---- Decisions ----

export const sendDecision = (body: {
  archetype_slug: string
  question: string
  position: string
  confidence: string
  ambition_level: string
  decision: string
  modification?: string
  reason?: string
  is_modification?: boolean
}) =>
  request<{ recorded: boolean }>('/session/decision', {
    method: 'POST',
    body: JSON.stringify(body),
  })
