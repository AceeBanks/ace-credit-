# Larger-Lab Codebase Map

> **Last Updated:** August 17, 2026  
> **Status:** Post-cleanup — reduced from ~7,000+ tracked files to active working set

---

## 🏗️ Repository Structure

```
larger-lab/
├── 📊 quant-lab/          # Quantitative trading research & backtesting
├── 🔧 tools/              # Utilities, dashboards, MCP servers, monitoring
├── 🧠 core/               # Observer Core AI agent system
├── 🏭 oce/                # Observer Core Engine (backend + frontend)
├── 📡 srrs_opc/           # SRRA-OPC adapter (bridge between systems)
├── 🧪 tests/              # Test suites for forge and observer
├── 📜 scripts/            # Startup scripts and batch operations
├── 🗄️ data/               # Manuals, research data, test results
├── 📈 forge/              # Forge workflow engine (phase gates, execution)
├── 🔮 .openclaw-2/        # OpenClaw2 AI assistant config
├── 📝 memory/             # Agent memory (daily notes, obsidian vault)
├── 🎯 .agents/            # Agent skill definitions
├── 🖥️ .freebuff/          # Freebuff workspace config
└── 📋 Root files          # Config, startup scripts, strategy files
```

---

## 📊 quant-lab/ — Quantitative Trading Lab

**Purpose:** Backtesting, strategy development, and market analysis for MT5/TradingView

### Key Directories
```
quant-lab/
├── strategies/            # Strategy engines (P90, Symmetry Trap, DMR, Blind Chain)
├── backtest/              # Backtest execution & results
├── reports/               # Generated analysis reports (JSON, CSV, MD)
├── data/                  # Market data files, extracted stats
├── engines/               # Strategy engine implementations
├── scripts/               # Automation scripts
├── mt5/                   # MT5 EA configurations
├── pine/                  # TradingView Pine Script strategies
├── pdf_extractions/       # Manual extraction data
├── shallow-well/          # Shallow well analysis
├── sniper/                # Sniper dashboard data
├── src/                   # Source code modules
├── tests/                 # Strategy tests
├── tools/                 # Analysis tools
├── ml/                    # Machine learning models
├── mlr_validation/        # MLR validation results
├── ontology/              # Ontology mappings
├── research/              # Research notes
├── progress/              # Progress tracking
├── war-room/              # War room analysis
└── wiki/                  # Strategy documentation
```

### Core Strategy Engines
| Engine | Purpose | Status |
|--------|---------|--------|
| `p90_cfd_expansion_engine.py` | P90 threshold cascade activation | Active |
| `symmetry_trap_engine.py` | Symmetry trap pattern detection | Active |
| `dmr_strategy.py` | DMR (Dynamic Multi-Regression) | Active |
| `blind_chain_engine.py` | Blind chain analysis | Active |
| `cerebus_resolution_engine.py` | Cerebus resolution patterns | Active |
| `nautilus_trader.py` | Nautilus backtest integration | Active |

---

## 🔧 tools/ — Utilities & Operations

**Purpose:** Operational tools, dashboards, monitoring, and automation

### Key Directories
```
tools/
├── forge/                 # Forge phase tools (inventory, backtest, etc.)
├── po_dashboard/          # Performance operations dashboard
├── d2/                    # D2 diagram generator
├── tradingview-mcp/       # TradingView MCP server
├── voicebox/              # Voice synthesis tools
├── sms-gateway/           # SMS notification gateway
├── operator/              # Operator tools
├── research/              # Research automation
├── testing/               # Test utilities
├── visualization/         # Data visualization
├── scripts/               # Utility scripts
├── agent-hooks/           # Agent lifecycle hooks
├── workspaces/            # Workspace configs
└── bin/                   # Binary tools
```

### Critical Tools
| Tool | Purpose |
|------|---------|
| `progress-sync.py` | Syncs progress across agents |
| `self_heal.py` | Self-healing automation |
| `terminal_cleanup.py` | Cleans stale terminals |
| `workspace_cleanup.py` | Workspace maintenance |
| `forge/phase0_inventory.py` | System inventory & audit |

---

## 🧠 core/ — Observer Core AI System

**Purpose:** Multi-agent AI orchestration system

### Architecture
```
core/
├── observer/              # Observer agent (main orchestrator)
├── orchestration/         # Task orchestration
├── cognition/             # Reasoning & decision-making
├── consensus/             # Multi-agent consensus
├── execution/             # Task execution
├── knowledge/             # Knowledge management
├── learning/              # Adaptive learning
├── observability/         # Monitoring & telemetry
├── identity/              # Agent identity management
├── persistent_field/      # Persistent state field
├── shared_memory/         # Shared memory system
├── semantic/              # Semantic understanding
├── response/              # Response generation
├── parser/                # Input parsing
├── spawn/                 # Agent spawning
├── topology/              # Network topology
├── skills/                # Skill registry
├── research/              # Research module
├── obsidian/              # Obsidian integration
├── telegram/              # Telegram bot
├── utils/                 # Utilities
└── tests/                 # Core tests
```

---

## 🏭 oce/ — Observer Core Engine

**Purpose:** Backend API + Frontend for the Observer system

