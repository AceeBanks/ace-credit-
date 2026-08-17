# Larger-Lab System Architecture

> **Version:** 2.0 (Post-Cleanup)  
> **Date:** August 17, 2026  
> **Status:** Clean codebase, active development

---

## 🏗️ System Overview

Larger-Lab is a **multi-agent quantitative trading research platform** that integrates:

1. **Observer Core (OCE)** — Multi-agent AI orchestration system
2. **Quant Lab** — Strategy backtesting & market analysis
3. **Forge** — Workflow automation & phase gates
4. **SRRA-OPC** — System bridge & adapter layer

---

## 🧠 Core Architecture

### Observer Core System

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSERVER CORE (OCE)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Observer   │  │ Cognition   │  │ Consensus   │        │
│  │  (Main)     │──│ (Reasoning) │──│ (Multi-Agt) │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ORCHESTRATION LAYER                     │   │
│  │  • Task routing  • Agent spawning  • State mgmt     │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Execution   │  │ Knowledge   │  │ Learning    │        │
│  │ (Actions)   │──│ (Memory)    │──│ (Adaptive)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Hierarchy

```
Observer (Main Orchestrator)
├── Cognition Agent (Reasoning & Decisions)
├── Consensus Agent (Multi-Agent Agreement)
├── Execution Agent (Task Completion)
├── Knowledge Agent (Memory & Retrieval)
├── Learning Agent (Adaptation)
├── Observability Agent (Monitoring)
└── Spawn Agent (Agent Creation)
```

---

## 📊 Quant Lab Architecture

### Strategy Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    QUANT LAB PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Data Input  │──│ Strategy    │──│ Backtest    │        │
│  │ (MT5/TV)    │  │ Engine      │  │ Execution   │        │
│  └─────────────┘  └─────────────┘  └──────┬──────┘        │
│                                           │                 │
│                                           ▼                 │
│                                    ┌─────────────┐         │
│                                    │ Results     │         │
│                                    │ Analysis    │         │
│                                    └──────┬──────┘         │
│                                           │                 │
│                                           ▼                 │
│                                    ┌─────────────┐         │
│                                    │ Reports     │         │
│                                    │ (JSON/CSV/MD)│         │
│                                    └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Strategy Engines

| Engine | Type | Purpose |
|--------|------|---------|
| **P90 Cascade** | Threshold | Activates at 90th percentile distributions |
| **Symmetry Trap** | Pattern | Detects price symmetry patterns |
| **DMR** | Regression | Dynamic multi-regression analysis |
| **Blind Chain** | Chain | Chain reaction analysis |
| **Cerebus** | Resolution | Multi-timeframe resolution |
| **Nautilus** | Backtest | NautilusTrader integration |

---

## 🔧 Forge Workflow System

### Phase Gates

```
┌─────────────────────────────────────────────────────────────┐
│                    FORGE PHASE GATES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 0: Discovery & Inventory                             │
│  ├── Environment fingerprinting                             │
│  ├── Claim reconciliation                                   │
│  ├── Contradiction analysis                                 │
│  └── Reality lock                                           │
│                                                             │
│  Phase 1: Implementation                                    │
│  ├── Test discovery                                         │
│  ├── Test execution                                         │
│  └── Claim verification                                     │
│                                                             │
│  Phase 2: Validation                                        │
│  ├── Backtest reproduction                                  │
│  ├── Baseline report                                        │
│  └── Service readiness                                      │
│                                                             │
│  Phase 3: Deployment                                        │
│  ├── Environment validation                                 │
│  ├── Configuration lock                                     │
│  └── Production readiness                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 SRRA-OPC Bridge

### Communication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SRRA      │────▶│  SRRA-OPC   │────▶│  Observer   │
│  (System)   │◀────│  Adapter    │◀────│   Core      │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
  ┌─────────┐        ┌─────────┐        ┌─────────┐
  │ Events  │        │ Bridge  │        │ Tasks   │
  │ Stream  │        │ Layer   │        │ Queue   │
  └─────────┘        └─────────┘        └─────────┘
```

---

## 🗄️ Data Architecture

### Storage Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Working    │  │  Persistent │  │  Archive    │        │
│  │  Memory     │  │  Storage    │  │  Storage    │        │
│  │  (RAM)      │  │  (Disk)     │  │  (Git)      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Agent      │  │  Obsidian   │  │  GitHub     │        │
│  │  Memory     │  │  Vault      │  │  Repo       │        │
│  │  (memory/)  │  │  (vault/)   │  │  (remote)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### File Organization

