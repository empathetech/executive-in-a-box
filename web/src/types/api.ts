/**
 * API response types — kept in sync with Python schemas in server/routes/.
 * Reference: hacky-hours/02-design/decisions/2026-04-04-package-structure.md
 */

// ---- Config ----

export interface ArchetypeInfo {
  slug: string
  name: string
  one_line: string
}

export interface ConfigResponse {
  archetype_slug: string
  archetype_name: string
  provider_name: string
  autonomy_level: 1 | 2 | 3 | 4
  api_key_set: boolean
  slack_configured: boolean
  archetypes: ArchetypeInfo[]
}

// ---- Session ----

export interface MessageRequest {
  message: string
  archetype_slug?: string
  executize?: boolean
}

export interface SessionResponse {
  valid: boolean
  archetype: string
  position: string
  reasoning: string
  confidence: 'low' | 'medium' | 'high'
  ambition_level: 'very_cautious' | 'cautious' | 'moderate' | 'ambitious' | 'very_ambitious'
  pros: string[]
  cons: string[]
  flags: string[]
  questions_for_user: string[]
  model: string
  input_tokens: number
  output_tokens: number
  secret_warnings: number
  // Populated when executize=true
  job_id?: string
  status?: 'queued' | 'running' | 'complete' | 'failed'
}

// ---- Jobs ----

export type JobStatus = 'queued' | 'running' | 'complete' | 'failed'

export interface Job {
  id: string
  archetype: string
  prompt: string
  status: JobStatus
  created_at: string
  updated_at: string
  result: string | null
  error: string | null
}

// ---- Artifacts ----

export interface ArtifactMeta {
  id: string
  session_id: string
  filename: string
  size_bytes: number
  modified_at: string
}

export interface ArtifactDetail extends ArtifactMeta {
  content: string
}

// ---- Slack ----

export interface AnnounceRequest {
  message: string
  archetype_slug?: string
}
