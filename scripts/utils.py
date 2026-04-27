import numpy as np
import pandas as pd
import re

def money_to_int(x):
    if pd.isna(x):
        return np.nan

    if isinstance(x, (int, float)):
        return x

    x = str(x).replace("€","").replace(",","").lower()

    if "m" in x:
        return float(x.replace("m","")) * 1_000_000
    if "k" in x:
        return float(x.replace("k","")) * 1_000

    return float(x)

def percent_to_float(x):
    if pd.isna(x):
        return np.nan

    if isinstance(x, str) and "%" in x:
        return float(x.replace("%","")) / 100

    return x

def minutes_to_int(x): #removes min and return the value as int
    if isinstance(x, str):
        nums = re.findall(r'\d+', x)
        return int(nums[0]) if nums else np.nan
    return x

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_radar(
    df,
    players: list,
    stats: list,
    player_col: str = "Player",
    title: str = "Player Comparison",
    normalize: bool = True,
    save_path: str = None,
):
    """
    Multi-player radar/spider chart.

    Parameters
    ----------
    df         : cleaned DataFrame (from data/clean/)
    players    : list of player name strings
    stats      : list of 4-8 column names to plot
    player_col : column that holds player names
    normalize  : scale each stat 0–1 relative to full dataset
    save_path  : optional path to save PNG, e.g. "data/clean/radar.png"
    """
    data = df[df[player_col].isin(players)].set_index(player_col)[stats].copy()

    if normalize:
        mins = df[stats].min()
        maxs = df[stats].max()
        data = (data - mins) / (maxs - mins)

    N = len(stats)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # close the loop

    COLORS = [
        "#e63946", "#457b9d", "#2a9d8f",
        "#e9c46a", "#f4a261", "#a8dadc",
        "#6a4c93", "#ffffff",
    ]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")

    for i, player in enumerate(players):
        if player not in data.index:
            print(f"⚠️  '{player}' not found — skipping.")
            continue
        values = data.loc[player].tolist() + data.loc[player].tolist()[:1]
        color = COLORS[i % len(COLORS)]
        ax.plot(angles, values, color=color, linewidth=2.5)
        ax.fill(angles, values, color=color, alpha=0.15)
        # dot on each vertex
        ax.scatter(angles[:-1], values[:-1], color=color, s=60, zorder=5)

    # Axis labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(stats, color="white", fontsize=11, fontweight="bold")
    ax.set_yticklabels([])
    ax.tick_params(pad=18)

    # Grid
    ax.set_ylim(0, 1)
    ax.grid(color="white", linestyle="--", linewidth=0.4, alpha=0.4)
    ax.spines["polar"].set_color("#30363d")

    # Gridline rings labels (0%, 50%, 100%)
    for r, label in zip([0.5, 1.0], ["50%", "100%"]):
        ax.text(0, r, label, color="gray", fontsize=8, ha="center", va="center")

    # Legend
    patches = [
        mpatches.Patch(color=COLORS[i % len(COLORS)], label=p)
        for i, p in enumerate(players)
    ]
    ax.legend(
        handles=patches,
        loc="upper right",
        bbox_to_anchor=(1.35, 1.15),
        framealpha=0.1,
        labelcolor="white",
        fontsize=11,
    )

    ax.set_title(title, color="white", fontsize=15, fontweight="bold", pad=25)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"Saved to {save_path}")
    plt.show()