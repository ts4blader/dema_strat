import numpy as np


def build_be_exits(data, signals, rr_ratio, sl_mult):
    atr_np = signals["atr"].to_numpy(dtype=np.float64)
    high_np = data["High"].to_numpy(dtype=np.float64)
    low_np = data["Low"].to_numpy(dtype=np.float64)
    close_np = data["Close"].to_numpy(dtype=np.float64)
    long_in = signals["long"].to_numpy(dtype=bool)
    short_in = signals["short"].to_numpy(dtype=bool)
    n = len(close_np)
    long_exits = np.zeros(n, dtype=bool)
    short_exits = np.zeros(n, dtype=bool)
    # stop‑loss distance for each trade (initial risk amount)
    sl_dists = np.full(n, np.nan, dtype=np.float64)

    pos = 0
    entry_price = np.nan
    sl_price = np.nan
    tp_price = np.nan
    be_triggered = False

    for i in range(n):
        if pos == 0:
            if long_in[i]:
                pos = 1
                entry_price = close_np[i]
                atr = atr_np[i]
                risk = atr * sl_mult
                sl_price = entry_price - risk
                tp_price = entry_price + risk * rr_ratio
                sl_dists[i] = risk
                be_triggered = False
            elif short_in[i]:
                pos = -1
                entry_price = close_np[i]
                atr = atr_np[i]
                risk = atr * sl_mult
                sl_price = entry_price + risk
                tp_price = entry_price - risk * rr_ratio
                sl_dists[i] = risk
                be_triggered = False
            continue

        if pos == 1:
            if short_in[i]:
                long_exits[i] = True
                pos, entry_price, sl_price, tp_price, be_triggered = (
                    0,
                    np.nan,
                    np.nan,
                    np.nan,
                    False,
                )
                continue

            be_level = entry_price + (tp_price - entry_price) * 0.5
            be_level = min(be_level, entry_price + (entry_price - sl_price))

            if not be_triggered and high_np[i] >= be_level:
                sl_price = entry_price
                be_triggered = True

            if low_np[i] <= sl_price or high_np[i] >= tp_price:
                long_exits[i] = True
                pos, entry_price, sl_price, tp_price, be_triggered = (
                    0,
                    np.nan,
                    np.nan,
                    np.nan,
                    False,
                )
        else:
            if long_in[i]:
                short_exits[i] = True
                pos, entry_price, sl_price, tp_price, be_triggered = (
                    0,
                    np.nan,
                    np.nan,
                    np.nan,
                    False,
                )
                continue

            be_level = entry_price - (entry_price - tp_price) * 0.5
            be_level = max(be_level, entry_price - (sl_price - entry_price))

            if not be_triggered and low_np[i] <= be_level:
                sl_price = entry_price
                be_triggered = True

            if high_np[i] >= sl_price or low_np[i] <= tp_price:
                short_exits[i] = True
                pos, entry_price, sl_price, tp_price, be_triggered = (
                    0,
                    np.nan,
                    np.nan,
                    np.nan,
                    False,
                )

    return long_exits, short_exits, sl_dists
