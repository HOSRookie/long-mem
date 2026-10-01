# long_mem

**Compaction-proof memory for AI coding agents.**

English | [简体中文](README.zh-CN.md)

> The conversation is not a storage medium.
> Anything that lives in the context window can be lost — so nothing lives there.
> Memory lives outside. The window only holds pointers.

![License](https://img.shields.io/badge/license-MIT-blue)
![Agents](https://img.shields.io/badge/agents-Codex·ClaudeCode·ZCode·KimiCode-8A2BE2)
![Field-tested](https://img.shields.io/badge/field--tested-5d_21h_40%2B_compactions_zero_loss-green)
![X](https://img.shields.io/badge/X-%40Rylie1933-black?logo=x)

**long_mem** keeps AI coding agents continuous across context compaction, session restarts, and multi-day runs — without you repeating yourself.

Field-tested: one Codex CLI session ran for **5 days 21 hours** through **40+ compactions** with zero context loss. The full run log is public: [polars-log](https://github.com/nextAgentPolars/polars-log).

Build logs and ongoing updates on X: **[@Rylie1933](https://x.com/Rylie1933)**.

## Why

Every AI coding agent — Claude Code, Codex, ZCode, Kimi Code — shares the same flaw: **the conversation is its entire memory.** So:

- The window fills up, the agent compacts, and everything you told it — constraints, decisions, reasons — is gone. It re-does work you already approved.
- Next-day sessions start from zero. You re-brief the agent on what it did yesterday.
- Some context plugins make it worse: they harvest your prompts, passively capture subagent output, and force-summarize your sessions into their store.

The usual fix is better summarization — which is just **a better lossy compression**.

long_mem is an inversion: **the conversation is not a storage medium.** Long-term memory lives outside — a governed [engram](https://github.com/Gentleman-Programming/engram) store plus the agent's own history. The window only holds pointers. Compaction destroys the conversation, and the conversation holds nothing of value — so compaction becomes a non-event.

## How it works

```text
┌─ session start ───────▶ inject governance policy + pinned memory index
│
├─ during the session …  the agent writes durable judgments to engram
│                         (through the governed gateway). The window
│                         only holds pointers; bodies are read by ID.
│
├─ compaction ──────────▶ inject the "continue directly" rule; recover by
│                         pointer. Never re-summarize.
│
└─ session end / next day rebuild from engram + history as needed —
                          never from the conversation.
```

**Two storage layers:**

| Layer | What it holds | Backed by |
|---|---|---|
| History recall | What happened | The agent's own history (e.g. Codex's SQLite history) |
| Judgment distillation | Why it was decided | [engram](https://github.com/Gentleman-Programming/engram) |

**The governance layer is the point.** Upstream memory plugins ship three automatic intake ports — prompt harvesting, passive subagent capture, forced session summaries. long_mem welds them shut and keeps exactly two: startup injection and post-compaction recovery. The thing being prevented is the agent polluting its own memory store.

| Upstream hook | What it does | long_mem |
|---|---|---|
| UserPromptSubmit | Harvests every prompt | ❌ welded shut (may contain credentials) |
| SubagentStop | Passively captures subagent output | ❌ welded shut |
| SessionEnd | Force-generates a summary | ❌ welded shut |
| SessionStart | Injects memory | ✅ kept |
| Post-compaction | Recovers context | ✅ kept |

## Quick start

Prerequisite — install [engram](https://github.com/Gentleman-Programming/engram):

```sh
brew install engram
```

Then pick your agent:

| Agent | Install |
|---|---|
| **Codex** | See [PLUGIN.md](PLUGIN.md) (add the marketplace to config.toml) |
| **Claude Code** | `claude plugin marketplace add HOSRookie/long-mem` → install long-mem |
| **ZCode** | Plugin Marketplace → Add → paste this repo's URL |
| **Kimi Code** | `/plugins install <repo>/adapters/kimi-code` — see the [adapter guide](adapters/kimi-code/README.md) |
| **Gemini / Qwen / MiniMax / anything else** | Clone this repo → `scripts/inject-rules.sh` + wire up MCP per the [compatibility matrix](#compatibility) |

After installing: open a new session. The agent sees the governance policy and your project's pinned memory index automatically. When the window compacts, it continues directly — you'll see what that means the first time it happens.

## Compatibility

| Agent | MCP | Resident rules | Lifecycle hooks | Manual recovery |
|---|---|---|---|---|
| Codex | ✓ | AGENTS.md | ✓ plugin hooks | compact-prompt |
| Claude Code | ✓ | CLAUDE.md injection | ✓ SessionStart (incl. compact) | skill long-mem-recover |
| ZCode | ✓ | rules template | ✓ SessionStart (compact matcher untested) | skill long-mem-recover |
| Kimi Code | ✓ bundled | systemPrompt injection | sessionStart.skill (hooks upstream WIP) | skill |
| Gemini / Qwen / others | ✓ | inject-rules.sh | — (rules + manual recovery) | skill |

The principle: **MCP is the greatest common denominator; hooks are a bonus.** Hookless agents still get ~90% of the value from resident rules + a manual recovery skill; hooked agents additionally get zero-touch injection.

## Trust model

Memory access is fail-closed:

- The write path goes through a single governed gateway. Blocked tools: `mem_delete`, `mem_capture_passive`, `mem_save_prompt`, `mem_merge_projects`.
- Upstream binary identity gate: sha256 drift is refused.
- Session ↔ project double binding: DB owner check + independent local probe verification.
- 16 KB cap on memory content — bodies live outside; memory stores evidence references.
- The database is opened read-only; cloud sync defaults to off; credentials never enter memory.

Full policy: [governance/POLICY.md](governance/POLICY.md).

## Known limitations

- engram's full-text search is weak on Chinese: recall works via the index + by-ID reads, not search.
- Single trust domain: when multiple agents share one store, access control is by convention, not enforcement.
- What's worth saving is judged by the agent: the mechanism guarantees saved memories aren't lost — it can't guarantee the judgment itself was right.

## Feedback & contributing

- Suggestions and feedback: open an [Issue](https://github.com/HOSRookie/long-mem/issues). Everything gets read.
- Code contributions: open an Issue first to align direction. main is a protected branch; PRs are reviewed and merged by the maintainer — **keeping the memory store clean comes first**.

## Docs

[PLUGIN.md](PLUGIN.md) · [docs/USAGE.md](docs/USAGE.md) · [adapters/](adapters/) · [templates/](templates/) · [governance/POLICY.md](governance/POLICY.md)

## Ecosystem

long_mem is the tip of a larger system:

- **Polaris** (in progress) — a task-governance system for serious development work. long_mem is a minor component extracted from it. One thing I can share: I'm using a structured governance layer to contain LLM hallucinations — **not by eliminating them, but by leaving them nowhere to take effect**. The run log is public: [polars-log](https://github.com/nextAgentPolars/polars-log).
- **Blue Space** (under wraps) — the name is romantic; the thing is still being validated. When it's ready to talk about, there'll be a link here.

If that direction interests you, a Star helps — for a long-cycle project, stars are one of the few fuels it runs on.

## Support

This project burns real money in tokens. If long_mem genuinely helped you, a donation is appreciated — every one of them becomes the context window for the next experiment.

International: [GitHub Sponsors](https://github.com/sponsors/HOSRookie)

Otherwise:

| Alipay | WeChat |
|---|---|
| <img src="docs/images/donate-alipay.jpg" width="240"/> | <img src="docs/images/donate-wechat.jpg" width="240"/> |

## License

[MIT](LICENSE)
