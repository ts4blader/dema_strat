import numpy as np


def build_chandelier_exits(data, signals, trail_mult):
    atr_np = signals["atr"].to_numpy(dtype=np.float64)
    high_np = data["High"].to_numpy(dtype=np.float64)
    low_np = data["Low"].to_numpy(dtype=np.float64)
    long_in = signals["long"].to_numpy(dtype=bool)
    short_in = signals["short"].to_numpy(dtype=bool)
    n = len(atr_np)
    long_exits = np.zeros(n, dtype=bool)
    short_exits = np.zeros(n, dtype=bool)
    peak = np.nan
    trail = np.nan
    pos = 0

    for i in range(n):
        if pos == 0:
            if long_in[i] and np.isfinite(atr_np[i]) and atr_np[i] > 0:
                pos = 1
                peak = high_np[i]
                trail = peak - trail_mult * atr_np[i]
            elif short_in[i] and np.isfinite(atr_np[i]) and atr_np[i] > 0:
                pos = -1
                peak = low_np[i]
                trail = peak + trail_mult * atr_np[i]
            continue

        if pos == 1:
            peak = max(peak, high_np[i])
            if np.isfinite(atr_np[i]) and atr_np[i] > 0:
                raw_trail = peak - trail_mult * atr_np[i]
                trail = max(trail, raw_trail)
            if low_np[i] <= trail:
                long_exits[i] = True
                pos, peak, trail = 0, np.nan, np.nan
        else:
            peak = min(peak, low_np[i])
            if np.isfinite(atr_np[i]) and atr_np[i] > 0:
                raw_trail = peak + trail_mult * atr_np[i]
                trail = min(trail, raw_trail)
            if high_np[i] >= trail:
                short_exits[i] = True
                pos, peak, trail = 0, np.nan, np.nan

    return long_exits, short_exits
