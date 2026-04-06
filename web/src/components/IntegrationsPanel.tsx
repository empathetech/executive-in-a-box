/**
 * IntegrationsPanel — LLM stats + provider selector, and Slack webhook selector.
 *
 * Credentials (API keys, webhook URLs) are write-only via the CLI to avoid
 * raw secrets travelling over HTTP. The web UI can read status and switch
 * between already-configured integrations.
 */

import { useEffect, useState } from 'react'
import type { SlackChannel } from '../types/api'
import { getLlmProviders, setActiveProvider, getSlackChannels, getSlackDefault, setSlackDefault } from '../lib/api'

type LlmProvider = { slug: string; label: string; needs_key: boolean; key_set: boolean; active: boolean }
type Tab = 'llm' | 'slack'

// ---- LLM Tab ----

interface LlmTabProps {
  accentColor: string
  currentModel: string | null
  sessionTokens: number
  providerName: string
  apiKeySet: boolean
}

function LlmTab({ accentColor, currentModel, sessionTokens, providerName, apiKeySet }: LlmTabProps) {
  const [providers, setProviders] = useState<LlmProvider[]>([])
  const [error, setError] = useState<string | null>(null)

  const reload = () => getLlmProviders().then(setProviders).catch(() => {})
  useEffect(() => { reload() }, [])

  async function handleSetActive(slug: string) {
    setError(null)
    try {
      await setActiveProvider(slug)
      reload()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to switch provider')
    }
  }

  const multipleConfigured = providers.filter(p => p.key_set || !p.needs_key).length > 1

  return (
    <div className="flex flex-col h-full overflow-y-auto gap-2 pr-0.5">

      {/* Current session stats */}
      <div className="font-mono space-y-1.5">
        <div>
          <p className="text-[#8888AA] text-[10px]">Provider</p>
          <p className="text-[#F0F0FF] text-xs">{providerName}</p>
        </div>
        <div>
          <p className="text-[#8888AA] text-[10px]">Model</p>
          <p className="text-[#F0F0FF] text-xs truncate" title={currentModel ?? undefined}>
            {currentModel ?? <span className="text-[#444466]">—</span>}
          </p>
        </div>
        <div>
          <p className="text-[#8888AA] text-[10px]">Session tokens</p>
          <p className="text-[#F0F0FF] text-xs">
            {sessionTokens > 0 ? sessionTokens.toLocaleString() : <span className="text-[#444466]">—</span>}
          </p>
        </div>
        <div>
          <p className="text-[#8888AA] text-[10px]">API key</p>
          <p className={`text-xs ${apiKeySet ? 'text-[#7FFF00]' : 'text-[#FF2D78]'}`}>
            {apiKeySet ? '✓ set' : '✗ missing'}
          </p>
        </div>
      </div>

      {/* Provider selector — only shown when multiple are available */}
      {multipleConfigured && (
        <div className="border-t border-[#2A2A44] pt-1.5">
          <p className="font-mono text-[9px] text-[#8888AA] uppercase tracking-widest mb-1">Switch</p>
          {error && <p className="font-mono text-[10px] text-[#FF2D78] mb-1">{error}</p>}
          <div className="flex flex-col gap-1">
            {providers.filter(p => p.key_set || !p.needs_key).map((p) => (
              <button
                key={p.slug}
                onClick={() => !p.active && void handleSetActive(p.slug)}
                disabled={p.active}
                className={[
                  'flex items-center justify-between w-full rounded border px-1.5 py-1 font-mono text-[10px] transition-colors text-left',
                  p.active
                    ? 'border-[#2A2A44] bg-[#1A1A2E] cursor-default'
                    : 'border-[#1E1E30] text-[#8888AA] hover:text-[#F0F0FF] hover:border-[#00F5FF]',
                ].join(' ')}
              >
                <span style={{ color: p.active ? accentColor : undefined }}>{p.label}</span>
                {p.active && (
                  <span className="text-[9px] px-1 rounded" style={{ background: `${accentColor}22`, color: accentColor }}>
                    active
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      <p className="font-mono text-[9px] text-[#444466] mt-auto leading-tight">
        Add keys: <span className="text-[#555577]">exec-in-a-box setup</span>
      </p>
    </div>
  )
}

// ---- Slack Tab ----

function SlackTab() {
  const [webhooks, setWebhooks] = useState<SlackChannel[]>([])
  const [defaultId, setDefaultId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const reload = () => {
    getSlackChannels().then(setWebhooks).catch(() => {})
    getSlackDefault().then(setDefaultId).catch(() => {})
  }
  useEffect(() => { reload() }, [])

  async function handleSetDefault(id: string) {
    setError(null)
    try {
      await setSlackDefault(id)
      setDefaultId(id)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to set default')
    }
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto gap-1.5 pr-0.5">
      {error && <p className="font-mono text-[10px] text-[#FF2D78]">{error}</p>}

      {webhooks.length === 0 ? (
        <p className="font-mono text-[10px] text-[#444466]">No webhooks configured.</p>
      ) : (
        <>
          <p className="font-mono text-[9px] text-[#8888AA] uppercase tracking-widest">Channels</p>
          {webhooks.map((w) => {
            const isDefault = w.id === defaultId
            return (
              <button
                key={w.id}
                onClick={() => !isDefault && void handleSetDefault(w.id)}
                disabled={isDefault}
                className={[
                  'w-full rounded border px-1.5 py-1 font-mono text-left transition-colors',
                  isDefault
                    ? 'border-[#2A2A44] bg-[#1A1A2E] cursor-default'
                    : 'border-[#1E1E30] hover:border-[#00F5FF]',
                ].join(' ')}
              >
                <div className="flex items-center justify-between gap-1">
                  <div className="min-w-0">
                    <p className="text-[10px] text-[#F0F0FF] truncate">{w.workspace}</p>
                    <p className="text-[9px] text-[#8888AA] truncate">{w.channel}</p>
                  </div>
                  {isDefault && (
                    <span className="text-[9px] px-1 rounded flex-shrink-0 bg-[#00F5FF22] text-[#00F5FF]">
                      default
                    </span>
                  )}
                </div>
              </button>
            )
          })}
        </>
      )}

      <p className="font-mono text-[9px] text-[#444466] mt-auto leading-tight">
        Add webhooks: <span className="text-[#555577]">exec-in-a-box slack setup</span>
      </p>
    </div>
  )
}

// ---- Panel ----

interface Props {
  accentColor: string
  currentModel: string | null
  sessionTokens: number
  providerName: string
  apiKeySet: boolean
}

export function IntegrationsPanel({ accentColor, currentModel, sessionTokens, providerName, apiKeySet }: Props) {
  const [tab, setTab] = useState<Tab>('llm')

  return (
    <div className="flex flex-col h-full">
      {/* Tab strip */}
      <div className="flex border-b border-[#2A2A44] flex-shrink-0 mb-1.5">
        {([['llm', 'LLMs'], ['slack', 'Slack']] as [Tab, string][]).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={[
              'flex-1 font-mono text-[9px] tracking-widest uppercase py-1 transition-colors',
              tab === key
                ? 'border-b border-[#00F5FF] text-[#00F5FF]'
                : 'text-[#8888AA] hover:text-[#F0F0FF]',
            ].join(' ')}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-hidden">
        {tab === 'llm' && (
          <LlmTab
            accentColor={accentColor}
            currentModel={currentModel}
            sessionTokens={sessionTokens}
            providerName={providerName}
            apiKeySet={apiKeySet}
          />
        )}
        {tab === 'slack' && <SlackTab />}
      </div>
    </div>
  )
}
