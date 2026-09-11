import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def portfolio_perf_visualizer(portfolio, show: bool = True) -> go.Figure:
    """Generate a multi‑panel performance visualization for a backtest.

    Parameters
    ----------
    portfolio : vectorbt.Portfolio
        The backtest portfolio object containing equity, drawdown, and wrapper
        (price series) information.
    show : bool, optional
        If ``True`` (default), the figure is displayed via ``fig.show()``. Setting
        ``False`` returns the figure without displaying, which is convenient for
        testing and programmatic use.

    Returns
    -------
    go.Figure
        A Plotly ``Figure`` with six sub‑plots:
        * Monthly return bar chart
        * Yearly return bar chart
        * Equity curve
        * Drawdown curve
        * Daily return histogram
        * Daily drawdown histogram

    Raises
    ------
    ValueError
        If the supplied ``portfolio`` has no price data.
    """

    # Constants (colors, layout sizes)
    UP_COLOR = "#636efa"
    DOWN_COLOR = "#EF553B"
    HIST_BINS = 50
    FIG_HEIGHT = 900

    # Helper for annotation text
    def _annotation_text(mean: float, median: float, std: float, skew: float) -> str:
        return (
            f"Mean: {mean:.2f}<br>"
            f"Median: {median:.2f}<br>"
            f"Std: {std:.2f}<br>"
            f"Skew: {skew:.2f}"
        )

    start_date = portfolio.wrapper.index[0]
    end_date = portfolio.wrapper.index[-1]

    equity_daily = portfolio.value().resample("D").last().ffill()
    daily_returns = equity_daily.pct_change().fillna(0)

    # Monthly and yearly returns (percentage)
    monthly_matrix = daily_returns.vbt.returns.qs.monthly_returns() * 100
    if monthly_matrix.empty:
        yearly_series = pd.Series(dtype=float)
        monthly_matrix = pd.DataFrame()
    else:
        yearly_series = monthly_matrix["EOY"]
        monthly_matrix = monthly_matrix.drop(columns=["EOY"])

    monthly_long = monthly_matrix.reset_index().melt(
        id_vars="index", var_name="Month", value_name="Return"
    )
    monthly_long["Date"] = pd.to_datetime(
        monthly_long["Month"] + " " + monthly_long["index"], format="%b %Y"
    )

    # Vectorised colour selection
    monthly_colors = np.where(
        monthly_long["Return"] >= 0, UP_COLOR, DOWN_COLOR
    ).tolist()
    yearly_colors = np.where(yearly_series >= 0, UP_COLOR, DOWN_COLOR).tolist()

    # Statistics
    monthly_median = monthly_long["Return"].median()
    monthly_mean = monthly_long["Return"].mean()
    monthly_std = monthly_long["Return"].std()
    monthly_skew = monthly_long["Return"].skew()

    yearly_median = yearly_series.median()
    yearly_mean = yearly_series.mean()
    yearly_std = yearly_series.std()
    yearly_skew = yearly_series.skew()

    # Figure layout
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

    # Monthly return bar chart
    fig.add_trace(
        go.Bar(
            x=monthly_long["Date"],
            y=monthly_long["Return"],
            marker_color=monthly_colors,
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
        text=_annotation_text(monthly_mean, monthly_median, monthly_std, monthly_skew),
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

    # Yearly return bar chart
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
        text=_annotation_text(yearly_mean, yearly_median, yearly_std, yearly_skew),
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

    # Determine overall date range for line plots (full year span)
    first_year = monthly_long["Date"].dt.year.min()
    start = pd.Timestamp(f"{first_year}-01-01")
    end = pd.Timestamp(f"{first_year + 1}-12-31")

    # Equity and drawdown line charts
    fig.update_layout(
        font_family="JetBrainsMono Nerd Font",
        title=f"📊 backtest result ({start_date.date()} - {end_date.date()})",
        template="plotly_dark",
        yaxis_tickformat=".1f",
        yaxis2={"tickformat": ".1f"},
        xaxis={"range": [start, end], "type": "date"},
        showlegend=False,
        height=FIG_HEIGHT,
        bargap=0.2,
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

    # Daily return histogram
    _daily_mean_pct = daily_returns.mean() * 100
    _daily_median_pct = daily_returns.median() * 100
    _daily_std_pct = daily_returns.std() * 100
    _daily_skew = daily_returns.skew()

    fig.add_trace(
        go.Histogram(
            x=daily_returns,
            nbinsx=HIST_BINS,
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
        text=_annotation_text(
            _daily_mean_pct, _daily_median_pct, _daily_std_pct, _daily_skew
        ),
        showarrow=False,
        align="left",
        font={"size": 10, "color": "white"},
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(17, 27, 33, 0.7)",
    )

    # Daily drawdown histogram
    _drawdown_mean = drawdown_series.mean()
    _drawdown_median = drawdown_series.median()
    _drawdown_std = drawdown_series.std()
    _drawdown_skew = drawdown_series.skew()

    fig.add_trace(
        go.Histogram(
            x=drawdown_series,
            nbinsx=HIST_BINS,
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
        text=_annotation_text(
            _drawdown_mean, _drawdown_median, _drawdown_std, _drawdown_skew
        ),
        showarrow=False,
        align="left",
        font={"size": 10, "color": "white"},
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(17, 27, 33, 0.7)",
    )

    return fig
