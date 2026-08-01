# MT5 EA Inventory and Parity Record

> **Purpose:** Document MT5 Expert Advisors, Nautilus strategies, and parity relationships  
> **Status:** Draft - Initial inventory complete  
> **Created:** 2026-08-01  
> **Classification:** MT5 MCP: experimental/quarantined (per safe default)

---

## Discovered Components

### 1. MT5 MCP Expert Advisor

**Location:** `projects/trading/mt5-mcp/controller_ea.mq5`  
**Type:** Helper EA for MCP-driven backtesting via file IPC  
**Purpose:** Executes backtest commands from JSON file, writes results to JSON file  
**Language:** MQL5 (MetaQuotes Language 5)  
**Classification:** Experimental/Quarantined

**Key Features:**
- Reads backtest commands from `backtest_command.json`
- Executes Strategy Tester backtests
- Writes results to `backtest_result.json`
- File IPC interface for MCP integration
- No trading authority (backtest only)

**Input Parameters:**
- EA name (auto-detect if empty)
- Symbol (default: EURUSD)
- Timeframe (default: H1)
- Deposit (default: 10,000)
- Date range (default: 2024-01-01 to 2025-12-31)
- Optimization flag

**Output Metrics:**
- Profit, balance, profit factor
- Sharpe ratio, max drawdown
- Total trades, profit/loss trades
- Expected payoff, recovery factor

---

### 2. Nautilus Symmetry Trap Strategy

**Location:** `projects/trading/nautilus/strategies/symmetry_trap.py`  
**Runner:** `projects/trading/nautilus/run_symmetry_trap.py`  
**Type:** Genuine Nautilus Trader strategy  
**Purpose:** Implements CEREBUS FX v4.0 Distribution Symmetry Trap (Part 15, Pages 141-143)  
**Framework:** Nautilus Trader (canonical backtest engine per anchor A6)  
**Classification:** Canonical FX backtest strategy

**Strategy Logic (Three-Layer Model):**
- **Layer 1 - BIAS LOCK:** First M5 close outside Asian Range sets session direction
- **Layer 2 - ATOMIC ENTRY:** Impulse candle in bias direction + opposite close pullback
- **Layer 3 - DISTRIBUTION TARGETS:** -25% / -50% / -100% of Asian Range

**Session Timing:**
- Asian Range: 7PM - 3AM EST (19:00-03:00 UTC)
- Bias Window: 3AM - 12PM EST (08:00-17:00 UTC)
- Hard Exit: 12:00 PM EST (17:00 UTC)

**Tier Classification:**
- T1: Asian Range < 20 pips | Atomic Unit = 10p
- T2: Asian Range 20-30 pips | Atomic Unit = 12p
- T3: Asian Range 30-45 pips | Atomic Unit = 15p
- NO-GO: Asian Range > 45 pips

**Position Management:**
- T25 (-25% AR): Close 50% of position, move SL to breakeven
- T50 (-50% AR): Close 40% of position
- T100 (-100% AR): Close remaining 10% runner
- SL: M5 close back inside Asian band (81.2% rule)

**Risk Management:**
- Risk per trade: 0.25% equity
- Max daily loss: 1.0% (4 trades x 0.25%)
- SL distance: Atomic Unit (tier-specific)

**Data Source:**
- CSV data (forex.com / OX Securities format)
- Loads from `DOWNLOADS_DIR`
- Parsed as Nautilus Bar objects

---

### 3. CEREBUS Symmetry Option B EA (External Candidate)

**Status:** Discovered external FX execution candidate  
**Source:** CEREBUS FX v4.0 manual  
**Type:** Pine Script Expert Advisor  
**Location:** External (not in repository - must be registered and reviewed)  
**Classification:** External blocker (until registered)

**Action Required:**
- [ ] Register external EA location
- [ ] Hash EA source code
- [ ] Review EA logic and safety controls
- [ ] Parity-check with Nautilus Symmetry Trap
- [ ] Document interface and data requirements
- [ ] Evaluate as canonical FX execution path

---

## Parity Matrix

| Feature | MT5 Controller EA | Nautilus Symmetry Trap | CEREBUS Option B EA |
|---------|-------------------|------------------------|---------------------|
| Platform | MT5 (MetaTrader 5) | Nautilus Trader | TradingView (Pine Script) |
| Data Source | MT5 Terminal | CSV (forex.com/OX) | TradingView |
| Backtest Engine | MT5 Strategy Tester | Nautilus Backtest Engine | TradingView Strategy Tester |
| Session Timing | Configurable | Hardcoded per manual | Configurable |
| Tier System | Not implemented | Implemented (T1/T2/T3) | Unknown |
| Risk Management | Basic | Advanced (0.25% per trade) | Unknown |
| Position Management | Not implemented | Advanced (T25/T50/T100) | Unknown |
| SL Logic | Not implemented | 81.2% Asian band rule | Unknown |
| Hard Exit | Not implemented | 12:00 PM EST | Unknown |
| File IPC | Yes (JSON) | No | Unknown |
| MCP Integration | Yes | No | Unknown |

---

## Key Findings

### MT5 MCP Status
- **Classification:** Experimental/Quarantined (per safe default)
- **Authority:** Backtest only, no live trading
- **Integration:** MCP-compatible via file IPC
- **Risk:** Low (test environment only)

### Nautilus Symmetry Trap Status
- **Classification:** Canonical FX backtest strategy
- **Framework:** Nautilus Trader (per anchor A6)
- **Completeness:** Fully implements CEREBUS v4.0 manual
- **Risk:** Low (backtest environment only)

### External FX Script Gap
- **Current Status:** External blocker (not in repository)
- **Candidate:** CEREBUS Symmetry Option B EA
- **Action Required:** Register, hash, review, parity-check before use
- **Impact:** FX execution blocked until location/interface recorded
- **Non-Blocker:** Research and data phases are not blocked

---

## Recommendations

### Immediate Actions
1. **Register CEREBUS Option B EA:** Document external location, hash source, review logic
2. **Parity Analysis:** Compare Symmetry Trap logic between Nautilus and Pine implementations
3. **MT5 MCP Classification:** Maintain as experimental/quarantined (not canonical FX path)

### For Phase 0 Book 3 Classification
- **MT5 MCP:** Experimental/Quarantined
- **Nautilus Symmetry Trap:** Canonical backtest strategy
- **CEREBUS Option B EA:** External blocker (until registered)
- **FX Execution Path:** External blocker (Phase 9 issue, not Phase 0 blocker)

### For Future FX Integration
- Evaluate MT5 MCP as candidate for Pine ↔ MT5 bridge
- Consider Nautilus Symmetry Trap as canonical strategy logic
- Integrate CEREBUS Option B EA only after registration and parity check

---

**Status:** MT5 EA inventory complete. Parity analysis required for CEREBUS EA. FX execution remains external blocker.