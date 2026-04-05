# CLI ↔ Web Parity Tracker

This document is the authoritative record of feature parity between the web app and CLI.
Update it whenever you add, change, or remove a feature in either interface.

**Rule:** If a feature exists in one interface, it must exist in the other — unless it is
listed under *Intentional Divergences*. When in doubt, add it both places.

---

## Feature Parity Table

| Feature | CLI | Web | Notes |
|---------|-----|-----|-------|
| **Session / Chat** | | | |
| Ask a question → get CEO response | ✅ session loop | ✅ ChatPanel | |
| Adopt with optional reason | ✅ Y → reason prompt | ✅ DecisionBar reason-adopt phase | |
| Reject with optional reason | ✅ N → reason prompt | ✅ DecisionBar reason-reject phase | |
| Modify → LLM re-run → Y/N only | ✅ `_handle_modify_rerun` | ✅ DecisionBar feedback phase | |
| Show reasoning (How/H) | ✅ H option in decision loop | ✅ inline in ChatPanel response | |
| Decisions logged to decisions.md | ✅ `_log_decision` | ✅ `POST /api/session/decision` | |
| Decisions written to session index | ✅ `_save_session` | ✅ `POST /api/session/decision` | `reason`, `is_modification` fields |
| Feedback calibration injected | ✅ `_load_feedback` in session loop | ✅ `_run_llm` in server route | checks `active` flag |
| Show feedback-active notice at start | ✅ printed in `run_session` | ✅ "✓ Active" badge in ScorecardPanel | |
| CEO switching | ✅ `/switch` command | ✅ mini icon clicks in hero panel | |
| URL fetching in question | ✅ `extract_urls` | ✅ server-side | |
| Secret scanning | ✅ `scan_for_secrets` | ✅ server-side | |
| Executize (background deep work) | ✅ `/executize` command | ✅ Executize button in ChatPanel | |
| Job status polling | ✅ checked before each prompt | ✅ SSE stream in ChatPanel | CLI is poll-based |
| **Slack** | | | |
| Announce from session/decision | ✅ S option → `_send_to_slack` | ✅ Announce button → AnnounceModal | |
| Webhook selection when multiple | ✅ numbered list in `_send_to_slack` | ✅ workspace+channel dropdowns | |
| Default webhook pre-selected | ✅ highlighted in `_send_to_slack` | ✅ `getSlackDefault()` in AnnounceModal | |
| Preview before send | ✅ preview step in both flows | ✅ Preview button in AnnounceModal | |
| Edit message before send | ✅ E option in both flows | ✅ editable textarea in AnnounceModal | |
| Standalone announce command | ✅ `exec-in-a-box slack` | ✅ Announce button in DecisionBar | |
| Use last session's position | ✅ option 2 in `run_slack_command` (via session index) | ✅ prefilled from `response.position` | |
| Extract `<announce>` tags | ✅ `run_slack_command` step 3 hint | ✅ `matchAll` in DecisionBar | |
| Webhook setup | ✅ `exec-in-a-box slack setup` | ❌ read-only in Integrations panel | by design — keys via CLI only |
| **CEO Personality / Profile** | | | |
| Archetype name + one-liner | ✅ in `stats` command | ✅ hero panel profile column | |
| Response style blurb | ❌ not shown | ✅ hero panel profile column | add to `stats` / session header |
| Personality traits bar chart | ✅ `stats` command | ✅ RadarChart in hero panel | |
| Feedback trait adjustments display | ✅ `feedback show` (bar chart + ±delta per trait) | ✅ RadarChart adjusted overlay | visual equivalent exists |
| Baseline vs adjusted toggle | ✅ `feedback toggle` | ✅ toggle button below radar | |
| Autonomy level display | ✅ `config autonomy` + session header | ✅ autonomy buttons in hero panel | |
| Autonomy level change | ✅ `exec-in-a-box config autonomy` | ✅ autonomy buttons (levels 1–2) | |
| Provider / model display | ✅ session header + `config show` | ✅ Integrations panel | |
| Session token usage | ❌ not shown | ✅ Integrations panel | low priority |
| **Stats / Scorecard** | | | |
| Agreement rate % | ✅ `stats` command | ✅ ScorecardPanel Agreement tab | |
| Adopted / Modified / Rejected counts | ✅ `stats` command | ✅ ScorecardPanel Agreement tab | |
| Per-CEO usage share bar | ✅ `stats` command | ❌ not in web | CLI-only fine |
| Recent decisions list | ✅ `stats` command (last 3) | ❌ not surfaced in web | CLI-only fine |
| Executize job counts | ✅ `stats` command | ✅ Jobs tab in left panel | |
| **Feedback Loop** | | | |
| Synthesize feedback from decisions | ✅ `feedback refresh [slug]` | ✅ ↻ Update Feedback in ScorecardPanel | |
| View current feedback summary | ✅ `feedback show [slug]` | ✅ Feedback tab in ScorecardPanel | |
| Reset / clear feedback | ✅ `feedback reset [slug]` | ✅ ✕ Reset button in ScorecardPanel | |
| Toggle active/baseline | ✅ `feedback toggle [slug]` | ✅ toggle button below RadarChart | |
| Feedback active indicator | ✅ shown at session start | ✅ "✓ Active" badge in ScorecardPanel | |
| **History** | | | |
| View all-time sessions | ✅ `exec-in-a-box history` | ✅ History tab in left panel | |
| Decision color coding | ✅ ANSI colors by decision | ✅ colored text in history list | |
| Show reason inline | ✅ indented under entry | ✅ in SessionDetailModal | |
| Filter by decision type | ❌ no filter flag | ✅ filter buttons in History tab | add `--filter` flag |
| Detail view (full position/reasoning) | ❌ only shows question preview | ✅ SessionDetailModal | add `--id` flag |
| **Artifacts** | | | |
| List artifacts | ✅ `artifacts list` | ✅ Artifacts tab in left panel | |
| View artifact content | ✅ `artifacts open id/file` | ✅ artifact tab in ChatPanel | |
| Delete artifact | ❌ not implemented | ✅ ✕ Delete in Artifacts tab | add `artifacts delete` |
| Reveal in Finder / file manager | ❌ not implemented | ✅ 📂 Finder button | low priority |
| Fullscreen/expand | ❌ N/A (stdout) | ✅ expand button | intentional — stdout is the CLI equivalent |
| Auto-open on LLM creation | ✅ path printed after response | ✅ tab opens automatically | |
| **Configuration** | | | |
| View current config | ✅ `config show` | ✅ Integrations panel | |
| Change archetype | ✅ `config archetype` | ✅ mini CEO icons | |
| Change provider | ✅ `config provider` | ❌ read-only in Integrations panel | by design |
| Add API key | ✅ `config provider` | ❌ read-only (CLI hint shown) | by design |
| Test connection | ✅ `test-connection` | ❌ not exposed | CLI-only fine |

