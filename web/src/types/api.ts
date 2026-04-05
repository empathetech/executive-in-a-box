/**
 * API response types — kept in sync with Python schemas in server/routes/.
 * Reference: hacky-hours/02-design/decisions/2026-04-04-package-structure.md
 */

// ---- Config ----

export interface ArchetypeInfo {
  slug: string
  name: string
  one_line: string
  traits: Record<string, number>       // personality trait scores, 0.0–1.0
  response_style_blurb: string         // short UI description of output style
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
  modification_context?: {
    original_position: string
    feedback: string
  }
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
  artifact?: { filename: string; content: string } | null
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

export interface SlackChannel {
  id: string
  workspace: string
  channel: string
}

export interface AnnounceRequest {
  message: string
  webhook_id: string
  archetype_slug?: string
}

// ---- Session History ----

export interface SessionRecord {
  id: string
  slug: string
  timestamp: string
  decision: string
  question: string
  position: string
  confidence: string
  ambition_level: string
  modification: string
}

// ---- Feedback ----

export interface FeedbackResponse {
  slug: string
  summary: string | null
  trait_adjustments: Record<string, number>
  system_prompt_addon: string | null
  updated_at: string | null
  decision_count: number
  active: boolean   // true = inject system_prompt_addon into LLM requests
}

// ---- Integrations ----

export interface LlmProvider {
  slug: string
  label: string
  needs_key: boolean
  key_set: boolean
  active: boolean
}

// ---- Stats ----

export interface DecisionRecord {
  timestamp: string
  archetype: string
  question: string
  position: string
  decision: 'Adopted' | 'Rejected' | 'Modified'
  modification: string
  confidence: 'low' | 'medium' | 'high'
  ambition_level: string
}

export interface CeoStats {
  slug: string
  name: string
  total: number
  adopted: number
  rejected: number
  modified: number
  agreement_rate: number
  modification_rate: number
  rejection_rate: number
  avg_confidence: number
  avg_ambition: number
  usage_share: number
  recent_decisions: DecisionRecord[]
}

export interface StatsResponse {
  ceos: CeoStats[]
  total_sessions: number
}
