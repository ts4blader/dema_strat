import numpy as np


def parametic_simulation(
    # ev config
    profit_target,
    payout,
    cost,
    # strategy config
    win_rate,
    profit_factor,
    rr_ratio=2.0,  # risk‑reward ratio (gross win / loss)
    risk_pct=0.01,
    start_equity=10_000,
    # simulation config
    n_sims=10_000,
    n_trades=1_000,
    drawdown_level=1,
    seed: int | None = None,
    verbose: bool = False,
):
    rng = np.random.default_rng(seed if seed is not None else 42)

    def solve_cost_R(win_rate_pct, profit_factor, rr_ratio=2.0, sl_R=1.0):
        """
        Back-solve the per-trade cost (in R units) from win rate, PF and RR.

        PF = p * (W - c) / ((1 - p) * (L + c))
        =>  c = (p*W - PF*(1-p)*L) / (PF*(1-p) + p)
        """
        p = win_rate_pct / 100
        W = rr_ratio * sl_R  # gross win in R
        L = sl_R  # gross loss in R
        c = (p * W - profit_factor * (1 - p) * L) / (profit_factor * (1 - p) + p)
        return c

    c = solve_cost_R(win_rate, profit_factor, rr_ratio)

    p_win = win_rate / 100
    net_win = rr_ratio - c
    net_loss = -(1 + c)

    # ---- simulate ----
    wins = rng.random((n_sims, n_trades)) < p_win
    R = np.where(wins, net_win, net_loss)

    # compounding equity
    equity = start_equity * np.cumprod(1 + risk_pct * R, axis=1)
    equity = np.hstack([np.full((n_sims, 1), start_equity), equity])

    # ---- metrics ----
    final = equity[:, -1]
    peak = np.maximum.accumulate(equity, axis=1)
    max_dd = ((peak - equity) / peak).max(axis=1)
    ruined = equity.min(axis=1) <= start_equity * drawdown_level

    # Determine if the profit target was reached **before** the account is ruined.
    # `target_equity` can be an absolute equity level or a profit amount added to `start_equity`.
    target_equity = (
        profit_target if profit_target >= start_equity else start_equity + profit_target
    )
    reached_target = np.any((equity >= target_equity), axis=1)
    reached_drawdown = np.any((equity <= 0), axis=1)

    # ---- EV calculation ----
    ev_per_sim = np.where(reached_target, payout, -cost)
    ev = ev_per_sim.mean()

    if verbose:
        print(f"Median final equity : {np.median(final):,.0f}")
        print(
            f"5th / 95th pct      : {np.percentile(final, 5):,.0f} / {np.percentile(final, 95):,.0f}"
        )
        print(f"Median max DD       : {np.median(max_dd):.1%}")
        print(f"95th pct max DD     : {np.percentile(max_dd, 95):.1%}")
        print(f"EV per simulation: {ev:,.2f}")
        print(f"P(ruin @ {drawdown_level:.0%})     : {ruined.mean():.1%}")
        print(f"P(payout): {reached_target.mean():.1%}")

    return {
        "final_equity": final,
        "max_drawdown": max_dd,
        "ruin_probability": ruined.mean(),
        "ev": ev,
        "payout_probability": reached_target.mean(),
        "metrics": {
            "median_final": np.median(final),
            "pct_5": np.percentile(final, 5),
            "pct_95": np.percentile(final, 95),
            "median_dd": np.median(max_dd),
            "pct_95_dd": np.percentile(max_dd, 95),
        },
    }