---

## Intentional Divergences

These features exist in only one interface **by design** and do not need to be ported.

| Feature | Where | Reason |
|---------|-------|--------|
| Credential input (API keys, webhooks) | CLI only | Security: keys must never travel over HTTP, even localhost |
| `all-hands` facilitation | CLI only | Multi-archetype deliberation flow; no web equivalent planned yet |
| `test-connection` | CLI only | Dev/ops utility |
| `dev` server command | CLI only | Dev utility |
| Radar chart visualization | Web only | Terminal equivalent is the trait bar chart in `stats` |
| CEO portrait images | Web only | Terminal equivalent is archetype name + color |
| SSE job streaming | Web only | CLI uses pre-prompt polling |
| Fullscreen artifact expand | Web only | CLI stdout is the equivalent |
| Session token count display | Web only | Low signal-to-noise in terminal |

---

## Known Gaps (prioritized)

### P1 — Fix now
| Gap | File to change |
|-----|----------------|
| `artifacts delete` command missing in CLI | `__main__.py` |
| `history --filter` flag missing in CLI | `__main__.py` |

### P2 — Fix soon
| Gap | File to change |
|-----|----------------|
| `response_style_blurb` not shown in CLI `stats` or session header | `__main__.py`, `cli_display.py` |
| `history --id` flag for full session detail view | `__main__.py` |

### P3 — Nice to have
| Gap | File to change |
|-----|----------------|
| Session token usage in CLI | `session.py`, `cli_display.py` |
| Web: per-CEO usage share bar | ScorecardPanel or StatsPage |
| Web: recent decisions list view | ScorecardPanel |

---

## Parity Check Protocol

When you change a feature in **either** interface:

1. Find the feature in the table above.
2. If the other interface is `✅`, update it to match the change.
3. If the other interface is `❌` and the feature is not in *Intentional Divergences*, implement it.
4. Update this table to reflect the new state.
5. If you're unsure whether something should be ported, add it to *Known Gaps* rather than leaving it undocumented.

**Do not mark a feature task complete if PARITY.md has not been updated.**
