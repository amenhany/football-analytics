"""
Performance vs Market Value

Detects underrated and overpriced players by plotting a composite
performance score against their market value (€M).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D


#colour palette (one per role)
ROLE_COLORS = {
    "Forward":    "#e63946",
    "Midfielder": "#457b9d",
    "Defender":   "#2a9d8f",
    "Goalkeeper": "#e9c46a",
    "Other":      "#adb5bd",
}


def _composite_score(df, perf_cols: list[str]) -> np.ndarray:
    """
    Normalise each stat to [0, 1] then take the mean → composite score in [0, 1].
    Robust to missing values (NaN columns are skipped).
    """
    normed = []
    for col in perf_cols:
        if col not in df.columns:
            print(f"  [WARNING] column '{col}' not found – skipping.")
            continue
        s = df[col].astype(float)
        col_min, col_max = s.min(), s.max()
        if col_max == col_min:          # constant column → skip
            continue
        normed.append((s - col_min) / (col_max - col_min))

    if not normed:
        raise ValueError("No valid performance columns found – check perf_cols.")

    score = np.nanmean(np.column_stack(normed), axis=1)
    return score


def _value_in_millions(series) -> np.ndarray:
    """Convert market value to €M regardless of original scale."""
    vals = series.astype(float).values
    # auto-detect: if median > 1_000_000 assume raw euros
    if np.nanmedian(vals) > 1_000_000:
        vals = vals / 1_000_000
    return vals


def plot_performance_vs_value(
    df,
    perf_cols: list[str],
    value_col: str = "market_value_eur",
    name_col: str = "player",
    role_col: str | None = "position",
    role_filter: str | None = None,
    top_n_labels: int = 10,
    figsize: tuple = (12, 8),
    save_path: str | None = None,
):
    """
    Scatter: composite performance score (x-axis) vs market value in €M (y-axis).

    Quadrant interpretation
    ───────────────────────
    Top-left  → Overpriced   (low perf, high value)
    Top-right → Elite        (high perf, high value)
    Bot-left  → Developing   (low perf, low value)
    Bot-right → Underrated   (high perf, low value)  ← bargain targets
    """
    data = df.copy()

    # optional role filter
    if role_filter and role_col and role_col in data.columns:
        data = data[data[role_col] == role_filter].reset_index(drop=True)
        if data.empty:
            raise ValueError(f"No rows found for role_filter='{role_filter}'.")

    # build axes values
    perf  = _composite_score(data, perf_cols)
    value = _value_in_millions(data[value_col])

    # assign colours
    if role_col and role_col in data.columns:
        colors = [
            ROLE_COLORS.get(r, ROLE_COLORS["Other"])
            for r in data[role_col].fillna("Other")
        ]
    else:
        colors = [ROLE_COLORS["Other"]] * len(data)

    #figure
    fig, ax = plt.subplots(figsize=figsize, facecolor="#0d1117")
    ax.set_facecolor("#161b22")

    # quadrant dividers (medians)
    med_perf  = np.nanmedian(perf)
    med_value = np.nanmedian(value)

    ax.axvline(med_perf,  color="#30363d", linewidth=1.2, linestyle="--", zorder=1)
    ax.axhline(med_value, color="#30363d", linewidth=1.2, linestyle="--", zorder=1)

    # quadrant labels
    quad_kw = dict(fontsize=9, alpha=0.45, color="white", fontstyle="italic")
    x_lo, x_hi = ax.get_xlim() if ax.get_xlim() != (0, 1) else (perf.min(), perf.max())
    v_lo, v_hi = value.min(), value.max()

    ax.text(med_perf * 0.50, med_value + (v_hi - med_value) * 0.6,
            "Overpriced",   ha="center", **quad_kw)
    ax.text(med_perf * 1.50 if med_perf < 0.9 else med_perf * 1.05,
            med_value + (v_hi - med_value) * 0.6,
            "Elite",        ha="center", **quad_kw)
    ax.text(med_perf * 0.50, med_value * 0.4,
            "Developing",   ha="center", **quad_kw)
    ax.text(med_perf * 1.50 if med_perf < 0.9 else med_perf * 1.05,
            med_value * 0.4,
            "Underrated ⭐", ha="center", **quad_kw)

    # scatter
    scatter = ax.scatter(
        perf, value,
        c=colors,
        s=80, alpha=0.82,
        edgecolors="white", linewidths=0.4,
        zorder=3,
    )

    #top_n_labels most extreme players
    if name_col in data.columns and top_n_labels > 0:
        p_norm = (perf  - med_perf)  / (perf.max()  - perf.min()  + 1e-9)
        v_norm = (value - med_value) / (value.max() - value.min() + 1e-9)
        extremeness = np.sqrt(p_norm**2 + v_norm**2)

        top_idx = np.argsort(extremeness)[-top_n_labels:]
        names   = data[name_col].values

        for i in top_idx:
            ax.annotate(
                names[i],
                xy=(perf[i], value[i]),
                xytext=(6, 4),
                textcoords="offset points",
                fontsize=7.5,
                color="white",
                alpha=0.9,
            )

    #axes styling
    ax.set_xlabel("Composite Performance Score  →  Better", color="#8b949e",
                  fontsize=11, labelpad=10)
    ax.set_ylabel("Market Value (€M)  →  More Expensive", color="#8b949e",
                  fontsize=11, labelpad=10)
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")

    #title
    subtitle = f" – {role_filter}" if role_filter else ""
    ax.set_title(
        f"Performance vs Market Value{subtitle}",
        color="white", fontsize=15, fontweight="bold", pad=16,
    )

    #legend
    if role_col and role_col in data.columns:
        roles_present = data[role_col].dropna().unique()
        handles = [
            mpatches.Patch(facecolor=ROLE_COLORS.get(r, ROLE_COLORS["Other"]),
                           label=r, edgecolor="white", linewidth=0.4)
            for r in roles_present
        ]
        ax.legend(
            handles=handles,
            loc="upper left",
            framealpha=0.25,
            facecolor="#161b22",
            edgecolor="#30363d",
            labelcolor="white",
            fontsize=9,
        )

    # performance stat list as figure text
    stat_text = "Stats: " + ", ".join(
        c for c in perf_cols if c in df.columns
    )
    fig.text(0.5, 0.01, stat_text, ha="center", fontsize=7.5,
             color="#484f58", style="italic")

    plt.tight_layout(rect=[0, 0.03, 1, 1])

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  Saved → {save_path}")

    plt.show()
    return fig, ax
