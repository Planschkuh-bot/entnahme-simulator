# AGENTS.md — Entnahmerechner

## Project Overview

A single-page retirement withdrawal simulator ("Entnahme-Simulator") for German users. It tests whether a portfolio can sustain a given withdrawal strategy across thousands of simulated or historical market scenarios. Written in German (all UI text, variable names in comments).

The core question it answers: *"If I withdraw X% per year from my portfolio, will the money last through my planned retirement horizon — even if the market performs poorly?"*

## Architecture

This is a **no-build, single-file web application**. There is no bundler, no transpiler, no package.json, no dev server.

### Files

- **`index.html`** — Production entry point. Self-contained HTML file with inline React (via CDN Babel standalone), inline CSS, and all JS logic embedded in a `<script type="text/babel">` block. Open directly in a browser.
- **`entnahme-simulator.html`** — Identical copy of `index.html` (appears to be a backup/alternate name).
- **`entnahme-simulator.jsx`** — The same JS/JSX code extracted as a standalone file with ES module imports (`import React from 'react'`). This is the "source of truth" for editing logic, but **cannot run standalone** — it has no HTML wrapper and expects a module bundler.

### Critical: Dual-File Sync Problem

The HTML files and the JSX file contain **the same application logic** but are maintained independently. Changes to `entnahme-simulator.jsx` do NOT automatically propagate to `index.html`. **When making any code change, you MUST update BOTH files** (the JSX and the relevant HTML file), or they will diverge. The JSX file uses ES module imports; the HTML file uses `<script>` CDN tags with Babel standalone transpilation.

### Data Architecture

The app embeds ~150 years of financial data directly as JS constants (no external data files, no API calls):

- **`HIST`** — Annual returns for S&P 500 (with dividends), Gold, 3-Month T-Bills, and US CPI (1872–2025). Sources: Damodaran/NYU Stern, US BLS, Shiller/Cowles Commission via DQYDJ.
- **`MONTHLY_EQ_SP`** — Monthly real total return of the S&P 500 (1,848 data points, Jan 1872–Dec 2025). From Shiller's "ie_data" dataset, already inflation-adjusted.
- **`WORLD_EQ_BY_YEAR`** — Annual world equity proxy returns (1970–2025): 65% US Large Cap + 35% MSCI EAFE.
- **`MONTHLY_EQ_WORLD`** / **`MONTHLY_GOLD_WORLD`** / **`MONTHLY_CASH_WORLD`** — Derived monthly series for the world proxy (built at module init from annual data via geometric intra-year distribution).

**GOTCHA**: Gold and Cash have NO real monthly data — their annual real returns are geometrically distributed across 12 identical sub-months. Only S&P 500 has genuine monthly variation. World-proxy mode similarly has no intra-year noise for any asset class.

### Simulation Engine (Core Logic)

Located in the same file, pure functions with no React dependency:

1. **`simulateWithdrawalBuckets()`** — The core engine. Takes monthly return arrays for eq/gold/cash/btc and a params object. Simulates one withdrawal path with the "bucket" strategy.
   - Good years (ETF drawdown < 20%): withdraw ETF → BTC → Gold → Cash
   - Bad years (ETF drawdown >= 20%): withdraw Cash → Gold → BTC → ETF
   - Reserves (Cash/Gold) are never replenished — portfolio drifts toward 100% ETF over time
   - Supports both "dynamisch" (Vanguard ceiling/floor) and "statisch" (fixed real amount) strategies
   - Supports both monthly and annual withdrawal frequencies
   - ETF TER (total expense ratio) deducted monthly from equity returns

2. **`aggregate()`** — Takes array of path results, computes success rate, Wilson CI, percentile bands (P10/P50/P90), failure curve, median end balance.

3. **Runner functions**:
   - `runHistoricalRolling(p)` — Rolling windows over actual S&P 500 history (1872–2025)
   - `runWorldRolling(p)` — Rolling windows over world proxy (1970–2025)
   - `runHistoricalBootstrap(p)` — Block bootstrap from historical data
   - `runMonteCarlo(p)` — Parametric Monte Carlo with correlated normal returns

4. **Helper functions**:
   - `mulberry32()` / `seedRng()` — Seeded PRNG for reproducible results
   - `wilsonCI()` — 95% Wilson score confidence interval
   - `percentile()` — Interpolated percentile from sorted array
   - `realAssetReturns()` — Deflates nominal returns by CPI
   - `computePensionAnnual()` — German pension calculation (Rentenpunkte × Rentenwert × adjustment factor)
   - `generateBtcReturnsMonthly()` — Lognormal Bitcoin returns (always parametric, never historical)
   - `computeRentalIncomeByYear()` — Rental income stream from apartment value