| Directory | Purpose | Retention |
|-----------|---------|-----------|
| `quant-lab/reports/` | Backtest results | Active |
| `quant-lab/data/` | Market data | Active |
| `memory/` | Agent memory | Rolling 30 days |
| `memory/obsidian-vault/` | Long-term knowledge | Permanent |
| `.openclaw-2/` | OpenClaw config | Active |
| `tools/` | Utilities | Active |

---

## 🔗 Integration Points

### External Systems

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  MetaTrader │  │ TradingView │  │  Telegram   │        │
│  │  5 (MT5)    │  │ (Pine)      │  │  Bot        │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              OBSERVER CORE SYSTEM                    │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  OpenClaw   │  │  Freebuff   │  │  Obsidian   │        │
│  │  2          │  │  Client     │  │  Vault      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture

### Local Development

```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL DEVELOPMENT                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  VS Code    │  │  Python     │  │  Git        │        │
│  │  (IDE)      │  │  (Runtime)  │  │  (VCS)      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WORKSPACE (larger-lab)                  │   │
│  │  • quant-lab/  • tools/  • core/  • oce/            │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │  GitHub     │                                           │
│  │  (Remote)   │                                           │
│  └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

### Secrets Management

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: .gitignore                                        │
│  ├── Credentials excluded from git                          │
│  ├── .env files excluded                                    │
│  └── Sensitive files excluded                               │
│                                                             │
│  Layer 2: Runtime Secrets                                   │
│  ├── Environment variables                                  │
│  ├── Credential files (local only)                          │
│  └── API keys (never committed)                             │
│                                                             │
│  Layer 3: Access Control                                    │
│  ├── GitHub repo permissions                                │
│  ├── Local file permissions                                 │
│  └── Network isolation                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Monitoring & Observability

### System Health

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Observer   │  │  Self-Heal  │  │  Progress   │        │
│  │  Runtime    │  │  Daemon     │  │  Sync       │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              TELEMETRY & LOGGING                     │   │
│  │  • Console logs  • File logs  • Telegram alerts     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Development Workflow

### Git Branching Strategy

```
main (production)
├── feature/* (new features)
├── bugfix/* (bug fixes)
├── agent/* (agent-specific work)
└── tb*/* (trading bot work)
```

### Commit Convention

```
type(scope): description

Examples:
feat(quant-lab): add P90 cascade activation
fix(tools): resolve terminal cleanup race condition
docs(core): update architecture documentation
```

---

## 🔄 System Flow

### Trading Research Pipeline

```
1. Data Collection (MT5/TradingView)
   ↓
2. Strategy Development (quant-lab/strategies/)
   ↓
3. Backtesting (quant-lab/backtest/)
   ↓
4. Analysis (quant-lab/reports/)
   ↓
5. Validation (tests/)
   ↓
6. Deployment (tools/)
   ↓
7. Monitoring (observer runtime)
```

### Agent Communication Flow

```
1. Task Received (Telegram/OpenClaw)
   ↓
2. Observer Routes (core/observer/)
   ↓
3. Agent Spawns (core/spawn/)
   ↓
4. Task Executes (core/execution/)
   ↓
5. Results Consensus (core/consensus/)
   ↓
6. Response Generated (core/response/)
   ↓
7. Memory Updated (core/knowledge/)
```

---

## 📊 Performance Metrics

### Key Indicators

| Metric | Target | Current |
|--------|--------|---------|
| Backtest Speed | < 5 min | ~3 min |
| Agent Response | < 2 sec | ~1.5 sec |
| Memory Usage | < 8GB | ~6GB |
| Disk Usage | < 50GB | ~45GB |
| Git Repo Size | < 1GB | ~0.8GB |

---

## 🎓 Learning Resources

### Documentation

- `CODEMAP.md` — Complete file structure
- `ARCHITECTURE.md` — This file
- `memory/obsidian-vault/doctrine/` — System doctrine
- `tools-catalog.md` — Available tools

### Code Examples

- `quant-lab/strategies/` — Strategy implementations
- `core/tests/` — Usage examples
- `tools/forge/` — Forge workflow examples

---

*Architecture documentation generated by Codebuff — August 17, 2026*
