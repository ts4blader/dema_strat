import math
import sys
from pathlib import Path

import pandas as pd
import vectorbt as vbt

from .loader import load_ohlcv

sys.path.insert(0, str(Path.cwd().parent))
from constants import TABLE_STYLES
import sqlite3
from itertools import product
from pathlib import Path


def load_data_and_split(path, split_ratio=0.8):

    def load_data(file_path):
        return load_ohlcv(file_path, use_cache=True, add_vwap=True)

    file_path = Path(path).expanduser()
    df = load_data(file_path)

    # Split 80/20 into in‑sample (IOS) and out‑of‑sample (OOS)
    split_idx = int(len(df) * split_ratio)
    df_ios = df.iloc[:split_idx]
    df_oos = df.iloc[split_idx:]

    return df_ios, df_oos


def stats_pretiier(stats):
    """Extract key performance metrics from a vectorbt Portfolio.stats() Series.

    Returns a dict with:
        sharp_ratio, sortino_ratio, profit_factor, calmar_ratio, ulcer_index,
        winrate, return_pct, num_trades, max_dd
    """
    mapping = {
        "sharp_ratio": "Sharpe Ratio",
        "sortino_ratio": "Sortino Ratio",
        "profit_factor": "Profit Factor",
        "calmar_ratio": "Calmar Ratio",
        "winrate": "Win Rate [%]",
        "return_pct": "Total Return [%]",
        "num_trades": "Total Trades",
        "max_dd": "Max Drawdown [%]",
        "fee": "Total Fees Paid",
        "expectancy": "Expectancy",
    }
    return {k: stats.get(v) for k, v in mapping.items()}


def compare_benchmark(portfolio, data, freq="1d"):
    # benchmark
    buy_hold_entries = pd.Series(False, index=data.index)
    buy_hold_entries.iloc[0] = True
    pf_benchmark = vbt.Portfolio.from_signals(data, buy_hold_entries, None, freq=freq)

    # Combine stats side-by-side
    pf_all = pd.DataFrame(
        {"STRATEGY": portfolio.stats(), "BENCHMARK": pf_benchmark.stats()}
    )

    selected_metrics = [
        "Total Return [%]",
        "Max Drawdown [%]",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Calmar Ratio",
        "Profit Factor",
        "Total Trades",
        "Win Rate [%]",
        "Total Fees Paid",
    ]

    def format_smart(x):
        if pd.isna(x) or x is None or math.isinf(x):
            return "N/A"
        if isinstance(x, (int, float)):
            # If the number has no decimal part, format as an integer
            if x == int(x):
                return f"{int(x):,}"
            # Otherwise, format with 3 decimal places
            return f"{x:,.3f}"
        return str(x)

    pf_custom = pf_all.loc[selected_metrics]
    display(
        pf_custom.style.format(
            {"STRATEGY": format_smart, "BENCHMARK": format_smart},
            na_rep="N/A",  # Cleanly replaces NaN values
        ).set_table_styles(TABLE_STYLES)
    )


def db_connect():

    db_path = Path("../backtest_results.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    return conn, cursor


def global_style(df):
    """Applies a unified dark-header corporate theme to any DataFrame."""
    return (
        df.style.hide(axis="index")  # Globally hide the index column
        .set_table_styles(TABLE_STYLES)
        .format(precision=2, thousands=",")
    )  # Set standard number formatting
