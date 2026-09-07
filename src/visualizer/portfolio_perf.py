import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def portfolio_perf_visualizer(portfolio):
    UP_COLOR = "#636efa"
    DOWN_COLOR = "#EF553B"

    start_date = portfolio.wrapper.index[0]
    end_date = portfolio.wrapper.index[-1]

    equity_daily = portfolio.value().resample("D").last().ffill()
    daily_returns = equity_daily.pct_change().fillna(0)

    monthly_matrix = daily_returns.vbt.returns.qs.monthly_returns() * 100

    yearly_series = monthly_matrix["EOY"]
    monthly_matrix = monthly_matrix.drop(columns=["EOY"])

    monthly_long = monthly_matrix.reset_index().melt(
        id_vars="index", var_name="Month", value_name="Return"
    )
    monthly_long["Date"] = pd.to_datetime(
        monthly_long["Month"] + " " + monthly_long["index"], format="%b %Y"
    )

    # 1. Map colors: UP_COLOR if Return >= 0, otherwise DOWN_COLOR
    bar_colors = [UP_COLOR if r >= 0 else DOWN_COLOR for r in monthly_long["Return"]]

    # 2. Compute statistics for overlay (monthly)
    monthly_median = monthly_long["Return"].median()
    monthly_mean = monthly_long["Return"].mean()
    monthly_std = monthly_long["Return"].std()
    monthly_skew = monthly_long["Return"].skew()

    # 3. Pass the bar_colors list to the marker_color parameter
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Monthly Return (%)",
            "Yearly Return (%)",
            "Equity (CASH)",
            "Drawdown (%)",
            "Daily Returns (%)",
            "Daily Drawdown (%)",
        ),
    )

    # Top row: monthly and yearly returns (same as before)
    fig.add_trace(
        go.Bar(
            x=monthly_long["Date"],
            y=monthly_long["Return"],
            marker_color=bar_colors,
            name="Monthly",
        ),
        row=1,
        col=1,
    )
    fig.add_annotation(
        xref="x domain",
        yref="y domain",
        x=0.98,
        y=0.05,
        text=(
            f"Mean: {monthly_mean:.2f}<br>"
            f"Median: {monthly_median:.2f}<br>"
            f"Std: {monthly_std:.2f}<br>"
            f"Skew: {monthly_skew:.2f}"
        ),
        showarrow=False,
        align="left",
        font={"size": 10, "color": "white"},
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(17, 27, 33, 0.7)",
        row=1,
        col=1,
    )

    yearly_colors = [UP_COLOR if r >= 0 else DOWN_COLOR for r in yearly_series]
    # Yearly statistics
    yearly_median = yearly_series.median()
    yearly_mean = yearly_series.mean()
    yearly_std = yearly_series.std()
    yearly_skew = yearly_series.skew()

    fig.add_trace(
        go.Bar(
            x=yearly_series.index,
            y=yearly_series,
            marker_color=yearly_colors,
            name="Yearly",
        ),
        row=1,
        col=2,
    )
    fig.add_annotation(
        xref="x2 domain",
        yref="y2 domain",
        x=0.98,
        y=0.05,
        text=(
            f"Mean: {yearly_mean:.2f}<br>"
            f"Median: {yearly_median:.2f}<br>"
            f"Std: {yearly_std:.2f}<br>"
            f"Skew: {yearly_skew:.2f}"
        ),
        showarrow=False,
        align="left",
        font={"size": 10, "color": "white"},
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(17, 27, 33, 0.7)",
        row=1,
        col=2,
    )

    first_year = monthly_long["Date"].dt.year.min()
    start = pd.Timestamp(f"{first_year}-01-01")
    end = pd.Timestamp(f"{first_year + 1}-12-31")

    # Second row: equity and drawdown line charts (as before)
    fig.update_layout(
        font_family="JetBrainsMono Nerd Font",
        title=f"📊 backtest result ({start_date.date()} - {end_date.date()})",
        template="plotly_dark",
        yaxis_tickformat=".1f",
        yaxis2={"tickformat": ".1f"},
        xaxis={"range": [start, end], "type": "date"},
        showlegend=False,
        height=900,
    )

    equity_series = portfolio.value()
    drawdown_series = portfolio.drawdown() * 100

    fig.add_trace(
        go.Scatter(x=equity_series.index, y=equity_series, mode="lines", name="Equity"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=drawdown_series.index, y=drawdown_series, mode="lines", name="Drawdown"
        ),
        row=2,
        col=2,
    )

    # Compute daily statistics (as percentages)
    # daily_returns are in decimal, convert to percent for metrics
    _daily_mean_pct = daily_returns.mean() * 100
    _daily_median_pct = daily_returns.median() * 100
    _daily_std_pct = daily_returns.std() * 100
    _daily_skew = daily_returns.skew()  # skew is unit‑less, keep as is

    # Drawdown series is already in percent
    _drawdown_mean = drawdown_series.mean()
    _drawdown_median = drawdown_series.median()
    _drawdown_std = drawdown_series.std()
    _drawdown_skew = drawdown_series.skew()

    # Third row: distribution of daily returns (histogram) and drawdown entries (histogram)
    fig.add_trace(
        go.Histogram(
            x=daily_returns,
            nbinsx=50,
            marker_color=UP_COLOR,
            histnorm="percent",
        ),
        row=3,
        col=1,
    )
    fig.add_annotation(
        xref="x5 domain",
        yref="y5 domain",
        x=0.98,
        y=0.05,
        text=(
            f"Mean: {_daily_mean_pct:.2f}%<br>"
            f"Median: {_daily_median_pct:.2f}%<br>"
            f"Std: {_daily_std_pct:.2f}%<br>"
            f"Skew: {_daily_skew:.2f}"
        ),
        showarrow=False,
        align="left",
        font={"size": 10, "color": "white"},
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(17, 27, 33, 0.7)",
    )
    fig.add_trace(
        go.Histogram(
            x=drawdown_series,
            nbinsx=50,
            marker_color=DOWN_COLOR,
            histnorm="percent",
        ),
        row=3,
        col=2,
    )
    fig.add_annotation(
        xref="x6 domain",
        yref="y6 domain",
        x=0.98,
        y=0.05,
        text=(
            f"Mean: {_drawdown_mean:.2f}%<br>"
            f"Median: {_drawdown_median:.2f}%<br>"
            f"Std: {_drawdown_std:.2f}%<br>"
            f"Skew: {_drawdown_skew:.2f}"
        ),
        showarrow=False,
        align="left",
        font={"size": 10, "color": "white"},
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(17, 27, 33, 0.7)",
    )

    fig.show()
