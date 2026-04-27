"""
radar_chart.py
==============
Multi-player radar / spider chart for football-analytics.
Place this file in:  scripts/radar_chart.py

Usage (from a notebook or terminal):
    from scripts.radar_chart import plot_radar
    OR
    python scripts/radar_chart.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import pandas as pd
from pathlib import Path


# ── Role presets ─────────────────────────────────────────────────────────────
# Six best stats per tactical role, matching your exact column names.
# Pass stats=None to the function and it picks from here automatically.

ROLE_STATS = {
    "Striker": [
        "Goals Scored (Per90)",
        "Expected Goals (xG) (Per90)",
        "Shots On Target (Per90)",
        "Goal Involvement (Per90)",
        "Dribble Success Rate",
        "Aerial Duels Won (Per90)",
    ],
    "Winger": [
        "Goals Scored (Per90)",
        "Assists (Per90)",
        "Successful Dribbles (Per90)",
        "Key Passes (Per90)",
        "Successful Crosses (Per90)",
        "Expected Assists (xA) (Per90)",
    ],
    "Attacking Midfielder": [
        "Goal Involvement (Per90)",
        "Key Passes (Per90)",
        "Expected Assists (xA) (Per90)",
        "Successful Dribbles (Per90)",
        "Pass Completion Rate",
        "Shots On Target (Per90)",
    ],
    "Central Midfielder": [
        "Passes (Per90)",
        "Pass Completion Rate",
        "Key Passes (Per90)",
        "Tackles (Per90)",
        "Interceptions (Per90)",
        "Goal Involvement (Per90)",
    ],
    "Mezzala": [
        "Goal Involvement (Per90)",
        "Key Passes (Per90)",
        "Successful Dribbles (Per90)",
        "Pass Completion Rate",
        "Tackles (Per90)",
        "Expected Assists (xA) (Per90)",
    ],
    "Ball Winning Midfielder": [
        "Tackles (Per90)",
        "Interceptions (Per90)",
        "Ground Duels Won (Per90)",
        "Aerial Duels Won (Per90)",
        "Clearances (Per90)",
        "Fouls Committed (Per90)",
    ],
    "Defensive Midfielder": [
        "Tackles (Per90)",
        "Interceptions (Per90)",
        "Pass Completion Rate",
        "Clearances (Per90)",
        "Ground Duels Won (Per90)",
        "Passes (Per90)",
    ],
    "Centre Back": [
        "Aerial Duels Won (Per90)",
        "Clearances (Per90)",
        "Interceptions (Per90)",
        "Tackles (Per90)",
        "Pass Completion Rate",
        "Ground Duels Won (Per90)",
    ],
    "Full Back": [
        "Successful Crosses (Per90)",
        "Tackles (Per90)",
        "Interceptions (Per90)",
        "Assists (Per90)",
        "Dribble Success Rate",
        "Pass Completion Rate",
    ],
    "Goalkeeper": [
        "Clean Sheets",
        "Shots Faced (Per90)",
        "Goals Conceded",
        "Pass Completion Rate",
        "Clearances (Per90)",
        "Aerial Duels Won (Per90)",
    ],
}

# ── Colour palette (one per player) ──────────────────────────────────────────
PLAYER_COLORS = [
    "#e63946",   # red
    "#4cc9f0",   # cyan
    "#f9c74f",   # yellow
    "#90be6d",   # green
    "#f8961e",   # orange
    "#9b5de5",   # purple
    "#f15bb5",   # pink
    "#00bbf9",   # sky blue
]


# ── Core function ─────────────────────────────────────────────────────────────

def plot_radar(
    df: pd.DataFrame,
    players: list,
    role: str = None,
    stats: list = None,
    player_col: str = "Name",
    title: str = None,
    normalize: bool = True,
    show_values: bool = True,
    save_path: str = None,
    figsize: tuple = (9, 9),
):
    """
    Draw a radar/spider chart comparing multiple players.

    Parameters
    ----------
    df          : your clean DataFrame (e.g. ranked_central_midfields.csv)
    players     : list of player name strings — each gets a unique colour
    role        : one of the keys in ROLE_STATS (used if stats=None)
                  e.g. "Mezzala", "Striker", "Centre Back"
    stats       : explicit list of column names (overrides role preset)
                  choose between 4 and 8 stats for best readability
    player_col  : column that holds the player names (default "Name")
    title       : chart title (auto-generated if None)
    normalize   : scale each stat 0–1 relative to ALL rows in df (recommended)
    show_values : annotate each vertex with the raw value
    save_path   : e.g. "data/clean/radar.png" — saves a PNG if provided
    figsize     : matplotlib figure size tuple
    """

    # ── 1. Resolve stats list ─────────────────────────────────────────────
    if stats is None:
        if role is None:
            raise ValueError(
                "Provide either `role` (e.g. 'Mezzala') or an explicit `stats` list."
            )
        if role not in ROLE_STATS:
            raise ValueError(
                f"Unknown role '{role}'. Available roles:\n  "
                + "\n  ".join(ROLE_STATS.keys())
            )
        stats = ROLE_STATS[role]

    if not (3 <= len(stats) <= 10):
        raise ValueError("Please choose between 3 and 10 stats.")

    # ── 2. Subset data ────────────────────────────────────────────────────
    missing = [p for p in players if p not in df[player_col].values]
    if missing:
        print(f"⚠️  Not found in dataframe, skipping: {missing}")
    players = [p for p in players if p not in missing]
    if not players:
        raise ValueError("None of the requested players were found.")

    subset = df[df[player_col].isin(players)].set_index(player_col)[stats].copy()

    # ── 3. Normalise 0–1 against full dataset ─────────────────────────────
    raw = subset.copy()  # keep raw for labels
    if normalize:
        col_min = df[stats].min()
        col_max = df[stats].max()
        denom = (col_max - col_min).replace(0, 1)   # avoid /0
        subset = (subset - col_min) / denom

    # ── 4. Geometry ───────────────────────────────────────────────────────
    N = len(stats)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles_closed = angles + angles[:1]

    # ── 5. Figure ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=figsize, facecolor="#0d1117")
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("#161b22")

    # rotate so first axis points up
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # ── 6. Draw each player ───────────────────────────────────────────────
    for i, player in enumerate(players):
        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        vals = subset.loc[player].tolist()
        vals_closed = vals + vals[:1]
        raw_vals = raw.loc[player].tolist()

        ax.plot(angles_closed, vals_closed, color=color,
                linewidth=2.5, linestyle="solid", zorder=4)
        ax.fill(angles_closed, vals_closed, color=color, alpha=0.15, zorder=3)
        ax.scatter(angles, vals, color=color, s=70, zorder=5, edgecolors="white",
                   linewidths=0.5)

        # vertex value labels
        if show_values:
            for angle, val, raw_val in zip(angles, vals, raw_vals):
                offset = 0.10
                label_r = min(val + offset, 1.05)
                ax.text(
                    angle, label_r,
                    f"{raw_val:.2f}".rstrip("0").rstrip("."),
                    ha="center", va="center",
                    fontsize=7.5, color=color, fontweight="bold",
                    zorder=6,
                )

    # ── 7. Axes & grid ────────────────────────────────────────────────────
    ax.set_xticks(angles)
    # Wrap long stat names
    wrapped = [s.replace(" (Per90)", "\n/90").replace(" Rate", "\nRate")
               for s in stats]
    ax.set_xticklabels(wrapped, color="white", fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", pad=16)

    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"],
                       color="#555", fontsize=7)
    ax.grid(color="#30363d", linestyle="--", linewidth=0.6, alpha=0.8)
    ax.spines["polar"].set_color("#30363d")

    # ── 8. Legend ─────────────────────────────────────────────────────────
    patches = [
        mpatches.Patch(facecolor=PLAYER_COLORS[i % len(PLAYER_COLORS)],
                       edgecolor="white", linewidth=0.5, label=p)
        for i, p in enumerate(players)
    ]
    legend = ax.legend(
        handles=patches,
        loc="upper right",
        bbox_to_anchor=(1.45, 1.18),
        framealpha=0.15,
        facecolor="#0d1117",
        edgecolor="#30363d",
        labelcolor="white",
        fontsize=11,
        title="Players",
        title_fontsize=11,
    )
    plt.setp(legend.get_title(), color="white")

    # ── 9. Title ──────────────────────────────────────────────────────────
    if title is None:
        role_label = role if role else "Custom Stats"
        title = f"{role_label} Comparison"
    ax.set_title(title, color="white", fontsize=14,
                 fontweight="bold", pad=28)

    # ── 10. Footnote ──────────────────────────────────────────────────────
    fig.text(0.5, 0.01,
             "Stats normalised relative to all players in dataset  •  /90 = per 90 minutes",
             ha="center", color="#555", fontsize=8)

    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"✅  Saved → {save_path}")

    plt.show()
    return fig, ax


# ── CLI / quick demo ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # ── Adjust the path to match where you run this from ──
    DATA_PATH = "data/clean/ranked_central_midfields.csv"

    df = pd.read_csv(DATA_PATH)

    print("Columns available:")
    print(df.columns.tolist())
    print("\nPlayers available:")
    print(df["Name"].tolist())

    # ── Example 1: use a role preset ──────────────────────────────────────
    plot_radar(
        df,
        players=["Bruno Guimarães", "Pedri", "Frenkie de Jong"],
        role="Mezzala",
        title="Mezzala Comparison",
        save_path="data/clean/radar_mezzala.png",
    )

    # ── Example 2: pick your own stats manually ───────────────────────────
    # plot_radar(
    #     df,
    #     players=["Bruno Guimarães", "Pedri"],
    #     stats=[
    #         "Passes (Per90)",
    #         "Pass Completion Rate",
    #         "Key Passes (Per90)",
    #         "Goal Involvement (Per90)",
    #         "Tackles (Per90)",
    #         "Successful Dribbles (Per90)",
    #     ],
    #     title="Custom Stat Comparison",
    # )