### Key Constants

- `RENTENWERT_MONATLICH = 42.52` — Euro per Rentenpunkt per month (since 1.7.2026)
- `REGELALTERSGRENZE = 70` — Normal retirement age
- Pension adjustment: -0.3%/month before 70, +0.5%/month after 70
- `WOHNUNG_MIETRENDITE = 0.03` — 3% p.a. rental yield (real)
- `WOHNUNG_REAL_APPRECIATION = 0.015` — 1.5% p.a. real appreciation
- Monte Carlo assumptions: Equities 5%/18%, Gold 0.5%/15%, Cash 0%/1.5%, BTC 15%/65%

### React Component (`EntnahmeSimulator`)

Single monolithic component (~800 lines) with:
- URL parameter loading/sharing (all params serialized to query string)
- `useMemo` for debounced simulation runs (sensitivity analysis, chart data)
- Inline styles throughout (no CSS files, no Tailwind)
- Charts via Recharts (`ComposedChart` with `Area` + `Line` + `ReferenceLine`)
- Responsive grid layout (340px sidebar + fluid main area, collapses at 860px)

Helper components (all in same file):
- `Gauge` — SVG circular gauge for success rate
- `Slider` — Labeled range input with tooltip
- `ModeTab` — Mode selection button
- `Stat` — Labeled stat display
- `SectionLabel` — Section header
- `InfoDot` — Tooltip trigger
- `ChartBlock`, `LightTooltip`, `FailTooltip` — Chart wrappers

### Dependencies (all via CDN in HTML)

- React 18 (production UMD)
- ReactDOM 18 (production UMD)
- Recharts 2.12.7 (UMD)
- Babel Standalone (for in-browser JSX transpilation)
- Google Fonts: Inter + IBM Plex Mono

## Commands

There are no build/test/lint commands. This is a zero-tooling project:

- **Run**: Open `index.html` in a browser
- **Deploy**: Copy files to any static web server or open locally
- **Dev**: Edit files, refresh browser. No hot reload.

## Styling Conventions

- All styles are **inline** via React `style` objects — no CSS files or CSS-in-JS libraries
- Color palette: `#2F5D62` (primary teal), `#3A6B8A` (secondary blue), `#C08A2E` (amber), `#A8432F` (red/error), `#5B6B65` (muted text), `#1C2521` (primary text), `#D3DAD6` (borders), `#EEF1EF` (background)
- Typography: Inter (body), IBM Plex Mono (data/numbers)
- German number formatting via `toLocaleString('de-DE')` — EUR symbol with space separator

## Code Patterns

- **All data embedded**: No external JSON, no fetch calls, no API dependencies
- **Seeded PRNG**: `mulberry32` ensures reproducible results across parameter changes; only the "Neue Zufallsstichprobe" button changes the seed
- **Debounced recomputation**: Simulation runs in `useMemo` keyed on debounced input values
- **No TypeScript, no tests, no linting**: Pure JSX, no type checking
- **Single-component architecture**: Everything lives in one React component + shared pure functions

## Gotchas

1. **Dual files must stay in sync**: `index.html` and `entnahme-simulator.jsx` contain the same logic. Edits to one must be mirrored in the other.
2. **Babel standalone transpilation**: The HTML files use `<script type="text/babel">` which transpiles JSX in the browser. This is slow on first load but enables zero-build development.
3. **`entnahme-simulator.jsx` is NOT directly runnable**: It uses ES module imports but has no bundler. Use `index.html` for running.
4. **World proxy has no intra-year noise**: Monthly values are geometrically distributed from annual data — all 12 months in a year are identical.
5. **Bitcoin is always parametric**: Even in "historical" modes, Bitcoin returns are simulated (lognormal, 15%/65% mu/sigma) because no sufficiently long historical series exists.
6. **Apartment excluded from simulation**: The Eigentumswohnung (apartment) is NOT part of the withdrawal simulation — only rental income offsets withdrawal needs.
7. **No rebalancing**: Once Cash/Gold reserves are depleted, they stay depleted. The portfolio naturally shifts toward 100% equity over time.
8. **Monthly index tracking**: `eqIndex` and `eqATH` (all-time high) track equity-only performance for the drawdown trigger — they exclude Gold/Cash/BTC from the drawdown calculation.
9. **Pension value is held real-constant**: The 42.52 EUR/Rentenpunkt value is assumed to keep pace with inflation over the entire simulation horizon.
10. **The `REGELALTERSGRENZE` is set to 70**, not the actual German Regelaltersgrenze of 67. The pension adjustment formula uses this value for the +/- month calculation.
