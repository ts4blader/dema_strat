import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def equity_trades_visualizer(data, signals, portfolio, N=500):
    slc = data.iloc[:N]
    sig = signals.iloc[:N]
    trades = portfolio.trades.records_readable

    trades_cap = trades[trades["Entry Timestamp"] < slc.index[-1]]

    fig = make_subplots(
        rows=1,
        cols=1,
        # vertical_spacing=0.03,
    )

    fig.add_trace(
        go.Candlestick(
            x=slc.index,
            open=slc["Open"],
            high=slc["High"],
            low=slc["Low"],
            close=slc["Close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=sig.index,
            y=sig["ema"],
            mode="lines",
            name="EMA",
            line=dict(width=1, color="dodgerblue"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=sig.index,
            y=sig["smoothed"],
            mode="lines",
            name="Smoothed",
            line=dict(width=1, color="orange"),
        ),
        row=1,
        col=1,
    )

    if "VWAP" in slc.columns:
        fig.add_trace(
            go.Scatter(
                x=slc.index,
                y=slc["VWAP"],
                mode="lines",
                name="VWAP",
                line=dict(width=1, dash="dot", color="gray"),
            ),
            row=1,
            col=1,
        )

    long_trades = trades_cap[trades_cap["Direction"] == "Long"]
    short_trades = trades_cap[trades_cap["Direction"] == "Short"]

    long_trade_entries = long_trades["Entry Timestamp"]
    long_trade_exits = long_trades["Exit Timestamp"]

    short_trade_entries = short_trades["Entry Timestamp"]
    short_trade_exits = short_trades["Exit Timestamp"]

    long_mask = slc.index.isin(long_trade_entries.values)
    long_exit_mask = slc.index.isin(long_trade_exits.values)

    short_mask = slc.index.isin(short_trade_entries.values)
    short_exit_mask = slc.index.isin(short_trade_exits.values)

    fig.add_trace(
        go.Scatter(
            x=slc.index[long_mask],
            y=slc["Low"].loc[long_mask].values * 0.999,
            mode="markers",
            name="Long Entry",
            marker=dict(symbol="triangle-up", size=9, color="lime"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=slc.index[long_exit_mask],
            y=slc["High"].loc[long_exit_mask].values * 1.001,
            mode="markers",
            name="Long Exit",
            marker=dict(symbol="x", size=9, color="lime"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=slc.index[short_mask],
            y=slc["High"].loc[short_mask].values * 1.001,
            mode="markers",
            name="Short Entry",
            marker=dict(symbol="triangle-down", size=9, color="red"),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=slc.index[short_exit_mask],
            y=slc["Low"].loc[short_exit_mask].values * 0.999,
            mode="markers",
            name="Short Exit",
            marker=dict(symbol="x", size=9, color="red"),
        ),
        row=1,
        col=1,
    )

    equity_fig = portfolio.value().vbt.plot()
    equity_fig.update_layout(
        title=f"Equity curve",
        xaxis_rangeslider_visible=False,
        height=400,
        template="plotly_dark",
        legend=dict(orientation="v", y=0.5, x=1.02, xanchor="left", yanchor="middle"),
    )
    equity_fig.show()

    fig.update_layout(
        title=f"DEMA Strategy – First {N} Candles",
        xaxis_rangeslider_visible=False,
        height=500,
        template="plotly_dark",
        legend=dict(orientation="v", y=0.5, x=1.02, xanchor="left", yanchor="middle"),
    )
    fig.update_yaxes(title_text="Price")
    fig.show()
