import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Pitch IQ", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.components.v1.html("""
<script>
(function() {
    function hideCollapseBtn() {
        var btns = window.parent.document.querySelectorAll(
            '[data-testid="collapsedControl"], button[kind="header"]'
        );
        btns.forEach(function(b) { b.style.display = 'none'; });
    }
    hideCollapseBtn();
    var observer = new MutationObserver(hideCollapseBtn);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", height=0)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:      #080c10;
    --surface: #0f1419;
    --surface2:#161d26;
    --border:  #1e2a38;
    --accent:  #00e676;
    --accent2: #00b0ff;
    --gold:    #ffd740;
    --red:     #ff5252;
    --text:    #e8edf2;
    --muted:   #5a6a7a;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] .block-container { padding: 1rem !important; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="collapsedControl"] { display: none !important; }

[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}
.stTextInput input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,230,118,0.15) !important;
}
.stSlider [data-baseweb="slider"] { padding: 0 !important; }

[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.1rem 1.4rem !important;
}
[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2rem !important;
    letter-spacing: 0.02em !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.2rem !important;
    letter-spacing: 0.03em !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

label, .stSelectbox label, .stMultiSelect label,
.stSlider label, .stTextInput label, .stRadio label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.scout-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
}

.sim-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}

.quadrant-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly base theme ──────────────────────────────────────────────────────
THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#e8edf2", size=12),
    colorway=["#00e676","#00b0ff","#ffd740","#ff5252","#bc8cff","#ff6d00"],
    xaxis=dict(gridcolor="#1e2a38", linecolor="#1e2a38", zeroline=False, tickfont=dict(color="#5a6a7a")),
    yaxis=dict(gridcolor="#1e2a38", linecolor="#1e2a38", zeroline=False, tickfont=dict(color="#5a6a7a")),
    legend=dict(bgcolor="rgba(15,20,25,0.8)", bordercolor="#1e2a38", borderwidth=1, font=dict(color="#e8edf2")),
    margin=dict(t=40, l=10, r=10, b=10),
    title_font=dict(family="Bebas Neue, sans-serif", color="#e8edf2", size=18),
)

# ── Data loading ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base_clean = "data/clean"
    base_proc  = "data/processed"

    df_master = pd.read_csv(f"{base_proc}/master_player_ranking_1500min.csv")
    df_full   = pd.read_csv(f"{base_clean}/master_player_ranking.csv")
    df_gk     = pd.read_csv(f"{base_clean}/classified_goalkeepers.csv")
    df_pred   = pd.read_csv(f"{base_proc}/all_player_predictions.csv")

    pos_files = {
        "Centre-Back":        f"{base_proc}/value_ranked_centre-backs_1500min.csv",
        "Full-Back":          f"{base_proc}/value_ranked_full-backs_1500min.csv",
        "Defensive Midfield": f"{base_proc}/value_ranked_defensive_midfields_1500min.csv",
        "Central Midfield":   f"{base_proc}/value_ranked_central_midfields_1500min.csv",
        "Attacking Midfield": f"{base_proc}/value_ranked_attacking_midfields_1500min.csv",
        "Winger":             f"{base_proc}/value_ranked_wingers_1500min.csv",
        "Striker":            f"{base_proc}/value_ranked_strikers_1500min.csv",
    }
    pos_dfs = {k: pd.read_csv(v) for k, v in pos_files.items()}

    for df in [df_master, df_full] + list(pos_dfs.values()):
        if "Unnamed: 0" in df.columns:
            df.drop(columns=["Unnamed: 0"], inplace=True)
    if "Unnamed: 0" in df_gk.columns:
        df_gk.drop(columns=["Unnamed: 0"], inplace=True)

    for col in ["Market Value", "Age"]:
        df_master[col] = pd.to_numeric(df_master[col], errors="coerce")
        df_full[col]   = pd.to_numeric(df_full[col],   errors="coerce")
        df_gk[col]     = pd.to_numeric(df_gk[col],     errors="coerce")

    df_full   = df_full.merge(df_pred[["Name", "Predicted_Market_Value"]], on="Name", how="left")
    df_master = df_master.merge(df_pred[["Name", "Predicted_Market_Value"]], on="Name", how="left")
    df_full["Value_Gap"]   = df_full["Predicted_Market_Value"]   - df_full["Market Value"]
    df_master["Value_Gap"] = df_master["Predicted_Market_Value"] - df_master["Market Value"]

    df_gk["GK_Role"] = df_gk.apply(
        lambda r: "Sweeper Keeper"
        if pd.notna(r.get("Sweeper Keeper_Score")) and pd.notna(r.get("Shot Stopper_Score"))
           and r["Sweeper Keeper_Score"] > r["Shot Stopper_Score"]
        else "Shot Stopper", axis=1
    )

    league_map = {"premier-league": "Premier League", "la-liga": "La Liga"}
    for df in [df_master, df_full]:
        df["League_Label"] = df["League"].map(league_map).fillna(df["League"])
    df_gk["League_Label"] = df_gk["League"].map(league_map).fillna(df_gk["League"])

    # ── Build combined dataset for similarity engine ───────────────────────
    # Add GK_Role column to outfield with NaN, and Tactical_Role to GK with NaN
    df_full_sim = df_full.copy()
    df_gk_sim   = df_gk.copy()

    common = sorted(set(df_full_sim.columns) & set(df_gk_sim.columns))
    df_all = pd.concat([df_full_sim[common], df_gk_sim[common]], ignore_index=True)

    # Traditional position grouping for performance scatter
    def trad_pos(row):
        pos = row.get("Position", "")
        if pd.isna(pos): return "Unknown"
        if pos in ["Striker", "Winger", "Attacking Midfield"]: return "Forward"
        if pos in ["Central Midfield", "Defensive Midfield"]:  return "Midfielder"
        if pos in ["Centre-Back", "Full-Back"]:                return "Defender"
        return "Unknown"

    df_full["Trad_Position"] = df_full.apply(trad_pos, axis=1)
    df_master["Trad_Position"] = df_master.apply(trad_pos, axis=1)

    return df_master, df_full, df_gk, df_pred, pos_dfs, df_all

df_master, df_full, df_gk, df_pred, pos_dfs, df_all = load_data()

# ── Feature columns for similarity ────────────────────────────────────────
PER90_COLS   = [c for c in df_all.columns if "Per90" in c]
RATE_COLS    = [c for c in df_all.columns if any(k in c for k in ["Rate", "Accuracy", "Percentage"]) and "Per90" not in c]
FEATURE_COLS = [c for c in PER90_COLS + RATE_COLS if c in df_all.columns]

RADAR_METRICS = [
    "Goals Scored (Per90)",
    "Assists (Per90)",
    "Key Passes (Per90)",
    "Tackles (Per90)",
    "Interceptions (Per90)",
    "Successful Dribbles (Per90)",
    "Shots On Target (Per90)",
    "Pass Completion Rate",
    "Expected Goals (xG) (Per90)",
    "Expected Assists (xA) (Per90)",
    "Aerial Duels Won (Per90)",
    "Clearances (Per90)",
]
RADAR_METRICS = [m for m in RADAR_METRICS if m in df_all.columns]

# ── Formatting helpers ─────────────────────────────────────────────────────
def fmt_val(v):
    if pd.isna(v): return "N/A"
    if v >= 1e9:   return f"€{v/1e9:.2f}B"
    if v >= 1e6:   return f"€{v/1e6:.1f}M"
    if v >= 1e3:   return f"€{v/1e3:.0f}K"
    return f"€{v:.0f}"

def fmt_gap(v):
    if pd.isna(v): return "N/A"
    sign = "+" if v >= 0 else "-"
    return f"{sign}{fmt_val(abs(v))}"

def fmt_pct(v, already_pct=False):
    if pd.isna(v): return "—"
    if not already_pct and v <= 1:
        return f"{v*100:.1f}%"
    return f"{v:.1f}%"

def card(label, value, sub=None, color="#00e676"):
    sub_html = f"<div style='font-size:0.72rem;color:#5a6a7a;margin-top:2px'>{sub}</div>" if sub else ""
    return (
        f"<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1.1rem 1.4rem'>"
        f"<div style='font-size:0.65rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>{label}</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.9rem;letter-spacing:0.02em;color:{color}'>{value}</div>"
        f"{sub_html}</div>"
    )

def section_header(text, sub=None):
    sub_html = f"<div style='font-size:0.85rem;color:#5a6a7a;margin-top:4px;font-weight:400'>{sub}</div>" if sub else ""
    st.markdown(
        f"<div style='margin:2rem 0 1.2rem 0'>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;letter-spacing:0.05em;color:#e8edf2'>{text}</div>"
        f"{sub_html}</div>",
        unsafe_allow_html=True
    )

def scout_player_card(row, badge_label, badge_color, stat_line):
    mv    = fmt_val(row.get("Market Value", np.nan))
    score = f"{row.get('Performance_Score', 0):.1f}" if pd.notna(row.get("Performance_Score")) else "—"
    pos   = row.get("Position", row.get("GK_Role", "Goalkeeper"))
    role  = row.get("Tactical_Role", row.get("GK_Role", ""))
    return (
        f"<div class='scout-card'>"
        f"<div style='display:flex;align-items:flex-start;justify-content:space-between'>"
        f"<div>"
        f"<span style='background:{badge_color}22;color:{badge_color};font-size:0.65rem;font-weight:700;"
        f"letter-spacing:0.1em;text-transform:uppercase;padding:2px 8px;border-radius:4px;"
        f"border:1px solid {badge_color}44'>{badge_label}</span>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.3rem;letter-spacing:0.04em;"
        f"color:#e8edf2;margin-top:6px;line-height:1'>{row.get('Name','')}</div>"
        f"<div style='font-size:0.78rem;color:#5a6a7a;margin-top:3px'>"
        f"{row.get('Team','')} &nbsp;·&nbsp; {pos} &nbsp;·&nbsp; {role}</div>"
        f"</div>"
        f"<div style='text-align:right;flex-shrink:0;margin-left:1rem'>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.4rem;color:{badge_color}'>{score}</div>"
        f"<div style='font-size:0.65rem;color:#5a6a7a;letter-spacing:0.06em;text-transform:uppercase'>Score</div>"
        f"<div style='font-size:0.85rem;color:#e8edf2;margin-top:4px;font-weight:500'>{mv}</div>"
        f"</div></div>"
        f"<div style='font-size:0.78rem;color:#5a6a7a;margin-top:8px;padding-top:8px;border-top:1px solid #1e2a38'>{stat_line}</div>"
        f"</div>"
    )

