import numpy as np
from IPython.display import display

from dema_strat import global_style


def neighborhood_analysis(df, PARAMS, TARGET, radius=1):
    param_cols = list(PARAMS)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[TARGET])

    # rank each param onto integer grid coordinates (handles uneven spacing)
    coords = (
        df[param_cols]
        .apply(lambda s: s.rank(method="dense").astype(int) - 1)
        .to_numpy()
    )
    vals = df[TARGET].to_numpy()

    # precompute Chebyshev distance matrix → neighbour mask
    # |coords[i] - coords[j]|_inf <= radius
    dist = np.abs(coords[:, None, :] - coords[None, :, :]).max(axis=2)
    mask = dist <= radius

    df = df.copy()
    df["smoothed"] = np.nanmean(np.where(mask, vals[None, :], np.nan), axis=1)
    df["n_neighbours"] = mask.sum(axis=1)

    # edge combos have few neighbours — their smoothed value is unreliable
    core = df[df["n_neighbours"] >= 0.6 * df["n_neighbours"].max()]
    core["score"] = (
        core["smoothed"] * 0.7 + core[TARGET] * 0.3
    )  # adjust weights to taste

    print(f"Target: {TARGET}, SCORE = smoothed * 0.7 + TARGET * 0.3")
    display(
        global_style(
            core.nlargest(10, columns=["score"])[
                param_cols + [TARGET, "smoothed", "n_neighbours", "score"]
            ]
        )
    )

    best = core.nlargest(1, columns=["score"]).iloc[0]
    print("The best parameters combination: ")
    display(best)

    return best
