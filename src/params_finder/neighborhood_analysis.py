import numpy as np
import pandas as pd
from IPython.display import display

from dema_strat import global_style


def neighborhood_analysis(df, PARAMS, TARGET):

    param_cols = [p for p in PARAMS if p not in ("asset", "timeframe")]
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[TARGET])

    # rank each param onto integer grid coordinates (handles uneven spacing)
    grid = df[param_cols].apply(lambda s: s.rank(method="dense").astype(int) - 1)

    def smooth(g, g_grid, radius=1):
        coords = g_grid.to_numpy()
        vals = g[TARGET].to_numpy()
        out = np.empty(len(g))
        for i in range(len(g)):
            # neighbours = within `radius` steps on every axis simultaneously
            mask = np.abs(coords - coords[i]).max(axis=1) <= radius
            out[i] = vals[mask].mean()
        return out

    res = []
    for (asset, tf), g in df.groupby(["asset", "timeframe"]):
        g = g.copy()
        gg = grid.loc[g.index]
        g["smoothed"] = smooth(g, gg)
        g["n_neighbours"] = [
            (np.abs(gg.to_numpy() - r).max(axis=1) <= 1).sum() for r in gg.to_numpy()
        ]
        res.append(g)

    df = pd.concat(res)

    # edge combos have few neighbours — their smoothed value is unreliable
    core = df[df["n_neighbours"] >= 0.6 * df["n_neighbours"].max()]

    print(f"Target: {TARGET}")
    display(
        global_style(
            core.nlargest(10, columns=["smoothed", TARGET])[
                ["asset", "timeframe"]
                + param_cols
                + [TARGET, "smoothed", "n_neighbours"]
            ]
        )
    )
