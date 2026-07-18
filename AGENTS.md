# AGENTS.md — `dema_vwap_rsi`

Guidance for AI assistants working in this backtesting project. Follow existing patterns; do not introduce new frameworks without asking.

## Project Overview

A `backtesting.py` based strategy lab. The current strategy is an **EMA(9/21) crossover filtered by daily-reset VWAP**, with previous-bar swing SL and an R:R multiple for TP. Position sizing is risk-based, capped by leverage.

Despite the folder name, **no DEMA and no RSI are used** — the folder name is aspirational. Don't add them without being asked.

## File Layout

```
dema_vwap_rsi/
├── AGENTS.md             # this file
├── strategy.py           # STRAT class for backtesting.py
├── preprc_mt5.py         # MT4/MT5 CSV -> DataFrame loader
├── backtester.ipynb      # main driver: load -> BT -> sweep -> DB -> plot
├── utils.ipynb           # scratchpad, ignore unless asked
├── backtest_results.db   # SQLite store (table: v1_rr)
└── index.html            # last Bokeh plot export
```

## Build / Run

- **Python**: 3.14.4 (see `.venv/`)
- **Notebook kernel**: `.venv (3.14.4)` — already configured in `backtester.ipynb`
- **Run sweep**: open `backtester.ipynb`, run cells top-to-bottom
- **Single backtest**: cell 7 (XAUUSD H1) is the minimal example
- There is no test suite, no `Makefile`, no `requirements.txt`. Don't invent commands.

Expected input CSVs live at `~/market_data/<ASSET>/<ASSET>_<TF>.csv` with columns `Datetime,Open,High,Low,Close,Volume`.

## Strategy (`strategy.py`)

```python
class STRAT(Strategy):
    n1 = 9              # fast EMA span
    n2 = 21             # slow EMA span
    risk_pct = 0.01     # 1% of equity risked per trade
    risk_reward = 2     # TP = risk_reward * SL distance
```

- **Indicators** (`init`):
  - VWAP: running cumsum of `typical_price * volume / volume` (no daily reset here — the notebook overrides this with a daily-reset VWAP pre-computed on the DataFrame and passed via `data.VWAP`)
  - `ema1`, `ema2`: `pd.Series(Close).ewm(span=n, adjust=False).mean()`
- **Signals** (`next`):
  - `long_signal  = crossover(ema1, ema2) and price > vwap`
  - `short_signal = crossover(ema2, ema1) and price < vwap`
- **SL**: previous bar's `Low` (long) / `High` (short)
- **TP**: `sl_dist * risk_reward`
- **Sizing**: `floor(min(equity * risk_pct / sl_dist, equity * 0.85 / (price * margin)))`
- **Cash/commission/margin** (notebook): `cash=10_000, commission=0.00015, margin=0.01` (≈100× leverage)
- Always `self.position.close()` before opening the opposite direction.

## Notebook Conventions (`backtester.ipynb`)

- **Imports** live in cell 1. Don't add new deps without asking.
- **VWAP is pre-computed in the notebook, not in `init`**, because the version in `init` doesn't reset daily:
  ```python
  typical_price = (data.High + data.Low + data.Close) / 3
  tp_vol = typical_price * data.Volume
  dates = data.index.date
  data['VWAP'] = tp_vol.groupby(dates).cumsum() / data.Volume.groupby(dates).cumsum()
  ```
- **Sweep cell (cell 11)** iterates `product(timeframes, assets, rr_range)` and writes one row per run into the `v1_rr` table. Keep new sweeps appending to a new table (`v2_*`) rather than overwriting.
- **Result queries** must reference the actual table name. The current cell 12 has a bug — it queries `backtest_results` but the table is `v1_rr`. Fix only if asked.

## Database Schema (`backtest_results.db` → `v1_rr`)

| column | type |
|---|---|
| id | INTEGER PK AUTOINCREMENT |
| asset, timeframe | TEXT |
| n1, n2 | INTEGER |
| risk_pct, risk_reward | REAL |
| return_pct, max_drawdown_pct, cagr_pct, sharpe_ratio, win_rate_pct, equity_final | REAL (nullable on error) |
| num_trades | INTEGER |
| run_timestamp | DATETIME DEFAULT CURRENT_TIMESTAMP |

Errors are stored as a row with NULL metrics so the sweep never aborts on a single bad CSV.

## Style

- **No comments** in code unless explicitly requested (house rule).
- Match the existing terse, no-frills style in `strategy.py`.
- Don't add docstrings to functions that don't already have them, unless asked.
- No emojis.

## Known Issues / Inconsistencies

These exist in the current code. Surface them, don't silently fix:

1. **Folder name vs implementation**: `dema_vwap_rsi` implies DEMA + RSI, but strategy uses plain EMA crossover with VWAP filter. No DEMA, no RSI.
2. **VWAP divergence**: `strategy.py:22` uses running (no-reset) VWAP; `backtester.ipynb` pre-computes a **daily-reset** VWAP and reads it from `data.VWAP`. Notebook is the source of truth for results.
3. **`risk_reward` default mismatch**: `2` in `strategy.py`, `1` in the notebook. Notebook override (`bt.run(risk_reward=rr)`) is what's actually executed.
4. **Wrong table name** in `backtester.ipynb:543` — queries `backtest_results`, real table is `v1_rr`.
5. **Unused `import talib`** in cell 1.
6. **Stray `print(size)`** in cell 8 of the notebook pollutes output.
7. **Not a git repo** — no version control on this project.

## Things to Ask Before Doing

- "Add a new indicator?" — confirm naming first (folder says DEMA+RSI, code says EMA+VWAP).
- "Change sweep grid?" — keep appending to a new table version (`v2_*`).
- "Tune `risk_pct` / `risk_reward`?" — these are the primary knobs; document any change in the run that introduces it.
