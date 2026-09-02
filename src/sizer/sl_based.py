import numpy as np


def sl_based_sizer(sl_dists, risk_per_trade):
    """Calculate position sizes based on stop‑loss distances.

    Parameters
    ----------
    sl_dists: array‑like
        Positive stop‑loss distance for each trade (price units).
    risk_per_trade: float
        Cash amount to risk on each trade.

    Returns
    -------
    np.ndarray
        Position size (cash value) for each trade. Trades with a non‑positive
        ``sl_dists`` receive a size of ``0.0`` to avoid division errors.
    """
    # Convert to numpy array for vectorised operations
    sl_arr = np.asarray(sl_dists, dtype=np.float64)
    # Avoid division by zero or negative distances
    with np.errstate(divide='ignore', invalid='ignore'):
        sizes = np.where(sl_arr > 0, risk_per_trade / sl_arr, 0.0)
    return sizes
