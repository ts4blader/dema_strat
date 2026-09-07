# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

| Task | Command | Notes |
|------|---------|-------|
| **Install / sync dependencies** | `uv sync` | Uses the `uv.lock` lockfile. Do **not** use `pip`, `poetry`, or other virtual‑env tools. |
| **Run a notebook** | `uv run jupyter lab`  *(or* `uv run jupyter notebook`*)* | Starts Jupyter in the repository root. Notebooks under `src/` are the primary deliverables. |
| **Execute a single notebook cell** | Inside the notebook, press **Shift+Enter** on the cell. |
| **Run a notebook from the CLI** | `uv run jupyter nbconvert --to notebook --execute path/to/notebook.ipynb --output out.ipynb` | Useful for CI or reproducible runs. |
| **Run the strategy programmatically** | `uv run python -m src.f0.strat` *(if a __main__ entry point is added)* | Not present now – you can create a tiny script that imports `STRAT` and runs a backtest. |
| **Run unit / integration tests** | `uv run pytest` | Add tests under a `tests/` directory; use `-k <expr>` to run a single test, e.g. `uv run pytest -k test_loader`. |
| **Lint / type‑check** | `uv run ruff check .`  *(if `ruff` is in dev‑deps)* or `uv run mypy .` | No linter is enforced in the repo, but these commands work once added to `pyproject.toml`. |
| **Clean generated caches** | `rm -f **/__cache_v1.parquet` | The loader creates Parquet caches next to CSVs; delete them to force a rebuild. |
| **Open a REPL with project imports** | `uv run python -i -c "import dema_strat; print('ready')"` | Handy for quick experimentation. |

## High‑Level Architecture & Structure

```
├─ pyproject.toml           # uv project definition (Python 3.14)
├─ uv.lock                  # pinned dependency graph
├─ src/
│   ├─ dema_strat/          # Importable package (installed as `dema_strat`)
│   │   ├─ __init__.py       # Re‑exports public API (loader, vbt_frame, etc.)
│   │   ├─ loader.py         # Loads OHLCV CSV/Parquet, builds float32 cache, adds VWAP
│   │   └─ utils.py (optional) # Shared helper utilities
│   ├─ constants.py         # Global trading parameters (CASH, COMMISSION, SESSIONS)
│   ├─ exits_builder/       # Exit strategy implementations (BE, Chandelier)
│   ├─ sizer/               # Position sizing logic (`sl_based.py`)
│   ├─ visualizer/          # Helpers for plotting trades (`equity_trades.py`)
│   └─ f0/                  # Primary strategy notebook and module
│       ├─ main.ipynb       # Interactive exploration of the DEMA strategy
│       └─ strat.py         # Minimal class used by the notebook
│   └─ f0_raw_smoothing/    # Exploratory notebooks (e.g., `chandelier_exit.ipynb`)
│   └─ pf_rules/           # Documentation of profit‑factor rule‑sets (markdown)
│   └─ backtest_results.db  # SQLite DB with generated backtest outcomes (regenerated, not source)
└─ README.md                # Repo overview (currently empty)
```

### Core Concepts

* **Data loading** – All notebooks and scripts should obtain market data via `dema_strat.load_ohlcv`. The loader creates a cached Parquet file (`<stem>__cache_v1.parquet`) to keep the in‑memory representation `float32`. Deleting the cache forces a fresh load.
* **Trading parameters** – `src/constants.py` defines `MARGIN`, `COMMISSION`, `CASH`, `RISK_PCT`, and `SESSIONS`. These constants are imported directly in notebooks and modules; do **not** hard‑code values elsewhere.
* **Strategy implementation** – The `STRAT` class in `src/f0/strat.py` builds EMA‑based signals, optional VWAP filter, and runs a `vectorbt.Portfolio`. It expects exit signal arrays supplied by the exit‑builder utilities.
* **Exit strategies** – Implemented under `src/exits_builder/` (e.g., `be_exit.py`, `chandelier_exit.py`). They expose functions that return boolean exit vectors compatible with `vectorbt`. Use them when calling `STRAT._run_backtest`.
* **Position sizing** – Encapsulated in `src/sizer/sl_based.py`. It provides functions that compute size based on stop‑loss distance or fixed value.
* **Visualization** – `src/visualizer/equity_trades.py` produces Plotly / Matplotlib charts of equity curves, trade markers, and summary tables. Call it with a `vectorbt.Portfolio` object.
* **Notebooks are first‑class** – The repository treats Jupyter notebooks as the primary output. Keep cell outputs that document results; strip cells that only import or set config to avoid noisy diffs.

## Development Workflow Tips (specific to this repo)

1. **Start from a clean cache** – `rm -f **/__cache_v1.parquet` before a major parameter sweep to guarantee fresh data reads.
2. **Use `free()` between backtest loops** – The notebook pattern calls `free(*objs)` (imported from `vectorbt`) to release underlying NumPy buffers and keep RAM usage stable.
3. **Run notebooks via `uv run jupyter lab`** – This ensures the same interpreter and environment as the library code.
4. **Add new exit or sizing logic** – Place the implementation in the appropriate subpackage (`exits_builder` or `sizer`) and expose it in the package's `__init__.py` for easy import.
5. **Commit messages** – Use short, imperative, lower‑case subjects (e.g., `add chandelier exit`, `fix loader cache key`).

## Relevant Project Documentation

* **AGENTS.md** – Contains the same high‑level overview and tooling recommendations; the content above mirrors its key points.
* **src/pf_rules/** – Markdown files describing profit‑factor rule‑sets (e.g., `ftmo_10k_2step.md`). Useful reference when evaluating backtest performance.

---

*Generated by Claude Code’s `/init` command.*