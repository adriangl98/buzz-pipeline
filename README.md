# Buzz Agent Pipeline

7-agent software factory running on Buzz with GitHub integration.

## Agents

| Agent | Channel | Role |
|-------|---------|------|
| Griller | #grill | Relentless interviewer. Aligns before building. |
| Specer | #spec | Converts conversations to formal specs. |
| Ticketer | #tickets | Breaks specs into tracer-bullet tickets. |
| Builder | #build | Implements with TDD (red-green-refactor). |
| Reviewer | #review | Two-axis code review (Standards + Spec). |
| Debugger | #debug | Methodical bug diagnosis loop. |
| Architect | #arch | Scans for deepening opportunities. |

## Pipeline

```
idea -> Griller -> Specer -> Ticketer -> Builder -> Reviewer -> done
                          bug -> Debugger -> Builder
                          debt -> Architect -> report
```

## Infrastructure

- **Relay:** Hermes Agent on Hetzner CX23 VPS
- **Git:** GitHub (adriangl98/buzz-pipeline)
- **Webhook relay:** GitHub -> Buzz event bridge (port 8900 -> nginx -> Buzz CLI)
- **Identity:** 7 agent SSH deploy keys, Nostr keypairs per agent

## Setup

See [IDENTITY-MAP.md](/home/adcgo1/vps-agent-lab/IDENTITY-MAP.md) for full agent identity mapping.

## Status (2026-07-31)

- [x] Agent SSH keys generated (7 keypairs)
- [x] Deploy keys added to GitHub repo
- [x] GitHub webhook configured
- [x] Webhook relay deployed on VPS (nginx + Python FastAPI)
- [x] Buzz channel integration verified
- [ ] Worktree isolation (Sandcastle pattern)
- [ ] Shared memory layer (agentmemory)
- [ ] Multi-model support
- [ ] Parallel execution
- [ ] Project board
