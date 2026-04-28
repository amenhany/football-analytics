"""
radar_chart.py
==============
Multi-player radar / spider chart for football-analytics.
Place this file in:  scripts/radar_chart.py

Usage (from a notebook or terminal):
    from scripts.radar_chart import plot_radar, list_roles
    OR
    python scripts/radar_chart.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from pathlib import Path


# ── Tactical role configs (mirrors your config.py structure) ─────────────────

outfield_config = {
    # CENTRE BACK
    "Centre-Back": {
        "Positions": ["Centre-Back"],
        "Aerial Stopper": {
            "Aerial Duels Won (Per90)": 0.55,
            "Clearances (Per90)": 0.25,
            "Shots Blocked (Per90)": 0.20,
        },
        "Ball Playing Defender": {
            "Pass Completion Rate": 0.40,
            "Successful Passes (Per90)": 0.30,
            "Key Passes (Per90)": 0.30,
        },
        "Defensive Sweeper": {
            "Interceptions (Per90)": 0.40,
            "Tackles (Per90)": 0.35,
            "Ground Duels Won (Per90)": 0.25,
        },
    },
    # FULL BACK
    "Full-Back": {
        "Positions": ["Left-Back", "Right-Back"],
        "Wing Back": {
            "Successful Crosses (Per90)": 0.30,
            "Expected Assists (xA) (Per90)": 0.30,
            "Successful Dribbles (Per90)": 0.25,
            "Key Passes (Per90)": 0.15,
        },
        "Inverted Full Back": {
            "Pass Completion Rate": 0.40,
            "Successful Passes (Per90)": 0.25,
            "Ground Duels Won (Per90)": 0.20,
            "Interceptions (Per90)": 0.15,
        },
        "Defensive Full Back": {
            "Tackles (Per90)": 0.40,
            "Interceptions (Per90)": 0.35,
            "Clearances (Per90)": 0.25,
        },
    },
    # DEFENSIVE MIDFIELD
    "Defensive Midfield": {
        "Positions": ["Defensive Midfield"],
        "Anchor Man": {
            "Interceptions (Per90)": 0.45,
            "Shots Blocked (Per90)": 0.30,
            "Clearances (Per90)": 0.25,
        },
        "Deep Lying Playmaker": {
            "Pass Completion Rate": 0.40,
            "Successful Passes (Per90)": 0.25,
            "Key Passes (Per90)": 0.35,
        },
        "Ball Winning Midfielder": {
            "Tackles (Per90)": 0.50,
            "Ground Duels Won (Per90)": 0.50,
        },
    },
    # CENTRAL MIDFIELD
    "Central Midfield": {
        "Positions": ["Central Midfield"],
        "Mezzala": {
            "Expected Assists (xA) (Per90)": 0.30,
            "Expected Goals (xG) (Per90)": 0.25,
            "Key Passes (Per90)": 0.25,
            "Successful Dribbles (Per90)": 0.20,
        },
        "Ball Winning Midfielder": {
            "Tackles (Per90)": 0.40,
            "Interceptions (Per90)": 0.35,
            "Ground Duels Won (Per90)": 0.25,
        },
    },
    # ATTACKING MIDFIELD
    "Attacking Midfield": {
        "Positions": ["Attacking Midfield"],
        "Shadow Striker": {
            "Goals Scored (Per90)": 0.40,
            "Expected Goals (xG) (Per90)": 0.35,
            "Shots On Target (Per90)": 0.25,
        },
        "Playmaker": {
            "Key Passes (Per90)": 0.40,
            "Expected Assists (xA) (Per90)": 0.40,
            "Successful Passes (Per90)": 0.20,
        },
    },
    # WINGER
    "Winger": {
        "Positions": ["Left Winger", "Right Winger", "Left Midfield"],
        "Inside Forward": {
            "Expected Goals (xG) (Per90)": 0.35,
            "Goals Scored (Per90)": 0.30,
            "Shots Taken (Per90)": 0.20,
            "Successful Dribbles (Per90)": 0.15,
        },
        "Traditional Winger": {
            "Successful Crosses (Per90)": 0.55,
            "Expected Assists (xA) (Per90)": 0.25,
            "Key Passes (Per90)": 0.20,
        },
    },
    # STRIKER
    "Striker": {
        "Positions": ["Centre-Forward", "Second Striker"],
        "Poacher": {
            "Goals Scored (Per90)": 0.50,
            "Expected Goals (xG) (Per90)": 0.30,
            "Shots On Target (Per90)": 0.20,
        },
        "Target Man": {
            "Aerial Duels Won (Per90)": 0.50,
            "Ground Duels Won (Per90)": 0.30,
            "Shots Taken (Per90)": 0.20,
        },
        "False Nine": {
            "Expected Assists (xA) (Per90)": 0.35,
            "Key Passes (Per90)": 0.35,
            "Successful Passes (Per90)": 0.20,
            "Successful Dribbles (Per90)": 0.10,
        },
    },
}

gk_config = {
    "Goalkeeper": {
        "Positions": ["Goalkeeper"],
        "Shot Stopper": {
            "Save Percentage": 0.55,
            "Saves (Per90)": 0.35,
            "Punches (Per90)": 0.10,
        },
        "Sweeper Keeper": {
            "Interceptions (Per90)": 0.40,
            "Clearances (Per90)": 0.25,
            "Pass Completion Rate": 0.20,
            "Successful Passes (Per90)": 0.15,
        },
    }
}


# ── Build flat lookup: "Position / Role" → [stat1, stat2, ...] ───────────────

def _build_role_stats(config: dict) -> dict:
    result = {}
    for position, data in config.items():
        for key, value in data.items():
            if key == "Positions":
                continue
            result[f"{position} / {key}"] = list(value.keys())
    return result

ROLE_STATS = {
    **_build_role_stats(outfield_config),
    **_build_role_stats(gk_config),
}


# ── Colour palette ────────────────────────────────────────────────────────────

PLAYER_COLORS = [
    "#e63946",  # red
    "#4cc9f0",  # cyan
    "#f9c74f",  # yellow
    "#90be6d",  # green
    "#f8961e",  # orange
    "#9b5de5",  # purple
    "#f15bb5",  # pink
    "#00bbf9",  # sky blue
]


# ── Helper ────────────────────────────────────────────────────────────────────

def list_roles():
    """Print every role string you can pass as role= to plot_radar."""
    print("Available roles:\n")
    for key, stats in ROLE_STATS.items():
        print(f"  '{key}'")
        for s in stats:
            print(f"      • {s}")
        print()


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
    role        : tactical role in format "Position / Role"
                    e.g. "Central Midfield / Mezzala"
                    e.g. "Striker / Poacher"
                    e.g. "Full-Back / Wing Back"
                  Run list_roles() to print every option.
    stats       : explicit list of column names — overrides role if given
    player_col  : column that holds player names (default "Name")
    title       : chart title — auto-generated from role if omitted
    normalize   : scale each stat 0–1 relative to ALL rows in df
    show_values : annotate each vertex with the raw stat value
    save_path   : path to save PNG, e.g. "../data/clean/radar.png"
    figsize     : matplotlib figure size tuple
    """

    # ── 1. Resolve stats ──────────────────────────────────────────────────
    if stats is None:
        if role is None:
            raise ValueError(
                "Provide either role= (e.g. 'Central Midfield / Mezzala') "
                "or an explicit stats= list.\n"
                "Call list_roles() to see every option."
            )
        if role not in ROLE_STATS:
            raise ValueError(
                f"Unknown role: '{role}'\n"
                "Call list_roles() to see every option."
            )
        stats = ROLE_STATS[role]

    if not (2 <= len(stats) <= 10):
        raise ValueError("Choose between 2 and 10 stats.")

    # ── 2. Validate players ───────────────────────────────────────────────
    missing_players = [p for p in players if p not in df[player_col].values]
    if missing_players:
        print(f"⚠️  Not found, skipping: {missing_players}")
    players = [p for p in players if p not in missing_players]
    if not players:
        raise ValueError("None of the requested players were found.")

    # ── 3. Validate stats ─────────────────────────────────────────────────
    missing_stats = [s for s in stats if s not in df.columns]
    if missing_stats:
        raise ValueError(
            f"These stats are not columns in your dataframe:\n  {missing_stats}"
        )

    # ── 4. Subset & normalise ─────────────────────────────────────────────
    subset = df[df[player_col].isin(players)].set_index(player_col)[stats].copy()
    raw = subset.copy()

    if normalize:
        col_min = df[stats].min()
        col_max = df[stats].max()
        denom = (col_max - col_min).replace(0, 1)
        subset = (subset - col_min) / denom

    # ── 5. Geometry ───────────────────────────────────────────────────────
    N = len(stats)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles_closed = angles + angles[:1]

    # ── 6. Figure & axes ──────────────────────────────────────────────────
    fig = plt.figure(figsize=figsize, facecolor="#0d1117")
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("#161b22")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # ── 7. Draw players ───────────────────────────────────────────────────
    for i, player in enumerate(players):
        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        vals = subset.loc[player].tolist()
        vals_closed = vals + vals[:1]
        raw_vals = raw.loc[player].tolist()

        ax.plot(angles_closed, vals_closed, color=color,
                linewidth=2.5, linestyle="solid", zorder=4)
        ax.fill(angles_closed, vals_closed, color=color, alpha=0.15, zorder=3)
        ax.scatter(angles, vals, color=color, s=70, zorder=5,
                   edgecolors="white", linewidths=0.5)

        if show_values:
            for angle, val, raw_val in zip(angles, vals, raw_vals):
                label_r = min(val + 0.10, 1.08)
                label = f"{raw_val:.2f}".rstrip("0").rstrip(".")
                ax.text(angle, label_r, label,
                        ha="center", va="center",
                        fontsize=7.5, color=color,
                        fontweight="bold", zorder=6)

    # ── 8. Axis styling ───────────────────────────────────────────────────
    ax.set_xticks(angles)
    wrapped = [
        s.replace(" (Per90)", "\n/90")
         .replace(" Rate", "\nRate")
         .replace(" Percentage", "\n%")
        for s in stats
    ]
    ax.set_xticklabels(wrapped, color="white", fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", pad=16)

    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], color="#555", fontsize=7)
    ax.grid(color="#30363d", linestyle="--", linewidth=0.6, alpha=0.8)
    ax.spines["polar"].set_color("#30363d")

    # ── 9. Legend ─────────────────────────────────────────────────────────
    patches = [
        mpatches.Patch(
            facecolor=PLAYER_COLORS[i % len(PLAYER_COLORS)],
            edgecolor="white", linewidth=0.5, label=p
        )
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

    # ── 10. Title & footnote ──────────────────────────────────────────────
    if title is None:
        title = role if role else "Player Comparison"
    ax.set_title(title, color="white", fontsize=14, fontweight="bold", pad=28)

    fig.text(
        0.5, 0.01,
        "Stats normalised relative to all players in dataset  •  /90 = per 90 minutes",
        ha="center", color="#555", fontsize=8,
    )

    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"✅  Saved → {save_path}")

    plt.show()
    return fig, ax


# ── CLI demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    list_roles()

    df = pd.read_csv("data/clean/ranked_central_midfields.csv")

    plot_radar(
        df,
        players=["Bruno Guimarães", "Pedri", "Frenkie de Jong"],
        role="Central Midfield / Mezzala",
        title="Mezzala Comparison",
        save_path="data/clean/radar_mezzala.png",
    )