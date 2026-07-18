"""
Convert a MetaTrader-style intraday CSV export (DATE + TIME columns)
into a pandas DataFrame usable by backtesting.py.

Expected input columns (tab-separated):
<DATE>  <TIME>  <OPEN>  <HIGH>  <LOW>  <CLOSE>  <TICKVOL>  <VOL>  <SPREAD>

Output DataFrame:
- DatetimeIndex (combining DATE + TIME)
- Columns: Open, High, Low, Close, Volume
"""

import pandas as pd


def load_mt_csv(filepath: str, sep: str = "\t") -> pd.DataFrame:
    """
    Load an MT4/MT5-exported intraday CSV and return a DataFrame
    formatted for backtesting.py.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    sep : str
        Field delimiter. MT exports are usually tab-separated ('\\t').
        If your file is comma-separated, pass sep=','.

    Returns
    -------
    pd.DataFrame
        Indexed by datetime, with columns Open, High, Low, Close, Volume.
    """
    df = pd.read_csv(filepath, sep=sep, dtype=str)

    # Normalize headers: <DATE> -> DATE, lowercase/whitespace variations -> uppercase
    df.columns = [c.strip().strip("<>").upper() for c in df.columns]

    # Build a datetime column from DATE/TIME when available, otherwise fall back
    if "TIME" in df.columns:
        df["Datetime"] = pd.to_datetime(
            df["DATE"].astype(str).str.strip() + " " + df["TIME"].astype(str).str.strip(),
            format="%Y.%m.%d %H:%M:%S",
            errors="coerce",
        )
    else:
        for col in ("DATE"):
            if col in df.columns:
                df["Datetime"] = pd.to_datetime(df[col], errors="coerce")
                break
        else:
            raise ValueError("Could not find a usable datetime column: DATE/TIME or DATETIME/TIMESTAMP")

    # Rename to backtesting.py's expected column names
    df = df.rename(
        columns={
            "OPEN": "Open",
            "HIGH": "High",
            "LOW": "Low",
            "CLOSE": "Close",
            "TICKVOL": "Volume",  # use tick volume as proxy (VOL is often 0)
        }
    )

    # Keep only what's needed, cast prices/volume to numeric
    df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.set_index("Datetime").sort_index()

    # Basic sanity checks
    df = df.dropna()
    df = df[~df.index.duplicated(keep="first")]

    return df