# ── Similarity engine ──────────────────────────────────────────────────────
def find_similar_players(df, player_name, top_n=10, same_position=False,
                         positions=None, leagues=None, max_age=None,
                         min_minutes=None, max_market_value=None, feature_cols=None):
    if feature_cols is None:
        feature_cols = FEATURE_COLS
    matches = df[df["Name"].str.lower() == player_name.strip().lower()]
    if matches.empty:
        matches = df[df["Name"].str.lower().str.contains(player_name.strip().lower(), na=False)]
    if matches.empty:
        return None, pd.DataFrame()

    ref     = matches.iloc[0]
    ref_pos = ref.get("Position", None)
    pool    = df[df["Name"] != ref["Name"]].copy()

    if same_position and ref_pos:
        pool = pool[pool["Position"] == ref_pos]
    if positions:
        pool = pool[pool["Position"].isin(positions)]
    if leagues and "League" in pool.columns:
        pool = pool[pool["League"].isin(leagues)]
    if max_age and "Age" in pool.columns:
        pool = pool[pd.to_numeric(pool["Age"], errors="coerce") <= max_age]
    if min_minutes and "Minutes" in pool.columns:
        pool = pool[pd.to_numeric(pool["Minutes"], errors="coerce") >= min_minutes]
    if max_market_value and "Market Value" in pool.columns:
        pool = pool[pd.to_numeric(pool["Market Value"], errors="coerce") <= max_market_value]
    if pool.empty:
        return ref, pd.DataFrame()

    available = [c for c in feature_cols if c in pool.columns]
    all_rows  = pd.concat([matches.head(1), pool], ignore_index=True)
    X = all_rows[available].apply(pd.to_numeric, errors="coerce").fillna(0)

    scaler   = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    sim_scores = cosine_similarity([X_scaled[0]], X_scaled[1:])[0]

    pool = pool.copy()
    pool["Similarity_%"] = (sim_scores * 100).round(1)
    pool = pool.sort_values("Similarity_%", ascending=False).reset_index(drop=True)

    out_cols = ["Name", "Team", "Age", "Position", "Tactical_Role",
                "League", "Minutes", "Market Value", "Performance_Score", "Similarity_%"]
    out_cols = [c for c in out_cols if c in pool.columns]
    return ref, pool[out_cols].head(top_n)

# ── Radar comparison chart ─────────────────────────────────────────────────
def build_radar_fig(df_pool, rows_dict, stat_cols, colors):
    """
    rows_dict: {player_name: row_series}
    stat_cols: list of column names to use
    colors:    list of hex colors, one per player
    """
    available = [m for m in stat_cols if m in df_pool.columns]
    if not available:
        return None

    pool_vals = df_pool[available].apply(pd.to_numeric, errors="coerce").fillna(0)
    scaler    = MinMaxScaler()
    scaler.fit(pool_vals)

    short_labels = [
        m.replace(" (Per90)", "").replace("Pass Completion Rate", "Pass %")
         .replace("Expected Goals (xG)", "xG").replace("Expected Assists (xA)", "xA")
         .replace("Successful Dribbles", "Dribbles").replace("Shots On Target", "Shots OT")
         .replace("Aerial Duels Won", "Aerial") for m in available
    ]

    angles = np.linspace(0, 2 * np.pi, len(available), endpoint=False).tolist()
    angles += angles[:1]

    fig = go.Figure()
    for (name, row), color in zip(rows_dict.items(), colors):
        vals = [pd.to_numeric(row.get(m, 0), errors="coerce") or 0 for m in available]
        scaled = scaler.transform([vals])[0]
        r_vals = list(scaled) + [scaled[0]]
        # Convert hex color to rgba for Plotly fillcolor compatibility
        if color.startswith("#") and len(color) == 7:
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fill_color = f"rgba({r},{g},{b},0.13)"
        else:
            fill_color = color
        fig.add_trace(go.Scatterpolar(
            r=r_vals, theta=short_labels + [short_labels[0]],
            fill="toself",
            fillcolor=fill_color,
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            name=name
        ))

    layout = {
        **THEME,
        "height": 420,
        "showlegend": True,
        "polar": dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,1], showticklabels=False,
                            gridcolor="#1e2a38", linecolor="#1e2a38"),
            angularaxis=dict(tickfont=dict(color="#e8edf2", size=10.5),
                             gridcolor="#1e2a38", linecolor="#1e2a38"),
        ),
        "legend": dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5,
                       bgcolor="rgba(15,20,25,0.8)", bordercolor="#1e2a38", borderwidth=1)
    }
    fig.update_layout(**layout)
    return fig

# ── Performance vs Market Value scatter (from notebook) ───────────────────
def build_perf_vs_value_fig(df, color_col="Trad_Position"):
    """
    Quadrant scatter: Role Performance Score vs Market Value (€M)
    Reproduces the notebook logic in Plotly with the dark theme.
    """
    d = df.copy()
    d["Market Value"] = pd.to_numeric(d["Market Value"], errors="coerce")
    d["Performance_Score"] = pd.to_numeric(d["Performance_Score"], errors="coerce")
    d = d.dropna(subset=["Market Value", "Performance_Score"])
    d["MV_M"] = d["Market Value"] / 1e6

    median_perf  = d["Performance_Score"].median()
    median_value = d["MV_M"].median()

    pos_colors = {
        "Forward":    "#ff5252",
        "Midfielder": "#00b0ff",
        "Defender":   "#00e676",
        "Unknown":    "#5a6a7a",
    }

    fig = go.Figure()

    for pos, col in pos_colors.items():
        sub = d[d[color_col] == pos]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["Performance_Score"], y=sub["MV_M"],
            mode="markers",
            name=pos,
            marker=dict(color=col, size=7, opacity=0.72,
                        line=dict(color="#080c10", width=0.5)),
            customdata=np.stack([sub["Name"], sub["Team"],
                                 sub["Market Value"].apply(fmt_val),
                                 sub.get("Tactical_Role", pd.Series([""] * len(sub), index=sub.index))], axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Role: %{customdata[3]}<br>"
                "Perf Score: %{x:.1f}<br>"
                "Market Value: %{customdata[2]}<extra></extra>"
            )
        ))

    # Quadrant dividers
    fig.add_vline(x=median_perf,  line=dict(color="#5a6a7a", dash="dot", width=1))
    fig.add_hline(y=median_value, line=dict(color="#5a6a7a", dash="dot", width=1))

    # Quadrant labels
    x_max = d["Performance_Score"].quantile(0.98)
    y_max = d["MV_M"].quantile(0.97)

    quad_annotations = [
        dict(x=median_perf * 0.55, y=y_max * 0.90, text="OVERPRICED",          color="#ff5252"),
        dict(x=median_perf * 1.42, y=y_max * 0.90, text="ELITE",               color="#00e676"),
        dict(x=median_perf * 0.55, y=median_value * 0.35, text="DEVELOPING",   color="#ffd740"),
        dict(x=median_perf * 1.42, y=median_value * 0.35, text="UNDERRATED ⭐", color="#00b0ff"),
    ]
    for q in quad_annotations:
        fig.add_annotation(
            x=q["x"], y=q["y"], text=f"<b>{q['text']}</b>",
            showarrow=False, font=dict(size=11, color=q["color"]),
            xref="x", yref="y", opacity=0.85
        )

    # Label top 12 extremes
    extremeness = np.sqrt(
        ((d["Performance_Score"] - median_perf) /
         (d["Performance_Score"].max() - d["Performance_Score"].min() + 1e-9)) ** 2 +
        ((d["MV_M"] - median_value) /
         (d["MV_M"].max() - d["MV_M"].min() + 1e-9)) ** 2
    )
    top_idx = extremeness.nlargest(12).index
    for idx in top_idx:
        row = d.loc[idx]
        fig.add_annotation(
            x=row["Performance_Score"], y=row["MV_M"],
            text=row["Name"].split()[-1],
            showarrow=False, font=dict(size=8, color="#e8edf2"),
            xshift=8, yshift=5
        )

    fig.update_layout(
        **THEME, height=500,
        xaxis_title="Performance Score",
        yaxis_title="Market Value (€M)",
    )
    return fig, median_perf, median_value


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:1.5rem 0.5rem 1rem 0.5rem;border-bottom:1px solid #1e2a38;margin-bottom:1rem'>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;letter-spacing:0.08em;color:#00e676;line-height:1'>PITCH IQ</div>"
        "<div style='font-size:0.72rem;color:#5a6a7a;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Football Analytics</div>"
        "</div>",
        unsafe_allow_html=True
    )
    page = st.radio(
        "Navigation",
        ["🏠  Overview",
         "🔍  Player Explorer",
         "👤  Player Profile",
         "🕵️  Scouting Report",
         "💰  Market Values",
         "🔁  Player Similarity"],
        label_visibility="collapsed"
    )
    st.markdown(
        "<div style='margin-top:1.5rem;padding-top:1rem;border-top:1px solid #1e2a38'>"
        "<div style='font-size:0.65rem;color:#5a6a7a;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem'>GLOBAL FILTERS</div>"
        "</div>",
        unsafe_allow_html=True
    )
    league_opts = ["All"] + sorted(df_full["League_Label"].dropna().unique().tolist())
    sel_league  = st.selectbox("League", league_opts)

df_base      = df_master.copy()
df_full_base = df_full.copy()
if sel_league != "All":
    df_base      = df_base[df_base["League_Label"]           == sel_league]
    df_full_base = df_full_base[df_full_base["League_Label"] == sel_league]


# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
if page == "🏠  Overview":
    total_players = len(df_full) + len(df_gk)
    total_mv      = (df_full["Market Value"].sum() + df_gk["Market Value"].sum()) / 1e9

    st.markdown("<div style='padding:3rem 0 1rem 0;border-bottom:1px solid #1e2a38;margin-bottom:2rem'>", unsafe_allow_html=True)
    st.markdown("<div style='display:inline-block;background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.25);border-radius:100px;padding:4px 14px;font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#00e676;margin-bottom:1.2rem'>⚽ 2025/26 Season &nbsp;&middot;&nbsp; Premier League &amp; La Liga</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:5rem;letter-spacing:0.04em;line-height:0.92;color:#e8edf2;margin-bottom:1.2rem'>FOOTBALL.<br><span style='color:#00e676'>DECODED.</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:1rem;color:#5a6a7a;max-width:580px;line-height:1.7;margin-bottom:2rem'>Two leagues. 735 players. Every stat that matters. Performance scores, tactical profiles, and ML-powered market value intelligence — all in one place.</div>", unsafe_allow_html=True)

    sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([3, 1, 3, 1, 3, 1, 3])
    sc1.markdown(f"<div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;color:#00e676;line-height:1;letter-spacing:0.02em'>{total_players}</div><div style='font-size:0.68rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:4px'>Players Tracked</div>", unsafe_allow_html=True)
    sc2.markdown("<div style='height:60px;width:1px;background:#1e2a38;margin:auto'></div>", unsafe_allow_html=True)
    sc3.markdown(f"<div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;color:#ffd740;line-height:1;letter-spacing:0.02em'>€{total_mv:.1f}B</div><div style='font-size:0.68rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:4px'>Total Market Value</div>", unsafe_allow_html=True)
    sc4.markdown("<div style='height:60px;width:1px;background:#1e2a38;margin:auto'></div>", unsafe_allow_html=True)
    sc5.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;color:#00b0ff;line-height:1;letter-spacing:0.02em'>46</div><div style='font-size:0.68rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:4px'>Tactical Roles</div>", unsafe_allow_html=True)
    sc6.markdown("<div style='height:60px;width:1px;background:#1e2a38;margin:auto'></div>", unsafe_allow_html=True)
    sc7.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;color:#bc8cff;line-height:1;letter-spacing:0.02em'>39</div><div style='font-size:0.68rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:4px'>Clubs Covered</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-family:Bebas Neue,sans-serif;font-size:0.75rem;letter-spacing:0.18em;color:#5a6a7a;text-transform:uppercase;margin-bottom:1rem'>What's Inside</div>", unsafe_allow_html=True)
    features = [
        {"accent": "#00e676", "top": "2px solid #00e676", "emoji": "🔍", "title": "Player Explorer",
         "desc": "Search, filter, and sort all 735 players by position, tactical role, age, and league. Includes a full goalkeeper mode with GK-specific filters.",
         "pills": ["735 Players", "7 Positions", "46 Roles", "GK Mode"]},
        {"accent": "#00b0ff", "top": "2px solid #00b0ff", "emoji": "👤", "title": "Player Profile",
         "desc": "Deep dive into any player — radar chart vs position peers with custom stat selection, multi-player comparisons, role fit scores, and market value vs ML prediction.",
         "pills": ["Radar Chart", "Compare Players", "Role Scores", "Value Gap"]},
        {"accent": "#ffd740", "top": "2px solid #ffd740", "emoji": "🕵️", "title": "Scouting Report",
         "desc": "Six curated watchlists: Top Performers, On Fire, Rising Stars (U21), Undervalued Gems, Defensive Walls, and Best Value for Money.",
         "pills": ["Top Performers", "U21 Stars", "Hidden Gems", "On Fire"]},
        {"accent": "#ff5252", "top": "2px solid #ff5252", "emoji": "💰", "title": "Market Value Intelligence",
         "desc": "ML predictions for every player's true market value, plus a quadrant scatter mapping performance vs value — identify elite, underrated, overpriced, and developing players.",
         "pills": ["Quadrant Chart", "ML Predictions", "Undervalued", "Overpriced"]},
        {"accent": "#bc8cff", "top": "2px solid #bc8cff", "emoji": "🔁", "title": "Player Similarity",
         "desc": "Cosine-similarity engine built from 40+ per-90 and rate stats. Find the most statistically similar players to any player in the dataset, with radar chart comparison.",
         "pills": ["Cosine Similarity", "Radar Comparison", "Age & Value Filters", "Position Filter"]},
    ]
    col1, col2, col3 = st.columns(3)
    cols_cycle = [col1, col2, col3]
    for i, f in enumerate(features):
        col = cols_cycle[i % 3]
        ac  = f["accent"]
        pills = "".join([
            f"<span style='display:inline-block;border:1px solid {ac}55;color:{ac};background:{ac}11;"
            f"border-radius:100px;padding:2px 10px;font-size:0.68rem;font-weight:600;letter-spacing:0.08em;margin:2px'>{p}</span>"
            for p in f["pills"]
        ])
        col.markdown(
            f"<div style='background:#0f1419;border:1px solid #1e2a38;border-top:{f['top']};border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:1rem'>"
            f"<div style='font-size:1.5rem;margin-bottom:0.5rem'>{f['emoji']}</div>"
            f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.3rem;letter-spacing:0.06em;color:{ac};margin-bottom:0.5rem'>{f['title']}</div>"
            f"<div style='font-size:0.85rem;color:#7a8fa0;line-height:1.6;margin-bottom:1rem'>{f['desc']}</div>"
            f"<div>{pills}</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    ds1, ds2 = st.columns(2)
    ds1.markdown("<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1rem 1.2rem'><div style='font-size:0.62rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>Data Sources</div><div style='font-family:Bebas Neue,sans-serif;font-size:1rem;color:#e8edf2;letter-spacing:0.05em'>Transfermarkt &amp; Footystats</div></div>", unsafe_allow_html=True)
    ds2.markdown("<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1rem 1.2rem'><div style='font-size:0.62rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>Coverage</div><div style='font-family:Bebas Neue,sans-serif;font-size:1rem;color:#e8edf2;letter-spacing:0.05em'>Premier League &amp; La Liga · 2025/26</div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLAYER EXPLORER
# ══════════════════════════════════════════════════════════════════════════
elif page == "🔍  Player Explorer":
    section_header("Player Explorer", "Browse, filter and search the full player database")
    mode = st.radio("Player Type", ["⚽ Outfield Players", "🥅 Goalkeepers"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    if mode == "⚽ Outfield Players":
        df_pool = df_full_base.copy()
        f1, f2, f3, f4, f5, f6 = st.columns([2, 2, 2, 2, 1, 1])
        with f1: search   = st.text_input("Search", placeholder="Player name or team...")
        with f2:
            pos_opts = ["All Positions"] + sorted(df_pool["Position"].dropna().unique().tolist())
            sel_pos  = st.selectbox("Position", pos_opts, key="explorer_pos")

        # Reset role selection when position changes to avoid invalid selectbox value
        prev_pos = st.session_state.get("_prev_pos", "All Positions")
        if sel_pos != prev_pos:
            st.session_state["explorer_role"] = "All Roles"
            st.session_state["_prev_pos"] = sel_pos

        with f3:
            if sel_pos != "All Positions":
                pos_roles = df_pool[df_pool["Position"] == sel_pos]["Tactical_Role"].dropna().unique().tolist()
                role_opts = ["All Roles"] + sorted(pos_roles)
            else:
                role_opts = ["All Roles"] + sorted(df_pool["Tactical_Role"].dropna().unique().tolist())
            sel_role = st.selectbox("Tactical Role", role_opts, key="explorer_role")
        with f4:
            min_age, max_age = int(df_pool["Age"].min()), int(df_pool["Age"].max())
            age_range = st.slider("Age Range", min_age, max_age, (min_age, max_age))
        with f5: sort_by  = st.selectbox("Sort By", ["Performance Score", "Market Value", "Age", "Name"])
        with f6: sort_dir = st.selectbox("Order", ["Descending", "Ascending"])

        df_exp = df_pool.copy()
        if search:
            mask = (df_exp["Name"].str.contains(search, case=False, na=False) |
                    df_exp["Team"].str.contains(search, case=False, na=False))
            df_exp = df_exp[mask]
        if sel_pos  != "All Positions": df_exp = df_exp[df_exp["Position"]      == sel_pos]
        if sel_role != "All Roles":     df_exp = df_exp[df_exp["Tactical_Role"] == sel_role]
        df_exp = df_exp[df_exp["Age"].between(*age_range)]
        sort_col_map = {"Performance Score": "Performance_Score", "Market Value": "Market Value", "Age": "Age", "Name": "Name"}
        df_exp = df_exp.sort_values(sort_col_map[sort_by], ascending=(sort_dir == "Ascending"))

        st.markdown(f"<div style='font-size:0.8rem;color:#5a6a7a;margin-bottom:0.8rem'>{len(df_exp)} players found</div>", unsafe_allow_html=True)
        disp = df_exp[["Name", "Team", "League_Label", "Position", "Tactical_Role", "Age", "Market Value", "Performance_Score", "Overall_Rank"]].copy()
        disp["Market Value"]      = disp["Market Value"].apply(fmt_val)
        disp["Performance_Score"] = disp["Performance_Score"].round(1)
        disp.columns = ["Player", "Team", "League", "Position", "Role", "Age", "Market Value", "Score", "Rank"]
        st.dataframe(disp, use_container_width=True, hide_index=True, height=520)

        st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
        section_header("Filtered Summary")
        s1, s2, s3, s4 = st.columns(4)
        s1.markdown(card("Players",          f"{len(df_exp):,}"),                              unsafe_allow_html=True)
        s2.markdown(card("Avg Market Value", fmt_val(df_exp["Market Value"].apply(pd.to_numeric, errors='coerce').mean())), unsafe_allow_html=True)
        s3.markdown(card("Avg Age",          f"{df_exp['Age'].mean():.1f}"),                    unsafe_allow_html=True)
        s4.markdown(card("Avg Perf. Score",  f"{df_exp['Performance_Score'].apply(pd.to_numeric, errors='coerce').mean():.1f}"), unsafe_allow_html=True)

    else:
        df_gk_base = df_gk.copy()
        if sel_league != "All":
            df_gk_base = df_gk_base[df_gk_base["League_Label"] == sel_league]

        f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 1, 1])
        with f1: gk_search   = st.text_input("Search", placeholder="Goalkeeper name or team...", key="gk_search")
        with f2: sel_gk_role = st.selectbox("GK Role", ["All Roles", "Shot Stopper", "Sweeper Keeper"], key="gk_role")
        with f3:
            gk_min_age = int(df_gk_base["Age"].min()); gk_max_age = int(df_gk_base["Age"].max())
            gk_age_range = st.slider("Age Range", gk_min_age, gk_max_age, (gk_min_age, gk_max_age), key="gk_age")
        with f4: gk_sort = st.selectbox("Sort By", ["Shot Stopper Score", "Sweeper Keeper Score", "Market Value", "Age", "Name"], key="gk_sort")
        with f5: gk_dir  = st.selectbox("Order", ["Descending", "Ascending"], key="gk_dir")

        df_gk_exp = df_gk_base.copy()
        if gk_search:
            mask = (df_gk_exp["Name"].str.contains(gk_search, case=False, na=False) |
                    df_gk_exp["Team"].str.contains(gk_search, case=False, na=False))
            df_gk_exp = df_gk_exp[mask]
        if sel_gk_role != "All Roles":
            df_gk_exp = df_gk_exp[df_gk_exp["GK_Role"] == sel_gk_role]
        df_gk_exp = df_gk_exp[df_gk_exp["Age"].between(*gk_age_range)]

        gk_sort_map = {
            "Shot Stopper Score":   "Shot Stopper_Score",
            "Sweeper Keeper Score": "Sweeper Keeper_Score",
            "Market Value": "Market Value", "Age": "Age", "Name": "Name"
        }
        sort_col = gk_sort_map[gk_sort]
        if sort_col in df_gk_exp.columns:
            df_gk_exp = df_gk_exp.sort_values(sort_col, ascending=(gk_dir == "Ascending"))

        st.markdown(f"<div style='font-size:0.8rem;color:#5a6a7a;margin-bottom:0.8rem'>{len(df_gk_exp)} goalkeepers found</div>", unsafe_allow_html=True)

        gk_disp = df_gk_exp.copy()
        gk_disp["Market Value"] = gk_disp["Market Value"].apply(fmt_val)
        if "Save Percentage" in gk_disp.columns:
            gk_disp["Save Percentage"] = gk_disp["Save Percentage"].apply(fmt_pct)
        for sc in ["Shot Stopper_Score", "Sweeper Keeper_Score"]:
            if sc in gk_disp.columns:
                gk_disp[sc] = gk_disp[sc].round(1)

        display_cols = {
            "Name": "Player", "Team": "Team", "League_Label": "League", "Age": "Age",
            "Market Value": "Market Value", "GK_Role": "Role",
            "Shot Stopper_Score": "Shot Stopper", "Sweeper Keeper_Score": "Sweeper Keeper",
            "Save Percentage": "Save %", "Clean Sheets": "Clean Sheets", "Minutes": "Minutes",
        }
        available = {k: v for k, v in display_cols.items() if k in gk_disp.columns}
        gk_final  = gk_disp[list(available.keys())].rename(columns=available)
        st.dataframe(gk_final, use_container_width=True, hide_index=True, height=520)

        section_header("Filtered Summary")
        s1, s2, s3, s4 = st.columns(4)
        ss = (df_gk_exp["GK_Role"] == "Shot Stopper").sum()
        s1.markdown(card("Goalkeepers",      f"{len(df_gk_exp):,}"),                            unsafe_allow_html=True)
        s2.markdown(card("Avg Market Value", fmt_val(df_gk_exp["Market Value"].mean())),         unsafe_allow_html=True)
        s3.markdown(card("Avg Age",          f"{df_gk_exp['Age'].mean():.1f}"),                  unsafe_allow_html=True)
        s4.markdown(card("Shot Stoppers",    f"{ss}", f"{len(df_gk_exp)-ss} Sweeper Keepers"),   unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — PLAYER PROFILE  (with enhanced radar + comparison)
# ══════════════════════════════════════════════════════════════════════════
elif page == "👤  Player Profile":
    section_header("Player Profile", "Deep dive into any player's stats, radar, and comparisons")

    all_names = sorted(df_full["Name"].dropna().unique().tolist()) + sorted(df_gk["Name"].dropna().unique().tolist())
    sel_name  = st.selectbox("Select Player", all_names)

    row = df_full[df_full["Name"] == sel_name]
    is_gk = False
    if row.empty:
        row   = df_gk[df_gk["Name"] == sel_name]
        is_gk = True
    if row.empty:
        st.warning("Player not found.")
        st.stop()
    row = row.iloc[0]

    league_label     = {"premier-league": "Premier League", "la-liga": "La Liga"}.get(row.get("League", ""), row.get("League", ""))
    position_display = "Goalkeeper" if is_gk else row.get("Position", "")
    role_display     = row.get("GK_Role", "") if is_gk else row.get("Tactical_Role", "")

    st.markdown(
        f"<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:12px;padding:1.8rem 2rem;"
        f"margin-bottom:1.5rem;display:flex;align-items:center;gap:2rem'>"
        f"<div style='width:72px;height:72px;background:#161d26;border-radius:50%;display:flex;"
        f"align-items:center;justify-content:center;font-size:2rem;flex-shrink:0'>{'🥅' if is_gk else '⚽'}</div>"
        f"<div style='flex:1'>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:2.4rem;letter-spacing:0.04em;color:#e8edf2;line-height:1'>{row['Name']}</div>"
        f"<div style='font-size:0.9rem;color:#5a6a7a;margin-top:4px'>{row.get('Team','')} &nbsp;·&nbsp; {league_label} &nbsp;·&nbsp; Age {int(row['Age']) if pd.notna(row['Age']) else 'N/A'}</div>"
        f"</div>"
        f"<div style='text-align:right'>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.1rem;color:#00e676;letter-spacing:0.08em'>{position_display}</div>"
        f"<div style='font-size:0.85rem;color:#5a6a7a;margin-top:2px'>{role_display}</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#ffd740;margin-top:4px'>{fmt_val(row.get('Market Value', np.nan))}</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

    if not is_gk:
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.markdown(card("Performance Score", f"{row.get('Performance_Score', 0):.1f}", "Out of 100", color="#00e676"), unsafe_allow_html=True)
        m2.markdown(card("Overall Rank", f"#{int(row.get('Overall_Rank', 0))}" if pd.notna(row.get("Overall_Rank")) else "N/A", "Across all positions"), unsafe_allow_html=True)
        m3.markdown(card("Goals (P90)",   f"{row.get('Goals Scored (Per90)', 0):.2f}"), unsafe_allow_html=True)
        m4.markdown(card("Assists (P90)", f"{row.get('Assists (Per90)', 0):.2f}"),       unsafe_allow_html=True)
        pcr = row.get("Pass Completion Rate", 0)
        m5.markdown(card("Pass %", fmt_pct(pcr)), unsafe_allow_html=True)
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(card("Save %",       fmt_pct(row.get("Save Percentage", 0))),  unsafe_allow_html=True)
        m2.markdown(card("Saves (P90)",  f"{row.get('Saves (Per90)', 0):.2f}"),     unsafe_allow_html=True)
        m3.markdown(card("Clean Sheets", f"{int(row.get('Clean Sheets', 0))}" if pd.notna(row.get("Clean Sheets")) else "N/A"), unsafe_allow_html=True)
        m4.markdown(card("GK Role",      row.get("GK_Role", ""), color="#00b0ff"),  unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── ENHANCED RADAR SECTION ─────────────────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        section_header("Performance Radar", "Customise stats · Compare with other players")

        if not is_gk:
            available_radar = [m for m in RADAR_METRICS if m in df_full.columns]
            short_labels_map = {
                m: m.replace(" (Per90)", "").replace("Pass Completion Rate", "Pass %")
                   .replace("Expected Goals (xG)", "xG").replace("Expected Assists (xA)", "xA")
                   .replace("Successful Dribbles", "Dribbles").replace("Shots On Target", "Shots OT")
                   .replace("Aerial Duels Won", "Aerial")
                for m in available_radar
            }

            # ── Stat selection ─────────────────────────────────────────────
            selected_stats = st.multiselect(
                "Choose Stats (4–10)",
                options=available_radar,
                default=available_radar[:8],
                format_func=lambda x: short_labels_map[x],
                key="radar_stats"
            )
            if len(selected_stats) < 3:
                st.warning("Select at least 3 stats to display the radar.")
            else:
                # ── Comparison player selection ────────────────────────────
                compare_opts = ["None"] + sorted(
                    df_full[df_full["Name"] != sel_name]["Name"].dropna().unique().tolist()
                )
                compare_name = st.selectbox("Compare with another player (optional)", compare_opts, key="compare_player")

                pos_df = df_full[df_full["Position"] == row.get("Position", "")] if not is_gk else df_gk

                rows_dict = {sel_name: row}
                colors    = ["#00e676"]

                if compare_name != "None":
                    cmp_row = df_full[df_full["Name"] == compare_name]
                    if not cmp_row.empty:
                        rows_dict[compare_name] = cmp_row.iloc[0]
                        colors.append("#bc8cff")

                fig_r = build_radar_fig(pos_df, rows_dict, selected_stats, colors)
                if fig_r:
                    st.plotly_chart(fig_r, use_container_width=True)

                if compare_name != "None" and compare_name in rows_dict:
                    cmp = rows_dict[compare_name]
                    cmp_pos  = cmp.get("Position", "—")
                    cmp_role = cmp.get("Tactical_Role", "—")
                    cmp_team = cmp.get("Team", "—")
                    cmp_mv   = fmt_val(cmp.get("Market Value", np.nan))
                    cmp_sc   = f"{cmp.get('Performance_Score', 0):.1f}"
                    st.markdown(
                        f"<div style='background:#0f1419;border:1px solid #bc8cff44;border-radius:10px;padding:0.9rem 1.2rem;margin-top:0.4rem'>"
                        f"<div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px'>Comparing With</div>"
                        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.2rem;color:#bc8cff'>{compare_name}</div>"
                        f"<div style='font-size:0.78rem;color:#5a6a7a;margin-top:3px'>{cmp_team} &nbsp;·&nbsp; {cmp_pos} &nbsp;·&nbsp; {cmp_role}</div>"
                        f"<div style='display:flex;gap:1.5rem;margin-top:8px'>"
                        f"<div><div style='font-size:0.62rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Score</div>"
                        f"<div style='font-family:Bebas Neue,sans-serif;color:#bc8cff'>{cmp_sc}</div></div>"
                        f"<div><div style='font-size:0.62rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Market Value</div>"
                        f"<div style='font-family:Bebas Neue,sans-serif;color:#e8edf2'>{cmp_mv}</div></div>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )
        else:
            # GK radar
            gk_labels   = ["Saves (P90)", "Interceptions", "Clearances", "Pass Comp %", "Clean Sheets"]
            gk_cols_map = ["Saves (Per90)", "Interceptions (Per90)", "Clearances (Per90)", "Pass Completion Rate", "Clean Sheets"]
            gk_vals = []
            for col_name in gk_cols_map:
                if col_name in df_gk.columns:
                    col_data = pd.to_numeric(df_gk[col_name], errors="coerce")
                    cmax = col_data.quantile(0.95); cmin = col_data.min()
                    raw  = pd.to_numeric(row.get(col_name, 0), errors="coerce") or 0
                    gk_vals.append(max(0, min(1, (raw - cmin) / (cmax - cmin) if cmax > cmin else 0)))
                else:
                    gk_vals.append(0)
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=gk_vals + gk_vals[:1], theta=gk_labels + [gk_labels[0]],
                fill="toself", fillcolor="rgba(0,176,255,0.15)",
                line=dict(color="#00b0ff", width=2), marker=dict(size=6, color="#00b0ff")
            ))
            fig_r.update_layout(**THEME, height=380, title_text="",
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0,1], showticklabels=False, gridcolor="#1e2a38", linecolor="#1e2a38"),
                    angularaxis=dict(tickfont=dict(color="#e8edf2", size=11), gridcolor="#1e2a38", linecolor="#1e2a38")),
                showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)

    with col_r:
        if not is_gk:
            section_header("Tactical Role Fit", "How well this player profiles across each tactical role (0–100)")
            score_cols = [c for c in df_full.columns if c.endswith("_Score") and c != "Performance_Score" and pd.notna(row.get(c))]
            if score_cols:
                scores = {c.replace("_Score", "").replace("_", " "): round(row[c], 1) for c in score_cols if pd.notna(row.get(c))}
                scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
                role_df = pd.DataFrame({"Role": list(scores.keys()), "Score": list(scores.values())})
                fig_s = px.bar(role_df, x="Score", y="Role", orientation="h",
                               color="Score", color_continuous_scale=["#1e2a38", "#ffd740"], range_x=[0, 100])
                fig_s.update_layout(**THEME, height=360, coloraxis_showscale=False, title_text="")
                fig_s.update_traces(marker_line_width=0)
                fig_s.update_yaxes(title="", categoryorder="total ascending")
                st.plotly_chart(fig_s, use_container_width=True)
            else:
                st.markdown("<div style='color:#5a6a7a;font-size:0.85rem;padding:1rem 0'>No role scores available for this player.</div>", unsafe_allow_html=True)
        else:
            section_header("GK Role Scores", "Shot Stopper vs Sweeper Keeper fit score (0–100)")
            gk_scores = {c.replace("_Score", "").replace("_", " "): round(row[c], 1)
                         for c in ["Shot Stopper_Score", "Sweeper Keeper_Score"]
                         if c in row.index and pd.notna(row[c])}
            if gk_scores:
                gk_df = pd.DataFrame({"Role": list(gk_scores.keys()), "Score": list(gk_scores.values())})
                fig_s = px.bar(gk_df, x="Score", y="Role", orientation="h",
                               color="Score", color_continuous_scale=["#1e2a38", "#00b0ff"], range_x=[0, 100])
                fig_s.update_layout(**THEME, height=180, coloraxis_showscale=False, title_text="")
                fig_s.update_traces(marker_line_width=0)
                st.plotly_chart(fig_s, use_container_width=True)
                primary_role  = max(gk_scores, key=gk_scores.get)
                primary_score = gk_scores[primary_role]
                role_desc = {
                    "Shot Stopper":   "Excels at shot-stopping, reflexes, and commanding the penalty area.",
                    "Sweeper Keeper": "Comfortable on the ball, sweeps behind the defensive line, and plays as an extra outfield player.",
                }
                st.markdown(
                    f"<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1rem 1.2rem;margin-top:0.5rem'>"
                    f"<div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px'>Primary Role</div>"
                    f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.2rem;color:#00b0ff'>{primary_role} <span style='font-size:0.9rem;color:#5a6a7a'>· {primary_score:.0f}/100</span></div>"
                    f"<div style='font-size:0.78rem;color:#7a8fa0;margin-top:6px;line-height:1.5'>{role_desc.get(primary_role,'')}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        if not is_gk and pd.notna(row.get("Predicted_Market_Value")):
            section_header("Market Value", "Actual vs ML-predicted value")
            actual    = row["Market Value"]
            predicted = row["Predicted_Market_Value"]
            gap       = predicted - actual
            color     = "#00e676" if gap > 0 else "#ff5252"
            label     = "Undervalued" if gap > 0 else "Overvalued"
            bar_w     = min(100, abs(gap) / max(actual, predicted) * 100 + 50)
            st.markdown(
                f"<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1.2rem'>"
                f"<div style='display:flex;justify-content:space-between;margin-bottom:0.8rem'>"
                f"<div><div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Actual</div>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem'>{fmt_val(actual)}</div></div>"
                f"<div style='text-align:right'><div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Predicted</div>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem'>{fmt_val(predicted)}</div></div>"
                f"</div>"
                f"<div style='height:4px;background:#1e2a38;border-radius:2px;margin-bottom:0.8rem'>"
                f"<div style='height:100%;width:{bar_w:.0f}%;background:{color};border-radius:2px'></div></div>"
                f"<div style='font-size:0.85rem;color:{color};font-weight:600'>{label} by {fmt_val(abs(gap))}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # ── Full Stats Breakdown ───────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Full Stats Breakdown")

    TH1 = (
        "<table style='width:100%;border-collapse:collapse'>"
        "<tr style='border-bottom:1px solid #1e2a38'>"
        "<th style='padding:6px 12px;text-align:left;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>STAT</th>"
        "<th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>VALUE</th>"
        "</tr>"
    )
    TH2 = (
        "<table style='width:100%;border-collapse:collapse'>"
        "<tr style='border-bottom:1px solid #1e2a38'>"
        "<th style='padding:6px 12px;text-align:left;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>STAT</th>"
        "<th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>TOTAL</th>"
        "<th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>PER 90</th>"
        "</tr>"
    )

    def _fmt(val, is_pct=False):
        if pd.isna(val): return "—"
        if is_pct:       return fmt_pct(val)
        if isinstance(val, (float, np.floating)): return f"{val:.2f}"
        return str(int(val))

    def stat_row(label, val, is_pct=False):
        return (f"<tr><td style='padding:6px 12px;color:#5a6a7a;font-size:0.83rem'>{label}</td>"
                f"<td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right'>{_fmt(val, is_pct)}</td></tr>")

    def stat_row2(label, total, per90=None, is_pct=False):
        p = "—"
        if per90 is not None:
            try: p = "—" if pd.isna(per90) else _fmt(per90)
            except: p = "—"
        return (f"<tr><td style='padding:6px 12px;color:#5a6a7a;font-size:0.83rem'>{label}</td>"
                f"<td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right'>{_fmt(total, is_pct)}</td>"
                f"<td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right;color:#5a6a7a'>{p}</td></tr>")

    if not is_gk:
        tab_g, tab_att, tab_def, tab_pass, tab_drib = st.tabs(
            ["📋 General", "⚽ Attacking", "🛡 Defending", "📤 Passing", "🏃 Dribbling"])

        with tab_g:
            st.markdown(TH1 + stat_row("Matches Played", row.get("Matches Played"))
                + stat_row("Minutes Played", row.get("Minutes")) + stat_row("Matches Started", row.get("Matches Started"))
                + stat_row("Yellow Cards", row.get("Yellow Cards")) + stat_row("Red Cards", row.get("Red Cards"))
                + stat_row("Fouls Committed", row.get("Fouls Committed")) + stat_row("Fouled Against", row.get("Fouled Against"))
                + "</table>", unsafe_allow_html=True)
        with tab_att:
            st.markdown(TH2 + stat_row2("Goals Scored", row.get("Goals Scored"), row.get("Goals Scored (Per90)"))
                + stat_row2("Shots Taken", row.get("Shots Taken"), row.get("Shots Taken (Per90)"))
                + stat_row2("Shots On Target", row.get("Shots On Target"), row.get("Shots On Target (Per90)"))
                + stat_row2("Shot Accuracy", row.get("Shot Accuracy"), is_pct=True)
                + stat_row2("Goal Involvement", row.get("Goal Involvement"), row.get("Goal Involvement (Per90)"))
                + "</table>", unsafe_allow_html=True)
        with tab_def:
            st.markdown(TH2 + stat_row2("Tackles", row.get("Tackles"), row.get("Tackles (Per90)"))
                + stat_row2("Interceptions", row.get("Interceptions"), row.get("Interceptions (Per90)"))
                + stat_row2("Clearances", row.get("Clearances"), row.get("Clearances (Per90)"))
                + stat_row2("Shots Blocked", row.get("Shots Blocked"), row.get("Shots Blocked (Per90)"))
                + stat_row2("Aerial Duels Won", row.get("Aerial Duels Won"), row.get("Aerial Duels Won (Per90)"))
                + stat_row2("Ground Duels Won", row.get("Ground Duels Won"), row.get("Ground Duels Won (Per90)"))
                + stat_row2("Dribbled Past", row.get("Dribbled Past"), row.get("Dribbled Past (Per90)"))
                + "</table>", unsafe_allow_html=True)
        with tab_pass:
            st.markdown(TH2 + stat_row2("Assists", row.get("Assists"), row.get("Assists (Per90)"))
                + stat_row2("Key Passes", row.get("Key Passes"), row.get("Key Passes (Per90)"))
                + stat_row2("Passes", row.get("Passes"), row.get("Passes (Per90)"))
                + stat_row2("Successful Passes", row.get("Successful Passes"), row.get("Successful Passes (Per90)"))
                + stat_row2("Pass Completion %", row.get("Pass Completion Rate"), is_pct=True)
                + stat_row2("Crosses", row.get("Crosses"), row.get("Crosses (Per90)"))
                + "</table>", unsafe_allow_html=True)
        with tab_drib:
            st.markdown(TH2 + stat_row2("Dribbles", row.get("Dribbles"), row.get("Dribbles (Per90)"))
                + stat_row2("Successful Dribbles", row.get("Successful Dribbles"), row.get("Successful Dribbles (Per90)"))
                + stat_row2("Dribble Success %", row.get("Dribble Success Rate"), is_pct=True)
                + stat_row2("Dispossessed", row.get("Dispossesed"), row.get("Dispossesed (Per90)"))
                + stat_row2("Offsides", row.get("Offsides"), row.get("Offsides (Per90)"))
                + "</table>", unsafe_allow_html=True)
    else:
        tab_gk_g, tab_gk_stop, tab_gk_dist = st.tabs(["📋 General", "🧤 Shot Stopping", "🏃🏻 Distribution"])
        with tab_gk_g:
            st.markdown(TH1 + stat_row("Matches Played", row.get("Matches Played"))
                + stat_row("Minutes Played", row.get("Minutes")) + stat_row("Matches Started", row.get("Matches Started"))
                + stat_row("Clean Sheets", row.get("Clean Sheets")) + stat_row("Yellow Cards", row.get("Yellow Cards"))
                + stat_row("Red Cards", row.get("Red Cards")) + stat_row("Fouls Committed", row.get("Fouls Committed"))
                + "</table>", unsafe_allow_html=True)
        with tab_gk_stop:
            st.markdown(TH2 + stat_row2("Saves", row.get("Saves"), row.get("Saves (Per90)"))
                + stat_row2("Shots Faced", row.get("Shots Faced"), row.get("Shots Faced (Per90)"))
                + stat_row2("Save Percentage", row.get("Save Percentage"), is_pct=True)
                + stat_row2("Goals Conceded", row.get("Goals Conceded"), row.get("Goals Conceded (Per90)"))
                + stat_row2("Aerial Duels Won", row.get("Aerial Duels Won"), row.get("Aerial Duels Won (Per90)"))
                + stat_row2("Punches", row.get("Punches"), row.get("Punches (Per90)"))
                + "</table>", unsafe_allow_html=True)
        with tab_gk_dist:
            st.markdown(TH2 + stat_row2("Passes", row.get("Passes"), row.get("Passes (Per90)"))
                + stat_row2("Successful Passes", row.get("Successful Passes"), row.get("Successful Passes (Per90)"))
                + stat_row2("Pass Completion %", row.get("Pass Completion Rate"), is_pct=True)
                + stat_row2("Interceptions", row.get("Interceptions"), row.get("Interceptions (Per90)"))
                + stat_row2("Clearances", row.get("Clearances"), row.get("Clearances (Per90)"))
                + "</table>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — SCOUTING REPORT
# ══════════════════════════════════════════════════════════════════════════
elif page == "🕵️  Scouting Report":
    st.markdown(
        "<div style='padding:2rem 0 1.2rem 0;border-bottom:1px solid #1e2a38;margin-bottom:2rem'>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:3rem;letter-spacing:0.06em;line-height:1;color:#e8edf2'>"
        "SCOUTING <span style='color:#00e676'>REPORT</span></div>"
        "<div style='font-size:0.9rem;color:#5a6a7a;margin-top:0.6rem'>"
        "Data-driven intelligence on the players shaping the 2025/26 season · 1,500+ min filter applied</div>"
        "</div>", unsafe_allow_html=True
    )

    df_scout = df_base.copy()
    for col in ["Age", "Minutes", "Market Value", "Goals Scored", "Assists",
                "Goals Scored (Per90)", "Assists (Per90)"]:
        df_scout[col] = pd.to_numeric(df_scout[col], errors="coerce")

    df_scout["G_A_per90"] = df_scout["Goals Scored (Per90)"].fillna(0) + df_scout["Assists (Per90)"].fillna(0)

    top_performers = df_scout.nlargest(6, "Performance_Score")
    on_fire        = df_scout.nlargest(6, "G_A_per90")
    rising         = df_scout[df_scout["Age"] <= 21].nlargest(6, "Performance_Score")
    undervalued    = df_scout[(df_scout["Value_Gap"] > 0) & (df_scout["Age"] <= 26)].nlargest(6, "Value_Gap")
    defenders      = df_scout[df_scout["Position"].isin(["Centre-Back", "Full-Back", "Defensive Midfield"])].nlargest(6, "Performance_Score")

    all_val = pd.concat(list(pos_dfs.values()), ignore_index=True)
    if sel_league != "All":
        lkey = "premier-league" if sel_league == "Premier League" else "la-liga"
        all_val = all_val[all_val["League"] == lkey]
    all_val["Age"]          = pd.to_numeric(all_val["Age"],          errors="coerce")
    all_val["Market Value"] = pd.to_numeric(all_val["Market Value"], errors="coerce")
    best_value = all_val[all_val["Age"] <= 25].nlargest(6, "Value_Score") if "Value_Score" in all_val.columns else pd.DataFrame()

    df_gk_scout = df_gk.copy()
    if sel_league != "All":
        df_gk_scout = df_gk_scout[df_gk_scout["League_Label"] == sel_league]
    for col in ["Age", "Minutes", "Market Value", "Save Percentage", "Clean Sheets"]:
        if col in df_gk_scout.columns:
            df_gk_scout[col] = pd.to_numeric(df_gk_scout[col], errors="coerce")
    best_stoppers = df_gk_scout.dropna(subset=["Shot Stopper_Score"]).nlargest(3, "Shot Stopper_Score") if "Shot Stopper_Score" in df_gk_scout.columns else pd.DataFrame()
    best_sweepers = df_gk_scout.dropna(subset=["Sweeper Keeper_Score"]).nlargest(3, "Sweeper Keeper_Score") if "Sweeper Keeper_Score" in df_gk_scout.columns else pd.DataFrame()

    def render_section(title, emoji, subtitle, df_rows, badge_label, badge_color, stat_fn):
        st.markdown(
            f"<div style='display:flex;align-items:baseline;gap:0.8rem;margin:2.2rem 0 0.3rem 0'>"
            f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.7rem;letter-spacing:0.05em;color:#e8edf2'>{emoji} {title}</div>"
            f"<div style='font-size:0.78rem;color:#5a6a7a'>{subtitle}</div></div>"
            f"<div style='height:2px;background:linear-gradient({badge_color},{badge_color}33,transparent);border-radius:1px;margin-bottom:1.2rem'></div>",
            unsafe_allow_html=True
        )
        cols = st.columns(3)
        for i, (_, r) in enumerate(df_rows.iterrows()):
            with cols[i % 3]:
                st.markdown(scout_player_card(r, badge_label, badge_color, stat_fn(r)), unsafe_allow_html=True)

    render_section("TOP PERFORMERS", "🏆", "Highest performance scores — the elite of two leagues",
        top_performers, "ELITE", "#ffd740",
        lambda r: f"Perf. Score <strong style='color:#ffd740'>{r.get('Performance_Score',0):.1f}</strong> &nbsp;·&nbsp; {int(r.get('Minutes',0))} mins &nbsp;·&nbsp; Rank #{int(r.get('Overall_Rank',0)) if pd.notna(r.get('Overall_Rank')) else '—'}")

    render_section("ON FIRE", "🔥", "Best goals + assists per 90 minutes right now",
        on_fire, "HOT FORM", "#ff5252",
        lambda r: f"G+A/90 <strong style='color:#ff5252'>{r.get('G_A_per90',0):.2f}</strong> &nbsp;·&nbsp; {int(r.get('Goals Scored',0) or 0)}G {int(r.get('Assists',0) or 0)}A &nbsp;·&nbsp; {int(r.get('Minutes',0))} mins")

    if not rising.empty:
        render_section("RISING STARS", "⭐", "U21 talent already making a serious impact",
            rising, "U21", "#00b0ff",
            lambda r: f"Age <strong style='color:#00b0ff'>{int(r.get('Age',0))}</strong> &nbsp;·&nbsp; Score {r.get('Performance_Score',0):.1f} &nbsp;·&nbsp; {int(r.get('Minutes',0))} mins")

    if not undervalued.empty:
        render_section("UNDERVALUED GEMS", "💎", "Young players worth far more than their price tag",
            undervalued, "UNDERVALUED", "#00e676",
            lambda r: f"Actual <strong style='color:#e8edf2'>{fmt_val(r.get('Market Value',np.nan))}</strong> &nbsp;·&nbsp; Predicted <strong style='color:#00e676'>{fmt_val(r.get('Predicted_Market_Value',np.nan))}</strong> &nbsp;·&nbsp; Gap +{fmt_val(r.get('Value_Gap',0))}")

    render_section("DEFENSIVE WALLS", "🛡", "Best defenders and defensive midfielders in both leagues",
        defenders, "DEFENDER", "#bc8cff",
        lambda r: f"Tackles/90 <strong style='color:#bc8cff'>{r.get('Tackles (Per90)',0):.2f}</strong> &nbsp;·&nbsp; Interceptions/90 {r.get('Interceptions (Per90)',0):.2f} &nbsp;·&nbsp; Score {r.get('Performance_Score',0):.1f}")

    if not best_value.empty:
        render_section("BEST VALUE FOR MONEY", "💰", "U25 players delivering elite output at a bargain price",
            best_value, "VALUE PICK", "#ff6d00",
            lambda r: f"Value Score <strong style='color:#ff6d00'>{r.get('Value_Score',0):.1f}</strong> &nbsp;·&nbsp; {fmt_val(r.get('Market Value',np.nan))} &nbsp;·&nbsp; Age {int(r.get('Age',0)) if pd.notna(r.get('Age')) else '—'}")

    st.markdown(
        "<div style='display:flex;align-items:baseline;gap:0.8rem;margin:2.2rem 0 0.3rem 0'>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:1.7rem;letter-spacing:0.05em;color:#e8edf2'>🥅 ELITE GOALKEEPERS</div>"
        "<div style='font-size:0.78rem;color:#5a6a7a'>Top shot stoppers and sweeper keepers across both leagues</div></div>"
        "<div style='height:2px;background:linear-gradient(#00b0ff,#00b0ff33,transparent);border-radius:1px;margin-bottom:1.2rem'></div>",
        unsafe_allow_html=True
    )
    gk_col1, gk_col2 = st.columns(2, gap="medium")
    with gk_col1:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#5a6a7a;margin-bottom:0.6rem'>🧤 Best Shot Stoppers</div>", unsafe_allow_html=True)
        if not best_stoppers.empty:
            for _, gk_row in best_stoppers.iterrows():
                sp_str    = fmt_pct(gk_row.get("Save Percentage", 0))
                cs        = int(gk_row.get("Clean Sheets", 0)) if pd.notna(gk_row.get("Clean Sheets")) else "—"
                score_val = gk_row.get("Shot Stopper_Score", 0)
                st.markdown(scout_player_card(gk_row, "SHOT STOPPER", "#00b0ff",
                    f"Save % <strong style='color:#00b0ff'>{sp_str}</strong> &nbsp;·&nbsp; Clean Sheets {cs} &nbsp;·&nbsp; Score {score_val:.1f}"), unsafe_allow_html=True)
    with gk_col2:
        st.markdown("<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#5a6a7a;margin-bottom:0.6rem'>🦶 Best Sweeper Keepers</div>", unsafe_allow_html=True)
        if not best_sweepers.empty:
            for _, gk_row in best_sweepers.iterrows():
                sp_str    = fmt_pct(gk_row.get("Save Percentage", 0))
                cs        = int(gk_row.get("Clean Sheets", 0)) if pd.notna(gk_row.get("Clean Sheets")) else "—"
                score_val = gk_row.get("Sweeper Keeper_Score", 0)
                st.markdown(scout_player_card(gk_row, "SWEEPER KEEPER", "#00e676",
                    f"Save % <strong style='color:#00e676'>{sp_str}</strong> &nbsp;·&nbsp; Clean Sheets {cs} &nbsp;·&nbsp; Score {score_val:.1f}"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 5 — MARKET VALUES  (with quadrant scatter from notebooks)
# ══════════════════════════════════════════════════════════════════════════
elif page == "💰  Market Values":
    section_header("Market Value Analysis", "Actual vs predicted — who's over or undervalued?")
    df_mv = df_full_base.dropna(subset=["Market Value", "Predicted_Market_Value", "Value_Gap"]).copy()

    most_under = df_mv.nlargest(1, "Value_Gap").iloc[0]
    most_over  = df_mv.nsmallest(1, "Value_Gap").iloc[0]
    avg_gap    = df_mv["Value_Gap"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(card("Players With Predictions", f"{len(df_mv):,}"), unsafe_allow_html=True)
    c2.markdown(card("Most Undervalued", most_under["Name"].split()[-1], f"+{fmt_val(most_under['Value_Gap'])}", color="#00e676"), unsafe_allow_html=True)
    c3.markdown(card("Most Overvalued",  most_over["Name"].split()[-1],  fmt_gap(most_over["Value_Gap"]),        color="#ff5252"), unsafe_allow_html=True)
    c4.markdown(card("Avg Prediction Gap", fmt_val(abs(avg_gap)), "Undervalued" if avg_gap > 0 else "Overvalued", color="#ffd740"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── TAB 1: Performance vs Market Value Quadrant (from notebooks) ───────
    tab_quad, tab_pred, tab_tables = st.tabs([
        "📊 Performance vs Value Quadrant",
        "🔵 Actual vs Predicted",
        "📋 Under / Overvalued Tables"
    ])

    with tab_quad:
        section_header("Performance vs Market Value", "Four quadrants: Elite · Underrated · Overpriced · Developing")

        # Position & filters
        q1, q2, q3 = st.columns([2, 2, 2])
        with q1:
            pos_filter = st.multiselect(
                "Filter by Position",
                options=sorted(df_full_base["Position"].dropna().unique().tolist()),
                default=[],
                key="quad_pos"
            )
        with q2:
            min_score, max_score = 0, 100
            score_rng = st.slider("Performance Score Range", min_score, max_score, (min_score, max_score), key="quad_score")
        with q3:
            mv_cap = st.selectbox("Max Market Value", ["All", "€10M", "€25M", "€50M", "€100M"], key="quad_mv")

        df_quad = df_full_base.copy()
        df_quad["Performance_Score"] = pd.to_numeric(df_quad["Performance_Score"], errors="coerce")
        df_quad["Market Value"]      = pd.to_numeric(df_quad["Market Value"],      errors="coerce")
        df_quad = df_quad.dropna(subset=["Performance_Score", "Market Value"])
        df_quad = df_quad[df_quad["Performance_Score"].between(*score_rng)]

        if pos_filter:
            df_quad = df_quad[df_quad["Position"].isin(pos_filter)]
        mv_cap_map = {"€10M": 10e6, "€25M": 25e6, "€50M": 50e6, "€100M": 100e6}
        if mv_cap in mv_cap_map:
            df_quad = df_quad[df_quad["Market Value"] <= mv_cap_map[mv_cap]]

        if df_quad.empty:
            st.info("No players match the current filters.")
        else:
            fig_quad, med_perf, med_val = build_perf_vs_value_fig(df_quad)
            st.plotly_chart(fig_quad, use_container_width=True)

            # Quadrant summary cards
            df_quad["MV_M"] = df_quad["Market Value"] / 1e6
            elite      = df_quad[(df_quad["Performance_Score"] >= med_perf) & (df_quad["MV_M"] >= med_val)]
            underrated = df_quad[(df_quad["Performance_Score"] >= med_perf) & (df_quad["MV_M"] <  med_val)]
            overpriced = df_quad[(df_quad["Performance_Score"] <  med_perf) & (df_quad["MV_M"] >= med_val)]
            developing = df_quad[(df_quad["Performance_Score"] <  med_perf) & (df_quad["MV_M"] <  med_val)]

            qa, qb, qc, qd = st.columns(4)
            qa.markdown(card("Elite",      f"{len(elite):,}",      "High Perf · High Value",  color="#00e676"),  unsafe_allow_html=True)
            qb.markdown(card("Underrated", f"{len(underrated):,}", "High Perf · Low Value",   color="#00b0ff"),  unsafe_allow_html=True)
            qc.markdown(card("Overpriced", f"{len(overpriced):,}", "Low Perf · High Value",   color="#ff5252"),  unsafe_allow_html=True)
            qd.markdown(card("Developing", f"{len(developing):,}", "Low Perf · Low Value",    color="#ffd740"),  unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
            section_header("Underrated Players", "High performance, low market value — the smart signings")
            under_disp = underrated.nlargest(10, "Performance_Score")[
                ["Name", "Team", "Position", "Tactical_Role", "Performance_Score", "Market Value", "Age"]
            ].copy()
            under_disp["Market Value"]      = under_disp["Market Value"].apply(fmt_val)
            under_disp["Performance_Score"] = under_disp["Performance_Score"].round(1)
            under_disp.columns = ["Player", "Team", "Position", "Role", "Score", "Market Value", "Age"]
            st.dataframe(under_disp, use_container_width=True, hide_index=True)

    with tab_pred:
        section_header("Actual vs Predicted Market Value", "Points above the line = undervalued · Points below = overvalued")
        df_mv["Gap_Color"] = df_mv["Value_Gap"].apply(lambda x: "Undervalued" if x > 0 else "Overvalued")
        fig_mv = px.scatter(
            df_mv, x="Market Value", y="Predicted_Market_Value",
            color="Gap_Color", hover_name="Name",
            hover_data={"Team": True, "Position": True, "Value_Gap": True},
            color_discrete_map={"Undervalued": "#00e676", "Overvalued": "#ff5252"},
            opacity=0.75
        )
        max_v = df_mv[["Market Value", "Predicted_Market_Value"]].max().max()
        fig_mv.add_trace(go.Scatter(x=[0, max_v], y=[0, max_v], mode="lines",
                                    line=dict(color="#5a6a7a", dash="dot", width=1), name="Fair Value"))
        fig_mv.update_layout(**THEME, height=450)
        fig_mv.update_xaxes(title="Actual Market Value (€)")
        fig_mv.update_yaxes(title="Predicted Market Value (€)")
        st.plotly_chart(fig_mv, use_container_width=True)

    with tab_tables:
        col_u, col_o = st.columns(2)
        with col_u:
            section_header("Most Undervalued", "Predicted value >> Actual value")
            under = df_mv.nlargest(15, "Value_Gap")[["Name", "Team", "Position", "Market Value", "Predicted_Market_Value", "Value_Gap"]].copy()
            under["Market Value"]           = under["Market Value"].apply(fmt_val)
            under["Predicted_Market_Value"] = under["Predicted_Market_Value"].apply(fmt_val)
            under["Value_Gap"]              = under["Value_Gap"].apply(lambda x: f"+{fmt_val(x)}")
            under.columns = ["Player", "Team", "Position", "Actual", "Predicted", "Gap"]
            st.dataframe(under, use_container_width=True, hide_index=True, height=420)
        with col_o:
            section_header("Most Overvalued", "Actual value >> Predicted value")
            over = df_mv.nsmallest(15, "Value_Gap")[["Name", "Team", "Position", "Market Value", "Predicted_Market_Value", "Value_Gap"]].copy()
            over["Market Value"]           = over["Market Value"].apply(fmt_val)
            over["Predicted_Market_Value"] = over["Predicted_Market_Value"].apply(fmt_val)
            over["Value_Gap"]              = over["Value_Gap"].apply(fmt_gap)
            over.columns = ["Player", "Team", "Position", "Actual", "Predicted", "Gap"]
            st.dataframe(over, use_container_width=True, hide_index=True, height=420)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 6 — PLAYER SIMILARITY  (new — from 04_scouting_and_similarity.ipynb)
# ══════════════════════════════════════════════════════════════════════════
elif page == "🔁  Player Similarity":
    st.markdown(
        "<div style='padding:2rem 0 1.2rem 0;border-bottom:1px solid #1e2a38;margin-bottom:2rem'>"
        "<div style='font-family:Bebas Neue,sans-serif;font-size:3rem;letter-spacing:0.06em;line-height:1;color:#e8edf2'>"
        "PLAYER <span style='color:#bc8cff'>SIMILARITY</span></div>"
        "<div style='font-size:0.9rem;color:#5a6a7a;margin-top:0.6rem'>"
        "Cosine-similarity engine across 40+ per-90 &amp; rate stats · Find statistically similar players</div>"
        "</div>", unsafe_allow_html=True
    )

    all_names_sim = sorted(df_all["Name"].dropna().unique().tolist())

    # ── Controls ───────────────────────────────────────────────────────────
    ctrl1, ctrl2 = st.columns([2, 2])
    with ctrl1:
        sim_player = st.selectbox("Reference Player", all_names_sim, key="sim_player")
    with ctrl2:
        top_n_sim = st.slider("Number of Similar Players", 5, 25, 10, key="sim_topn")

    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        same_pos = st.checkbox("Same Position Only", value=True, key="sim_samepos")
    with f2:
        sim_max_age = st.selectbox("Max Age", ["Any"] + list(range(18, 41)), key="sim_age")
        sim_max_age = None if sim_max_age == "Any" else int(sim_max_age)
    with f3:
        sim_min_min = st.selectbox("Min Minutes", [0, 450, 900, 1350, 2000], key="sim_min")
        sim_min_min = None if sim_min_min == 0 else sim_min_min
    with f4:
        sim_max_mv = st.selectbox("Max Market Value", ["Any", "€5M", "€10M", "€25M", "€50M", "€100M"], key="sim_mv")
        mv_map_sim = {"€5M": 5e6, "€10M": 10e6, "€25M": 25e6, "€50M": 50e6, "€100M": 100e6}
        sim_max_mv = mv_map_sim.get(sim_max_mv, None)
    with f5:
        sim_leagues = st.multiselect("Leagues", sorted(df_all["League"].dropna().unique().tolist()),
                                     default=[], key="sim_leagues")
        sim_leagues = sim_leagues if sim_leagues else None

    # ── Stat selection for similarity ──────────────────────────────────────
    with st.expander("⚙️ Customise similarity stats", expanded=False):
        all_feat_labels = {
            c: c.replace(" (Per90)", "/90").replace("Pass Completion Rate", "Pass%")
               .replace("Dribble Success Rate", "Dribble%").replace("Shot Accuracy", "Shot%")
            for c in FEATURE_COLS
        }
        selected_feats = st.multiselect(
            "Stats used for similarity computation",
            options=FEATURE_COLS,
            default=FEATURE_COLS,
            format_func=lambda x: all_feat_labels[x],
            key="sim_feats"
        )
        if len(selected_feats) < 5:
            st.warning("Select at least 5 features for reliable similarity scoring.")
            selected_feats = FEATURE_COLS

    # ── Radar stat selection ───────────────────────────────────────────────
    with st.expander("📡 Customise radar chart stats", expanded=False):
        radar_opts = [m for m in RADAR_METRICS if m in df_all.columns]
        selected_radar = st.multiselect(
            "Stats shown on the comparison radar",
            options=radar_opts,
            default=radar_opts[:8],
            format_func=lambda x: x.replace(" (Per90)", "").replace("Pass Completion Rate", "Pass %"),
            key="sim_radar_stats"
        )
        if len(selected_radar) < 3:
            selected_radar = radar_opts[:8]

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Run similarity ─────────────────────────────────────────────────────
    ref_row, sim_df = find_similar_players(
        df_all,
        player_name      = sim_player,
        top_n            = top_n_sim,
        same_position    = same_pos,
        leagues          = sim_leagues,
        max_age          = sim_max_age,
        min_minutes      = sim_min_min,
        max_market_value = sim_max_mv,
        feature_cols     = selected_feats,
    )

    if ref_row is None:
        st.error(f"Player '{sim_player}' not found in dataset.")
        st.stop()

    if sim_df.empty:
        st.warning("No similar players found with the current filters. Try relaxing the constraints.")
        st.stop()

    # ── Reference player header ────────────────────────────────────────────
    ref_pos    = ref_row.get("Position", "—")
    ref_role   = ref_row.get("Tactical_Role", ref_row.get("GK_Role", "—"))
    ref_team   = ref_row.get("Team", "—")
    ref_league = {"premier-league": "Premier League", "la-liga": "La Liga"}.get(ref_row.get("League", ""), ref_row.get("League", ""))
    ref_mv     = fmt_val(ref_row.get("Market Value", np.nan))
    ref_score  = f"{ref_row.get('Performance_Score', 0):.1f}" if pd.notna(ref_row.get("Performance_Score")) else "—"
    ref_age    = int(ref_row["Age"]) if pd.notna(ref_row.get("Age")) else "—"

    st.markdown(
        f"<div style='background:#0f1419;border:1px solid #bc8cff44;border-top:2px solid #bc8cff;border-radius:12px;"
        f"padding:1.5rem 2rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:2rem'>"
        f"<div style='width:60px;height:60px;background:#161d26;border-radius:50%;display:flex;"
        f"align-items:center;justify-content:center;font-size:1.8rem;flex-shrink:0'>🔎</div>"
        f"<div style='flex:1'>"
        f"<div style='font-size:0.65rem;color:#bc8cff;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px'>Reference Player</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:2rem;letter-spacing:0.04em;color:#e8edf2;line-height:1'>{sim_player}</div>"
        f"<div style='font-size:0.85rem;color:#5a6a7a;margin-top:4px'>{ref_team} &nbsp;·&nbsp; {ref_league} &nbsp;·&nbsp; {ref_pos} &nbsp;·&nbsp; {ref_role} &nbsp;·&nbsp; Age {ref_age}</div>"
        f"</div>"
        f"<div style='display:flex;gap:2rem'>"
        f"<div style='text-align:right'>"
        f"<div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Score</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#bc8cff'>{ref_score}</div>"
        f"</div>"
        f"<div style='text-align:right'>"
        f"<div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Value</div>"
        f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#ffd740'>{ref_mv}</div>"
        f"</div></div></div>",
        unsafe_allow_html=True
    )

    # ── Two-column layout: Results + Radar ────────────────────────────────
    left_col, right_col = st.columns([5, 4], gap="large")

    with left_col:
        section_header(f"Top {len(sim_df)} Similar Players", f"Ranked by cosine similarity across {len(selected_feats)} stats")

        COLORS_CYCLE = ["#00e676", "#00b0ff", "#ffd740", "#ff5252", "#bc8cff",
                        "#ff6d00", "#26c6da", "#ec407a", "#66bb6a", "#ab47bc",
                        "#ef5350", "#42a5f5", "#ffca28", "#26a69a", "#8d6e63",
                        "#78909c", "#d4e157", "#f06292", "#4db6ac", "#ffa726",
                        "#29b6f6", "#9ccc65", "#ff7043", "#5c6bc0", "#26c6da"]

        for rank, (_, sim_row) in enumerate(sim_df.iterrows(), start=1):
            name      = sim_row.get("Name", "—")
            team      = sim_row.get("Team", "—")
            pos       = sim_row.get("Position", "—")
            role      = sim_row.get("Tactical_Role", "—")
            age       = int(sim_row["Age"]) if pd.notna(sim_row.get("Age")) else "—"
            mv        = fmt_val(sim_row.get("Market Value", np.nan))
            score     = f"{sim_row.get('Performance_Score', 0):.1f}" if pd.notna(sim_row.get("Performance_Score")) else "—"
            sim_pct   = sim_row.get("Similarity_%", 0)
            bar_w     = sim_pct
            c         = COLORS_CYCLE[rank % len(COLORS_CYCLE)]

            st.markdown(
                f"<div class='sim-card'>"
                f"<div style='display:flex;align-items:center;gap:0.8rem'>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem;color:#1e2a38;min-width:32px;text-align:center'>"
                f"<span style='color:{c}'>#{rank}</span></div>"
                f"<div style='flex:1'>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.15rem;letter-spacing:0.03em;color:#e8edf2;line-height:1.1'>{name}</div>"
                f"<div style='font-size:0.75rem;color:#5a6a7a;margin-top:2px'>{team} &nbsp;·&nbsp; {pos} &nbsp;·&nbsp; {role} &nbsp;·&nbsp; Age {age}</div>"
                f"</div>"
                f"<div style='text-align:right;flex-shrink:0'>"
                f"<div style='font-family:Bebas Neue,sans-serif;font-size:1.3rem;color:{c}'>{sim_pct:.1f}%</div>"
                f"<div style='font-size:0.62rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>Match</div>"
                f"</div>"
                f"<div style='text-align:right;flex-shrink:0;margin-left:0.8rem'>"
                f"<div style='font-size:0.85rem;color:#e8edf2;font-weight:500'>{mv}</div>"
                f"<div style='font-size:0.65rem;color:#5a6a7a'>Score: {score}</div>"
                f"</div></div>"
                f"<div style='height:3px;background:#1e2a38;border-radius:2px;margin-top:8px'>"
                f"<div style='height:100%;width:{bar_w:.1f}%;background:{c};border-radius:2px;opacity:0.7'></div></div>"
                f"</div>",
                unsafe_allow_html=True
            )

        # Table view toggle
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        if st.checkbox("Show as table", key="sim_table"):
            disp_sim = sim_df.copy()
            if "Market Value" in disp_sim.columns:
                disp_sim["Market Value"] = disp_sim["Market Value"].apply(fmt_val)
            if "Performance_Score" in disp_sim.columns:
                disp_sim["Performance_Score"] = disp_sim["Performance_Score"].round(1)
            st.dataframe(disp_sim, use_container_width=True, hide_index=True)

    with right_col:
        section_header("Radar Comparison", "Reference player vs selected match")

        compare_with_idx = st.selectbox(
            "Compare radar with",
            options=[f"#{i+1} — {r['Name']}" for i, (_, r) in enumerate(sim_df.iterrows())],
            key="sim_radar_pick"
        )
        compare_idx = int(compare_with_idx.split(" — ")[0].strip("#")) - 1
        compare_sim_row = sim_df.iloc[compare_idx]
        compare_name = compare_sim_row.get("Name")
        # sim_df only holds a subset of columns, fetch the full row for stats
        cmp_matches = df_all[df_all["Name"] == compare_name]
        compare_full_row = cmp_matches.iloc[0] if not cmp_matches.empty else compare_sim_row

        # Build pool for normalization (same position if possible)
        ref_pos_val = ref_row.get("Position", None)
        if ref_pos_val and ref_pos_val in df_full["Position"].values:
            radar_pool = df_full[df_full["Position"] == ref_pos_val]
        else:
            radar_pool = df_all

        radar_rows = {
            sim_player:   ref_row,
            compare_name: compare_full_row,
        }

        fig_radar = build_radar_fig(radar_pool, radar_rows, selected_radar, ["#bc8cff", "#ffd740"])
        if fig_radar:
            sim_pct_val = compare_sim_row.get("Similarity_%", 0)
            fig_radar.update_layout(title=dict(
                text=f"{sim_player} vs {compare_sim_row.get('Name','')} · {sim_pct_val:.1f}% match",
                font=dict(family="Bebas Neue, sans-serif", size=14, color="#e8edf2"),
                x=0.5
            ))
            st.plotly_chart(fig_radar, use_container_width=True)