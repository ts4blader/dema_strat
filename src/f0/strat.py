import vectorbt as vbt
import numpy as np
import pandas as pd

from pathlib import Path
import sys

sys.path.insert(0, str(Path(".").resolve().parent))
from constants import COMMISSION, CASH


class STRAT:

    def __init__(
        self,
        data,
        ema_p=9,
        smoothing_p=12,
        use_vwap=True,
        atr_p=18,
    ):
        # self.params = {
        #     "ema": {"default": 9, "data": range(5, 15, 2)},
        #     "smoothing": {"default": 12, "data": range(6, 16, 2)},
        #     "vwap": {"default": True, "data": [True, False]},
        #     "atr_period": {"default": 18, "data": [14, 18, 21]},
        #     "sl_mult": {"default": 1, "data": [1, 2, 3]},
        #     "rr_ratio": {"default": 1, "data": [0.25, 0.5, 1.0, 1.5, 2.0]},
        # }

        self.ema_p = ema_p
        self.smoothing_p = smoothing_p
        self.use_vwap = use_vwap
        self.atr_p = atr_p

        self.data = data
        self.freq = self.data.index.to_series().diff().median()

    def _make_signals(self):
        data = self.data

        # keep float32 through indicator math; cast up only at the vectorbt boundary
        close = data["Close"]
        high = data["High"]
        low = data["Low"]

        ema = vbt.indicators.MA.run(close, window=self.ema_p, ewm=True)
        smoothed = vbt.indicators.MA.run(ema.ma, window=self.smoothing_p, ewm=True)
        atr = vbt.indicators.ATR.run(high, low, close, window=self.atr_p)

        long_cross = ema.ma_crossed_above(smoothed)
        short_cross = ema.ma_crossed_below(smoothed)

        valid_atr = np.isfinite(atr.atr) & (atr.atr > 0)
        long_mask = long_cross & valid_atr
        short_mask = short_cross & valid_atr

        if self.use_vwap:
            long_mask = long_mask & (close > data["VWAP"])
            short_mask = short_mask & (close < data["VWAP"])
        long_signal = long_mask
        short_signal = short_mask

        return pd.DataFrame(
            {
                "ema": ema.ma,
                "smoothed": smoothed.ma,
                "long": long_signal,
                "short": short_signal,
                "atr": atr.atr,
            }
        )

    def _run_backtest(self, long_exits, short_exits, size=200, size_type="value"):
        if long_exits is None or short_exits is None:
            print("Please provide long exits and short exits")
            return

        signals = self._make_signals()
        freq = self.data.index.to_series().diff().median()

        long_signal = signals["long"].to_numpy()
        short_signal = signals["short"].to_numpy()

        portfolio = vbt.Portfolio.from_signals(
            close=self.data["Close"],
            entries=long_signal,
            exits=long_exits,
            short_entries=short_signal,
            short_exits=short_exits,
            init_cash=CASH,
            fees=COMMISSION,
            size=size,
            size_type=size_type,
            freq=freq,
        )

        return portfolio