### Structure
```
oce/
├── backend/               # Python FastAPI backend
│   ├── main.py            # API entry point
│   ├── execution_api.py   # Execution endpoints
│   ├── governance_api.py  # Governance endpoints
│   ├── phase4_api.py      # Phase 4 endpoints
│   ├── observer_runtime.py # Observer runtime
│   ├── event_fabric.py    # Event system
│   ├── dspy_*.py          # DSPy integration
│   ├── srrs_adapter.py    # SRRA adapter
│   └── tests/             # Backend tests
└── frontend/              # Frontend (if exists)
```

---

## 📡 srrs_opc/ — SRRA-OPC Adapter

**Purpose:** Bridge between SRRA and Observer Core

### Key Files
| File | Purpose |
|------|---------|
| `agent_bridge.py` | Agent communication bridge |
| `drift_detector.py` | System drift detection |
| `api/` | API endpoints |
| `frontend/` | Frontend interface |
| `tests/` | Adapter tests |

---

## 🧪 tests/ — Test Suites

```
tests/
├── forge/                 # Forge workflow tests
│   └── phase_00/          # Phase 0 tests
├── stability/             # Stability tests
└── test_observer/         # Observer tests
```

---

## 📜 scripts/ — Startup & Operations

```
scripts/
├── run_*.bat              # Windows batch scripts
├── start_*.py             # Python startup scripts
├── start_*.vbs            # VBScript launchers
└── start_scanners.ps1     # PowerShell scanner start
```

---

## 🗄️ data/ — Data Storage

```
data/
├── manuals/               # Trading manuals
├── observer/              # Observer data
├── rce_llm_results/       # LLM test results
├── rce_test_results/      # RCE test results
├── research/              # Research data
└── test_reports/          # Test reports
```

---

## 🔮 .openclaw-2/ — OpenClaw2 Config

```
.openclaw-2/
├── .openclaw/             # OpenClaw runtime
│   ├── openclaw.json      # Main config
│   ├── MEMORY.md          # Agent memory
│   ├── cron/              # Scheduled jobs
│   └── plugin-skills/     # Plugin skills
├── skills/                # Agent skills
│   └── context-monitor/   # Context monitoring skill
└── openclaw.json          # Workspace config
```

---

## 📝 memory/ — Agent Memory

```
memory/
├── YYYY-MM-DD.md          # Daily notes
├── .dreams/               # Dream state (short-term recall)
└── obsidian-vault/        # Obsidian vault
    ├── doctrine/          # System doctrine
    ├── skills/            # Skill documentation
    ├── ontology/          # Ontology mappings
    └── memory/            # Memory entries
```

---

## 🎯 .agents/ — Agent Definitions

```
.agents/
├── skills/                # Agent skill definitions
│   ├── agent-onboarding/  # Onboarding workflow
│   ├── creative-think/    # Creative thinking
│   ├── github-problem-search/ # GitHub search
│   ├── lazyweb/           # Lazy web browsing
│   ├── mt5-strategy-tester/ # MT5 testing
│   ├── oransim/           # Oracle simulation
│   ├── pdf-omni/          # PDF processing
│   ├── scrapling/         # Web scraping
│   ├── spec-kit/          # Specification toolkit
│   └── violin/            # Violin analysis
└── claude-code.agent.md   # Claude Code agent config
```

---

## 🔗 Key Integrations

| System | Integration Point |
|--------|-------------------|
| **MT5** | `quant-lab/mt5/`, `quant-lab/strategies/` |
| **TradingView** | `quant-lab/pine/`, `tools/tradingview-mcp/` |
| **Telegram** | `core/telegram/`, `tools/sms-gateway/` |
| **Obsidian** | `memory/obsidian-vault/`, `core/obsidian/` |
| **OpenClaw** | `.openclaw-2/` |
| **Freebuff** | `.freebuff/` |

---

## 🚀 Quick Start

### View Strategy Reports
```bash
# List latest backtest results
ls -lt quant-lab/reports/ | head -20

# View specific strategy
cat quant-lab/strategies/p90_cfd_expansion_engine.py
```

### Run Forge Inventory
```bash
python tools/forge/phase0_inventory.py
```

### Start OpenClaw2
```bash
# Check OpenClaw2 status
cat .openclaw-2/openclaw.json
```

### Check Observer Core
```bash
# View core architecture
ls core/

# Run core tests
pytest tests/ -v
```

---

## 📈 Recent Activity

- **2026-08-17:** Major cleanup — removed ~6,800 legacy files
- **2026-08-17:** Restored quant-lab, tools, openclaw-2 from git
- **2026-08-17:** Updated .gitignore for PID/status files
- **2026-08-17:** Pushed cleaned codebase to main

---

## 🎯 Active Branches

| Branch | Purpose | Status |
|--------|---------|--------|
| `main` | Production branch | ✅ Clean |
| `cerebus-mve-implementation` | Cerebus MVE work | ✅ Pushed |
| `capital-routing` | Capital routing design | ✅ Pushed |
| `tb-forward-engine` | Forward engine research | ✅ Pushed |
| `tbx-d01-seal` | TBX D01 seal | ✅ Pushed |

---

*Generated by Codebuff — Clean, organized, ready for action.*
