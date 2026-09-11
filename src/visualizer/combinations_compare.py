import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def combinations_compare_visualizer(
    first_data, second_data, chart_title, first_name, second_name
):
    METRICS_TO_COMPARE = ["profit_factor", "winrate", "calmar_ratio", "max_dd"]

    # ── labels ──
    col_labels = {
        "profit_factor": "Profit Factor",
        "winrate": "Win Rate (%)",
        "calmar_ratio": "Calmar Ratio",
        "max_dd": "Max Drawdown (%)",
    }

    # ── figure: 2×2 percent-normalized histograms ──
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[f"{col_labels[c]}" for c in METRICS_TO_COMPARE],
        horizontal_spacing=0.08,
        vertical_spacing=0.12,
    )

    def _annotation_text(mean: float, median: float, std: float, skew: float) -> str:
        return (
            f"Mean: {mean:.2f}<br>"
            f"Median: {median:.2f}<br>"
            f"Std: {std:.2f}<br>"
            f"Skew: {skew:.2f}"
        )

    for i, col in enumerate(METRICS_TO_COMPARE):
        row, col_idx = divmod(i, 2)
        row += 1
        col_idx += 1

        first_values = first_data[col].dropna()
        second_values = second_data[col].dropna()
        mid_len = (len(first_values) + len(second_values)) / 2
        n_bins = max(15, min(int(np.ceil(np.log2(mid_len)) + 1), 30))
        # n_bins = 30

        # compute statistics
        mean_val = first_values.mean()
        median_val = first_values.median()
        std_val = first_values.std()
        skew_val = first_values.skew()

        fig.add_trace(
            go.Histogram(
                x=first_values,
                nbinsx=n_bins,
                histnorm="percent",
                hovertemplate=(
                    f"{col_labels[col]}: " + "%{x:.2f}<br>"
                    "Percent: %{y:.1f}%<extra></extra>"
                ),
                showlegend=i == 0,
                marker={"color": "#fa6363"},
                legendgroup="first",
                name=first_name,
            ),
            row=row,
            col=col_idx,
        )

        fig.add_trace(
            go.Histogram(
                x=second_values,
                nbinsx=n_bins,
                histnorm="percent",
                hovertemplate=(
                    f"{col_labels[col]}: " + "%{x:.2f}<br>"
                    "Percent: %{y:.1f}%<extra></extra>"
                ),
                showlegend=i == 0,
                marker={"color": "#636efa"},
                legendgroup="second",
                name=second_name,
            ),
            row=row,
            col=col_idx,
        )

        # annotation for this subplot
        axis_num = i + 1
        xref = "x domain" if axis_num == 1 else f"x{axis_num} domain"
        yref = "y domain" if axis_num == 1 else f"y{axis_num} domain"
        fig.add_annotation(
            xref=xref,
            yref=yref,
            x=0.98,
            y=0.95,
            text=_annotation_text(mean_val, median_val, std_val, skew_val),
            showarrow=False,
            align="left",
            font={"size": 10, "color": "white"},
            bordercolor="white",
            borderwidth=1,
            borderpad=4,
            bgcolor="rgba(17, 27, 33, 0.7)",
            row=row,
            col=col_idx,
        )

        fig.update_yaxes(
            ticksuffix="%",
            row=row,
            col=col_idx,
        )

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=1.0,
        y=-0.15,  # Position slightly below the bottom right
        text="*Metrics calculated on red bar only",
        showarrow=False,  # Turn off the arrow for captions
        xanchor="right",  # Align text to the right
        font={"size": 10, "color": "gray"},
    )

    fig.update_layout(
        title={
            "text": chart_title,
            "x": 0.5,
            "xanchor": "center",
        },
        height=700,
        font_family="JetBrainsMono Nerd Font",
        bargap=0.2,
        template="plotly_dark",
        margin={"t": 120},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.03,
            "xanchor": "center",
            "x": 0.5,
        },
    )

    return fig
