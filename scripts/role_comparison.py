"""
Role Comparison for a Specific Player

Shows how well a chosen player fits different roles by scoring them
against the top-N players in each role and displaying the results
as a horizontal bar chart.

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# role colour palette 
ROLE_COLORS = {
    "Forward":    "#e63946",
    "Midfielder": "#457b9d",
    "Defender":   "#2a9d8f",
    "Goalkeeper": "#e9c46a",
}
DEFAULT_COLOR = "#adb5bd"

# default stat sets per role (overridable via role_stats param)
DEFAULT_ROLE_STATS: dict[str, list[str]] = {
    "Forward": [
        "goals", "assists", "shots_on_target",
        "dribbles_completed", "key_passes", "xg",
    ],
    "Midfielder": [
        "key_passes", "assists", "pass_accuracy",
        "dribbles_completed", "tackles", "progressive_passes",
    ],
    "Defender": [
        "tackles", "interceptions", "clearances",
        "aerial_duels_won", "blocks", "pass_accuracy",
    ],
    "Goalkeeper": [
        "saves", "clean_sheets", "save_percentage",
        "goals_conceded", "passes_completed", "long_ball_accuracy",
    ],
}


def _role_score(
    player_row,
    role_df,
    stats: list[str],
) -> tuple[float, dict[str, float]]:
    """
    Score a player for a given role by percentile-ranking them
    against the role_df pool on each relevant stat.

    Returns
    -------
    overall_score : float  in [0, 100]
    per_stat      : dict   {stat: percentile}
    """
    percentiles = {}
    valid_stats = [s for s in stats if s in role_df.columns and s in player_row.index]

    if not valid_stats:
        return 0.0, {}

    for stat in valid_stats:
        pool  = role_df[stat].astype(float).dropna().values
        p_val = float(player_row[stat])
        if len(pool) == 0 or np.isnan(p_val):
            percentiles[stat] = 0.0
            continue
        # for "conceded"-style stats (lower is better) we invert
        lower_is_better = any(kw in stat for kw in ("conceded", "errors", "fouls"))
        pct = float(np.mean(pool <= p_val) * 100)
        percentiles[stat] = (100 - pct) if lower_is_better else pct

    overall = float(np.mean(list(percentiles.values()))) if percentiles else 0.0
    return overall, percentiles


def plot_role_comparison(
    df,
    player_name: str,
    name_col: str = "player",
    role_col: str = "position",
    roles: list[str] | None = None,
    role_stats: dict[str, list[str]] | None = None,
    top_n: int = 30,
    figsize: tuple = (13, 8),
    save_path: str | None = None,
):
    """
    Two-panel figure:
      Left  – overall role suitability bar chart
      Right – per-stat percentile breakdown for the best-fit role
    """
    #resolve inputs 
    stats_map = {**(DEFAULT_ROLE_STATS), **(role_stats or {})}
    if roles is None:
        roles = [r for r in stats_map if r in df[role_col].unique()] \
                if role_col in df.columns else list(stats_map.keys())

    #find player row
    mask = df[name_col].str.strip().str.lower() == player_name.strip().lower()
    if not mask.any():
        raise ValueError(
            f"Player '{player_name}' not found. "
            f"Check spelling or the name_col='{name_col}' parameter."
        )
    player_row = df[mask].iloc[0]
    actual_name = player_row[name_col]

    #score player against each role 
    overall_scores: dict[str, float] = {}
    per_stat_scores: dict[str, dict[str, float]] = {}

    for role in roles:
        stats = stats_map.get(role, [])
        if not stats:
            continue

        # build comparison pool: top_n players in this role
        if role_col in df.columns:
            role_df = df[df[role_col] == role]
        else:
            role_df = df  # no role column → compare against everyone

        # sort by available stats to get the elite pool
        sortable = [s for s in stats if s in role_df.columns]
        if sortable:
            role_df = role_df.nlargest(top_n, sortable[0])
        else:
            role_df = role_df.head(top_n)

        score, per_stat = _role_score(player_row, role_df, stats)
        overall_scores[role]   = score
        per_stat_scores[role]  = per_stat

    if not overall_scores:
        raise ValueError("Could not compute scores – check role_stats column names.")

    best_role     = max(overall_scores, key=overall_scores.get)
    sorted_roles  = sorted(overall_scores, key=overall_scores.get, reverse=True)

    #figure
    fig, (ax_bar, ax_detail) = plt.subplots(
        1, 2,
        figsize=figsize,
        facecolor="#0d1117",
        gridspec_kw={"width_ratios": [1, 1.6]},
    )
    for ax in (ax_bar, ax_detail):
        ax.set_facecolor("#161b22")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")
        ax.tick_params(colors="#8b949e")

    # LEFT: overall role suitability
    bar_colors = [
        ROLE_COLORS.get(r, DEFAULT_COLOR) for r in sorted_roles
    ]
    bars = ax_bar.barh(
        sorted_roles[::-1],
        [overall_scores[r] for r in sorted_roles[::-1]],
        color=bar_colors[::-1],
        edgecolor="#0d1117",
        linewidth=0.6,
        height=0.55,
    )

    # value labels
    for bar, role in zip(bars, sorted_roles[::-1]):
        w = bar.get_width()
        ax_bar.text(
            w + 1, bar.get_y() + bar.get_height() / 2,
            f"{w:.1f}",
            va="center", ha="left",
            color="white", fontsize=10, fontweight="bold",
        )
        # crown on best role
        if role == best_role:
            ax_bar.text(
                w + 6, bar.get_y() + bar.get_height() / 2,
                "  ← Best fit",
                va="center", ha="left",
                color=ROLE_COLORS.get(best_role, DEFAULT_COLOR),
                fontsize=8.5, fontstyle="italic",
            )

    ax_bar.set_xlim(0, 115)
    ax_bar.set_xlabel("Role Suitability Score  (percentile avg)",
                       color="#8b949e", fontsize=9)
    ax_bar.set_title("Role Fit Overview", color="white", fontsize=12,
                     fontweight="bold", pad=10)
    ax_bar.xaxis.set_tick_params(labelcolor="#8b949e")
    ax_bar.yaxis.set_tick_params(labelcolor="white", labelsize=11)
    ax_bar.axvline(50, color="#30363d", linewidth=0.8, linestyle=":")

    #RIGHT: per-stat breakdown for best role 
    best_stats = per_stat_scores.get(best_role, {})
    if best_stats:
        stat_names  = list(best_stats.keys())
        stat_values = [best_stats[s] for s in stat_names]

        best_color = ROLE_COLORS.get(best_role, DEFAULT_COLOR)

        y_pos = np.arange(len(stat_names))
        h_bars = ax_detail.barh(
            y_pos, stat_values,
            color=best_color,
            alpha=0.85,
            edgecolor="#0d1117",
            linewidth=0.6,
            height=0.55,
        )

        # background full-width bars
        ax_detail.barh(
            y_pos, [100] * len(stat_names),
            color="#21262d", height=0.55,
            edgecolor="#30363d", linewidth=0.4,
            zorder=0,
        )
        for bar_bg in ax_detail.patches[len(stat_names):]:
            bar_bg.set_zorder(0)

        # value labels
        for i, (bar, val) in enumerate(zip(h_bars, stat_values)):
            ax_detail.text(
                val + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}th",
                va="center", ha="left",
                color="white", fontsize=9,
            )

        ax_detail.set_yticks(y_pos)
        ax_detail.set_yticklabels(
            [s.replace("_", " ").title() for s in stat_names],
            color="white", fontsize=10,
        )
        ax_detail.set_xlim(0, 115)
        ax_detail.set_xlabel("Percentile vs Top Players in Role",
                              color="#8b949e", fontsize=9)
        ax_detail.set_title(
            f"Stat Breakdown as {best_role}",
            color=best_color, fontsize=12, fontweight="bold", pad=10,
        )
        ax_detail.axvline(50,  color="#30363d", linewidth=0.8, linestyle=":")
        ax_detail.axvline(75,  color="#30363d", linewidth=0.6, linestyle=":")
        ax_detail.axvline(90,  color="#30363d", linewidth=0.6, linestyle=":")

    #main title 
    fig.suptitle(
        f"Role Comparison – {actual_name}",
        color="white", fontsize=16, fontweight="bold", y=1.01,
    )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  Saved → {save_path}")

    plt.show()
    return fig, (ax_bar, ax_detail)
