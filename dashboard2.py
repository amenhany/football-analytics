import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Pitch IQ", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
:root {
    --bg:#080c10; --surface:#0f1419; --surface2:#161d26; --border:#1e2a38;
    --accent:#00e676; --accent2:#00b0ff; --gold:#ffd740; --red:#ff5252;
    --text:#e8edf2; --muted:#5a6a7a;
    --font-display:'Bebas Neue',sans-serif; --font-body:'DM Sans',sans-serif; --font-mono:'DM Mono',monospace;
}
html,body,[class*="css"]{font-family:var(--font-body)!important;background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 2rem 2rem 2rem!important;max-width:100%!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;padding-top:0!important;}
[data-testid="stSidebar"] .block-container{padding:1rem!important;}
[data-testid="stSidebarNav"]{display:none;}
[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:6px!important;color:var(--text)!important;}
.stTextInput input{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:6px!important;color:var(--text)!important;font-family:var(--font-body)!important;}
.stTextInput input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(0,230,118,0.15)!important;}
.stSlider [data-baseweb="slider"]{padding:0!important;}
[data-testid="metric-container"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:10px!important;padding:1.1rem 1.4rem!important;}
[data-testid="metric-container"] label{color:var(--muted)!important;font-size:0.7rem!important;font-weight:600!important;letter-spacing:0.1em!important;text-transform:uppercase!important;}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:var(--font-display)!important;font-size:2rem!important;letter-spacing:0.02em!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border)!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;border:none!important;color:var(--muted)!important;font-family:var(--font-body)!important;font-size:0.85rem!important;font-weight:500!important;padding:0.6rem 1.2rem!important;letter-spacing:0.03em!important;}
.stTabs [aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;background:transparent!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:8px!important;}
.stButton button{background:var(--accent)!important;color:#000!important;border:none!important;border-radius:6px!important;font-family:var(--font-body)!important;font-weight:600!important;}
label,.stSelectbox label,.stMultiSelect label,.stSlider label,.stTextInput label,.stRadio label{color:var(--muted)!important;font-size:0.72rem!important;font-weight:600!important;letter-spacing:0.08em!important;text-transform:uppercase!important;}
hr{border-color:var(--border)!important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}

/* Landing page elements */
.feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.feature-card:hover { border-color: #2a3d52; }
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.feature-card.green::before  { background: linear-gradient(90deg, #00e676, transparent); }
.feature-card.blue::before   { background: linear-gradient(90deg, #00b0ff, transparent); }
.feature-card.gold::before   { background: linear-gradient(90deg, #ffd740, transparent); }
.feature-card.red::before    { background: linear-gradient(90deg, #ff5252, transparent); }
.feature-card.purple::before { background: linear-gradient(90deg, #bc8cff, transparent); }

.stat-pill {
    display: inline-block;
    background: rgba(0,230,118,0.08);
    border: 1px solid rgba(0,230,118,0.2);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #00e676;
    margin-right: 8px;
    margin-bottom: 6px;
}
.audience-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text);
    margin: 4px;
}
.scout-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.7rem;}
</style>
""", unsafe_allow_html=True)

THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#e8edf2", size=12),
    colorway=["#00e676","#00b0ff","#ffd740","#ff5252","#bc8cff","#ff6d00"],
    xaxis=dict(gridcolor="#1e2a38", linecolor="#1e2a38", zeroline=False, tickfont=dict(color="#5a6a7a")),
    yaxis=dict(gridcolor="#1e2a38", linecolor="#1e2a38", zeroline=False, tickfont=dict(color="#5a6a7a")),
    legend=dict(bgcolor="rgba(15,20,25,0.8)", bordercolor="#1e2a38", borderwidth=1, font=dict(color="#e8edf2")),
    margin=dict(t=40, l=10, r=10, b=10),
    title_font=dict(family="Bebas Neue, sans-serif", color="#e8edf2", size=18),
)

@st.cache_data
def load_data():
    base_clean = "data/clean"
    base_proc  = "data/processed"

    df_master  = pd.read_csv(f"{base_proc}/master_player_ranking_1500min.csv")
    df_full    = pd.read_csv(f"{base_clean}/master_player_ranking.csv")   # for explorer & profile
    df_gk      = pd.read_csv(f"{base_clean}/classified_goalkeepers.csv")
    df_pred    = pd.read_csv(f"{base_proc}/all_player_predictions.csv")

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
        if "Unnamed: 0" in df.columns: df.drop(columns=["Unnamed: 0"], inplace=True)
    if "Unnamed: 0" in df_gk.columns: df_gk.drop(columns=["Unnamed: 0"], inplace=True)

    for col in ["Market Value","Age"]:
        df_master[col] = pd.to_numeric(df_master[col], errors="coerce")
        df_full[col]   = pd.to_numeric(df_full[col],   errors="coerce")
        df_gk[col]     = pd.to_numeric(df_gk[col],     errors="coerce")

    df_full   = df_full.merge(df_pred[["Name","Predicted_Market_Value"]], on="Name", how="left")
    df_master = df_master.merge(df_pred[["Name","Predicted_Market_Value"]], on="Name", how="left")
    df_full["Value_Gap"]   = df_full["Predicted_Market_Value"]   - df_full["Market Value"]
    df_master["Value_Gap"] = df_master["Predicted_Market_Value"] - df_master["Market Value"]

    df_gk["GK_Role"] = df_gk.apply(
        lambda r: "Sweeper Keeper"
        if pd.notna(r.get("Sweeper Keeper_Score")) and pd.notna(r.get("Shot Stopper_Score"))
           and r["Sweeper Keeper_Score"] > r["Shot Stopper_Score"] else "Shot Stopper", axis=1)

    for df in [df_master, df_full]:
        df["League_Label"] = df["League"].map({"premier-league":"Premier League","la-liga":"La Liga"}).fillna(df["League"])
    df_gk["League_Label"] = df_gk["League"].map({"premier-league":"Premier League","la-liga":"La Liga"}).fillna(df_gk["League"])

    return df_master, df_full, df_gk, df_pred, pos_dfs

df_master, df_full, df_gk, df_pred, pos_dfs = load_data()

def fmt_val(v):
    if pd.isna(v): return "N/A"
    if v >= 1e9:   return f"€{v/1e9:.2f}B"
    if v >= 1e6:   return f"€{v/1e6:.1f}M"
    if v >= 1e3:   return f"€{v/1e3:.0f}K"
    return f"€{v:.0f}"

def card(label, value, sub=None, color="#00e676"):
    sub_html = f"<div style='font-size:0.72rem;color:#5a6a7a;margin-top:2px'>{sub}</div>" if sub else ""
    return f"""<div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1.1rem 1.4rem;'>
        <div style='font-size:0.65rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>{label}</div>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.9rem;letter-spacing:0.02em;color:{color}'>{value}</div>
        {sub_html}</div>"""

def section_header(text, sub=None):
    sub_html = f"<div style='font-size:0.85rem;color:#5a6a7a;margin-top:4px;font-weight:400'>{sub}</div>" if sub else ""
    st.markdown(f"""<div style='margin:2rem 0 1.2rem 0;'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;letter-spacing:0.05em;color:#e8edf2'>{text}</div>
        {sub_html}</div>""", unsafe_allow_html=True)

def scout_player_card(row, badge_label, badge_color, stat_line):
    mv = fmt_val(row.get("Market Value", np.nan))
    score = f"{row.get('Performance_Score', 0):.1f}"
    return f"""
    <div class='scout-card'>
        <div style='display:flex;align-items:flex-start;justify-content:space-between;'>
            <div>
                <span style='background:{badge_color}22;color:{badge_color};font-size:0.65rem;font-weight:700;
                      letter-spacing:0.1em;text-transform:uppercase;padding:2px 8px;border-radius:4px;
                      border:1px solid {badge_color}44'>{badge_label}</span>
                <div style='font-family:Bebas Neue,sans-serif;font-size:1.3rem;letter-spacing:0.04em;
                      color:#e8edf2;margin-top:6px;line-height:1'>{row.get('Name','')}</div>
                <div style='font-size:0.78rem;color:#5a6a7a;margin-top:3px'>
                    {row.get('Team','')} &nbsp;·&nbsp; {row.get('Position','')} &nbsp;·&nbsp; {row.get('Tactical_Role','')}
                </div>
            </div>
            <div style='text-align:right;flex-shrink:0;margin-left:1rem'>
                <div style='font-family:Bebas Neue,sans-serif;font-size:1.4rem;color:{badge_color}'>{score}</div>
                <div style='font-size:0.65rem;color:#5a6a7a;letter-spacing:0.06em;text-transform:uppercase'>Score</div>
                <div style='font-size:0.85rem;color:#e8edf2;margin-top:4px;font-weight:500'>{mv}</div>
            </div>
        </div>
        <div style='font-size:0.78rem;color:#5a6a7a;margin-top:8px;padding-top:8px;border-top:1px solid #1e2a38'>{stat_line}</div>
    </div>"""

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.5rem 0.5rem 1rem 0.5rem;border-bottom:1px solid #1e2a38;margin-bottom:1rem'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;letter-spacing:0.08em;color:#00e676;line-height:1'>PITCH IQ</div>
        <div style='font-size:0.72rem;color:#5a6a7a;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Football Analytics</div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("Navigation",
        ["🏠  Overview","🔍  Player Explorer","👤  Player Profile","🕵️  Scouting Report","💰  Market Values"],
        label_visibility="collapsed")

    st.markdown("<div style='margin-top:1.5rem;padding-top:1rem;border-top:1px solid #1e2a38'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.65rem;color:#5a6a7a;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem'>GLOBAL FILTERS</div>", unsafe_allow_html=True)
    league_opts = ["All"] + sorted(df_full["League_Label"].dropna().unique().tolist())
    sel_league  = st.selectbox("League", league_opts)
    st.markdown("</div>", unsafe_allow_html=True)

# Global filter applies to both datasets
df_base      = df_master.copy()
df_full_base = df_full.copy()
if sel_league != "All":
    df_base      = df_base[df_base["League_Label"]      == sel_league]
    df_full_base = df_full_base[df_full_base["League_Label"] == sel_league]

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW (Landing Page)
# ══════════════════════════════════════════════════════════════════════════
if page == "🏠  Overview":

    total_players = len(df_full) + len(df_gk)
    total_mv      = (df_full["Market Value"].sum() + df_gk["Market Value"].sum()) / 1e9

    # ── HERO ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='
        min-height: 340px;
        padding: 3.5rem 0 3rem 0;
        border-bottom: 1px solid #1e2a38;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    '>
        <!-- background grid lines for depth -->
        <div style='
            position:absolute;top:0;left:0;right:0;bottom:0;
            background-image: repeating-linear-gradient(90deg,#1e2a3820 0px,transparent 1px,transparent 80px),
                              repeating-linear-gradient(180deg,#1e2a3820 0px,transparent 1px,transparent 80px);
            pointer-events:none;
        '></div>
        <!-- glowing orb -->
        <div style='
            position:absolute;top:-80px;right:-60px;
            width:420px;height:420px;
            background:radial-gradient(circle,rgba(0,230,118,0.07) 0%,transparent 70%);
            pointer-events:none;
        '></div>

        <div style='position:relative;'>
            <div style='
                display:inline-block;
                background:rgba(0,230,118,0.08);
                border:1px solid rgba(0,230,118,0.25);
                border-radius:100px;
                padding:5px 16px;
                font-size:0.68rem;
                font-weight:700;
                letter-spacing:0.14em;
                text-transform:uppercase;
                color:#00e676;
                margin-bottom:1.4rem;
            '>⚽ 2025/26 Season &nbsp;·&nbsp; Premier League &amp; La Liga</div>

            <div style='
                font-family:Bebas Neue,sans-serif;
                font-size:clamp(3rem,6vw,5.2rem);
                letter-spacing:0.04em;
                line-height:0.95;
                color:#e8edf2;
                margin-bottom:1.4rem;
            '>
                FOOTBALL.<br>
                <span style='color:#00e676;'>DECODED.</span>
            </div>

            <div style='
                font-size:1rem;
                color:#5a6a7a;
                max-width:580px;
                line-height:1.7;
                margin-bottom:2.2rem;
            '>
                Two leagues. 735 players. Every stat that matters.<br>
                Performance scores, tactical profiles, and ML-powered market value intelligence —
                all in one place.
            </div>

            <!-- Big stats -->
            <div style='display:flex;gap:2.5rem;flex-wrap:wrap;align-items:flex-end;'>
                <div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:3.8rem;color:#00e676;line-height:1;letter-spacing:0.02em'>{total_players}</div>
                    <div style='font-size:0.72rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Players Tracked</div>
                </div>
                <div style='width:1px;height:60px;background:#1e2a38;'></div>
                <div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:3.8rem;color:#ffd740;line-height:1;letter-spacing:0.02em'>€{total_mv:.1f}B</div>
                    <div style='font-size:0.72rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Total Market Value</div>
                </div>
                <div style='width:1px;height:60px;background:#1e2a38;'></div>
                <div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:3.8rem;color:#00b0ff;line-height:1;letter-spacing:0.02em'>46</div>
                    <div style='font-size:0.72rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Tactical Roles</div>
                </div>
                <div style='width:1px;height:60px;background:#1e2a38;'></div>
                <div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:3.8rem;color:#bc8cff;line-height:1;letter-spacing:0.02em'>40+</div>
                    <div style='font-size:0.72rem;color:#5a6a7a;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Clubs Covered</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FEATURES ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-family:Bebas Neue,sans-serif;font-size:0.75rem;letter-spacing:0.18em;color:#5a6a7a;text-transform:uppercase;margin-bottom:1.2rem'>
        What's Inside
    </div>""", unsafe_allow_html=True)

    features = [
        {
            "color": "green", "accent": "#00e676", "emoji": "🔍",
            "title": "Player Explorer",
            "desc": "Search and filter all 735 players by position, tactical role, age, and league. Sort by performance, market value, or name. Includes a full goalkeeper database with GK-specific filters.",
            "pills": ["735 Players", "7 Positions", "46 Roles", "GK Mode"],
            "page": "Player Explorer",
        },
        {
            "color": "blue", "accent": "#00b0ff", "emoji": "👤",
            "title": "Player Profile",
            "desc": "Deep dive into any player. Radar chart normalized against position peers, role fit scores, a full stat breakdown across 5 categories, and an actual vs predicted market value card.",
            "pills": ["Radar Chart", "Role Scores", "5 Stat Tabs", "Value Gap"],
            "page": "Player Profile",
        },
        {
            "color": "gold", "accent": "#ffd740", "emoji": "🕵️",
            "title": "Scouting Report",
            "desc": "Six curated categories of players to watch: Top Performers, On Fire, Rising Stars (U21), Undervalued Gems, Defensive Walls, and Best Value for Money. Data-driven, not opinion-driven.",
            "pills": ["Top Performers", "U21 Stars", "Hidden Gems", "On Fire"],
            "page": "Scouting Report",
        },
        {
            "color": "red", "accent": "#ff5252", "emoji": "💰",
            "title": "Market Value Intelligence",
            "desc": "Our ML model predicts what every player should be worth based on their stats. See who the market is sleeping on, who is massively overpriced, and where the real bargains are.",
            "pills": ["ML Predictions", "Value Gap", "Undervalued", "Overpriced"],
            "page": "Market Values",
        },
    ]

    col1, col2 = st.columns(2, gap="medium")
    for i, f in enumerate(features):
        col = col1 if i % 2 == 0 else col2
        hex_color = f["accent"].lstrip("#")
        r, g, b   = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
        pills_html = "".join([
            f"<span class='stat-pill' style='border-color:rgba({r},{g},{b},0.3);color:{f['accent']};background:rgba({r},{g},{b},0.06)'>{p}</span>"
            for p in f["pills"]
        ])
        col.markdown(f"""
        <div class='feature-card {f["color"]}' style='margin-bottom:1rem'>
            <div style='display:flex;align-items:flex-start;gap:1rem;margin-bottom:1rem'>
                <div style='font-size:1.8rem;line-height:1;flex-shrink:0'>{f["emoji"]}</div>
                <div>
                    <div style='font-family:Bebas Neue,sans-serif;font-size:1.4rem;letter-spacing:0.06em;color:{f["accent"]};line-height:1'>{f["title"]}</div>
                </div>
            </div>
            <div style='font-size:0.88rem;color:#8a9bb0;line-height:1.65;margin-bottom:1.2rem'>{f["desc"]}</div>
            <div style='margin-bottom:0'>{pills_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── WHO IS THIS FOR ────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin:3rem 0 1.2rem 0;'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;letter-spacing:0.05em;color:#e8edf2'>Who Is This For?</div>
        <div style='font-size:0.85rem;color:#5a6a7a;margin-top:4px'>Pitch IQ is built for anyone who wants to understand football beyond the scoreline</div>
    </div>""", unsafe_allow_html=True)

    audiences = [
        ("🏟️", "Football Clubs",        "Recruitment teams & scouts looking for data-backed player assessments"),
        ("📊", "Performance Analysts",  "Professionals who need clean, filterable stats across two major leagues"),
        ("🧠", "Tactical Enthusiasts",  "Fans who want to understand positional roles and playing styles"),
        ("📰", "Journalists & Writers", "Reporters who want facts and rankings to back their stories"),
        ("🎮", "Fantasy Managers",      "Managers looking for form players, rising stars, and value picks"),
        ("🎓", "Students & Researchers","Big Data students or academics working with real sports datasets"),
    ]

    a1, a2, a3 = st.columns(3)
    for i, (emoji, title, desc) in enumerate(audiences):
        col = [a1, a2, a3][i % 3]
        col.markdown(f"""
        <div style='background:#0f1419;border:1px solid #1e2a38;border-radius:12px;padding:1.3rem 1.4rem;margin-bottom:0.8rem;'>
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:0.5rem'>
                <span style='font-size:1.3rem'>{emoji}</span>
                <span style='font-family:Bebas Neue,sans-serif;font-size:1.05rem;letter-spacing:0.05em;color:#e8edf2'>{title}</span>
            </div>
            <div style='font-size:0.8rem;color:#5a6a7a;line-height:1.55'>{desc}</div>
        </div>""", unsafe_allow_html=True)

    # ── DATA SOURCES ───────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin:2.5rem 0 1rem 0;padding:1.5rem 2rem;background:#0f1419;border:1px solid #1e2a38;border-radius:12px;display:flex;flex-wrap:wrap;align-items:center;gap:2rem;'>
        <div>
            <div style='font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>Data Sources</div>
            <div style='display:flex;gap:1.5rem;flex-wrap:wrap'>
                <span style='font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.06em;color:#e8edf2'>Transfermarkt</span>
                <span style='color:#1e2a38'>·</span>
                <span style='font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.06em;color:#e8edf2'>Footystats</span>
            </div>
        </div>
        <div style='width:1px;height:40px;background:#1e2a38'></div>
        <div>
            <div style='font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>Coverage</div>
            <div style='font-size:0.88rem;color:#e8edf2'>Premier League &amp; La Liga &nbsp;·&nbsp; 2025/26 Season</div>
        </div>
        <div style='width:1px;height:40px;background:#1e2a38'></div>
        <div>
            <div style='font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>Rankings Filter</div>
            <div style='font-size:0.88rem;color:#e8edf2'>1,500+ minutes played &nbsp;·&nbsp; Serious starters only</div>
        </div>
        <div style='width:1px;height:40px;background:#1e2a38'></div>
        <div>
            <div style='font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>ML Model</div>
            <div style='font-size:0.88rem;color:#e8edf2'>Gradient Boosting &nbsp;·&nbsp; Market Value Prediction</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLAYER EXPLORER
# ══════════════════════════════════════════════════════════════════════════
elif page == "🔍  Player Explorer":
    section_header("Player Explorer", "Browse, filter and search the full player database")

    mode = st.radio("Player Type", ["⚽ Outfield Players", "🥅 Goalkeepers"], horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    if mode == "⚽ Outfield Players":
        df_pool = df_full_base.copy()
        f1,f2,f3,f4,f5 = st.columns([2,2,2,2,1])
        with f1: search  = st.text_input("Search", placeholder="Player name or team...")
        with f2:
            pos_opts = ["All Positions"] + sorted(df_pool["Position"].dropna().unique().tolist())
            sel_pos  = st.selectbox("Position", pos_opts)
        with f3:
            role_opts = ["All Roles"] + sorted(df_pool["Tactical_Role"].dropna().unique().tolist())
            sel_role  = st.selectbox("Tactical Role", role_opts)
        with f4:
            min_age, max_age = int(df_pool["Age"].min()), int(df_pool["Age"].max())
            age_range = st.slider("Age Range", min_age, max_age, (min_age, max_age))
        with f5:
            sort_by = st.selectbox("Sort By", ["Performance Score","Market Value","Age","Name"])

        df_exp = df_pool.copy()
        if search:
            mask = (df_exp["Name"].str.contains(search, case=False, na=False) |
                    df_exp["Team"].str.contains(search, case=False, na=False))
            df_exp = df_exp[mask]
        if sel_pos  != "All Positions": df_exp = df_exp[df_exp["Position"]      == sel_pos]
        if sel_role != "All Roles":     df_exp = df_exp[df_exp["Tactical_Role"] == sel_role]
        df_exp = df_exp[df_exp["Age"].between(*age_range)]
        sort_map = {"Performance Score":"Performance_Score","Market Value":"Market Value","Age":"Age","Name":"Name"}
        df_exp = df_exp.sort_values(sort_map[sort_by], ascending=(sort_by=="Name"))

        st.markdown(f"<div style='font-size:0.8rem;color:#5a6a7a;margin-bottom:0.8rem'>{len(df_exp)} players found</div>", unsafe_allow_html=True)
        disp = df_exp[["Name","Team","League_Label","Position","Tactical_Role","Age","Market Value","Performance_Score","Overall_Rank"]].copy()
        disp["Market Value"]      = disp["Market Value"].apply(fmt_val)
        disp["Performance_Score"] = disp["Performance_Score"].round(1)
        disp.columns = ["Player","Team","League","Position","Role","Age","Market Value","Score","Rank"]
        st.dataframe(disp, use_container_width=True, hide_index=True, height=520)

        st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
        section_header("Filtered Summary")
        s1,s2,s3,s4 = st.columns(4)
        s1.markdown(card("Players",          f"{len(df_exp):,}"),                            unsafe_allow_html=True)
        s2.markdown(card("Avg Market Value", fmt_val(df_exp["Market Value"].mean())),         unsafe_allow_html=True)
        s3.markdown(card("Avg Age",          f"{df_exp['Age'].mean():.1f}"),                  unsafe_allow_html=True)
        s4.markdown(card("Avg Perf. Score",  f"{df_exp['Performance_Score'].mean():.1f}"),    unsafe_allow_html=True)

    else:
        df_gk_base = df_gk.copy()
        if sel_league != "All":
            df_gk_base = df_gk_base[df_gk_base["League_Label"] == sel_league]

        f1,f2,f3,f4 = st.columns([2,2,2,2])
        with f1: gk_search    = st.text_input("Search", placeholder="Goalkeeper name or team...", key="gk_search")
        with f2:
            sel_gk_role = st.selectbox("GK Role", ["All Roles","Shot Stopper","Sweeper Keeper"], key="gk_role")
        with f3:
            gk_min_age = int(df_gk_base["Age"].min()); gk_max_age = int(df_gk_base["Age"].max())
            gk_age_range = st.slider("Age Range", gk_min_age, gk_max_age, (gk_min_age, gk_max_age), key="gk_age")
        with f4:
            gk_sort = st.selectbox("Sort By", ["Shot Stopper Score","Sweeper Keeper Score","Market Value","Age","Name"], key="gk_sort")

        df_gk_exp = df_gk_base.copy()
        if gk_search:
            mask = (df_gk_exp["Name"].str.contains(gk_search, case=False, na=False) |
                    df_gk_exp["Team"].str.contains(gk_search, case=False, na=False))
            df_gk_exp = df_gk_exp[mask]
        if sel_gk_role != "All Roles": df_gk_exp = df_gk_exp[df_gk_exp["GK_Role"] == sel_gk_role]
        df_gk_exp = df_gk_exp[df_gk_exp["Age"].between(*gk_age_range)]
        gk_sort_map = {"Shot Stopper Score":"Shot Stopper_Score","Sweeper Keeper Score":"Sweeper Keeper_Score",
                       "Market Value":"Market Value","Age":"Age","Name":"Name"}
        sort_col = gk_sort_map[gk_sort]
        if sort_col in df_gk_exp.columns:
            df_gk_exp = df_gk_exp.sort_values(sort_col, ascending=(gk_sort=="Name"))

        st.markdown(f"<div style='font-size:0.8rem;color:#5a6a7a;margin-bottom:0.8rem'>{len(df_gk_exp)} goalkeepers found</div>", unsafe_allow_html=True)
        show_cols = [c for c in ["Name","Team","League_Label","Age","Market Value","GK_Role",
                                  "Shot Stopper_Score","Sweeper Keeper_Score","Save Percentage","Clean Sheets","Minutes"] if c in df_gk_exp.columns]
        gk_disp = df_gk_exp[show_cols].copy()
        gk_disp["Market Value"] = gk_disp["Market Value"].apply(fmt_val)
        if "Save Percentage" in gk_disp.columns:
            gk_disp["Save Percentage"] = gk_disp["Save Percentage"].apply(
                lambda x: f"{x*100:.1f}%" if pd.notna(x) and x<=1 else (f"{x:.1f}%" if pd.notna(x) else "—"))
        for sc in ["Shot Stopper_Score","Sweeper Keeper_Score"]:
            if sc in gk_disp.columns: gk_disp[sc] = gk_disp[sc].round(1)
        st.dataframe(gk_disp, use_container_width=True, hide_index=True, height=520)

        st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
        section_header("Filtered Summary")
        s1,s2,s3,s4 = st.columns(4)
        s1.markdown(card("Goalkeepers",      f"{len(df_gk_exp):,}"),                              unsafe_allow_html=True)
        s2.markdown(card("Avg Market Value", fmt_val(df_gk_exp["Market Value"].mean())),           unsafe_allow_html=True)
        s3.markdown(card("Avg Age",          f"{df_gk_exp['Age'].mean():.1f}"),                    unsafe_allow_html=True)
        ss = (df_gk_exp["GK_Role"] == "Shot Stopper").sum()
        s4.markdown(card("Shot Stoppers",    f"{ss}", f"{len(df_gk_exp)-ss} Sweeper Keepers"),     unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — PLAYER PROFILE
# ══════════════════════════════════════════════════════════════════════════
elif page == "👤  Player Profile":
    section_header("Player Profile", "Deep dive into any player's stats and tactical role")

    all_names = sorted(df_full["Name"].dropna().unique().tolist()) + sorted(df_gk["Name"].dropna().unique().tolist())
    sel_name  = st.selectbox("Select Player", all_names)

    row = df_full[df_full["Name"] == sel_name]
    is_gk = False
    if row.empty:
        row = df_gk[df_gk["Name"] == sel_name]
        is_gk = True
    if row.empty:
        st.warning("Player not found.")
        st.stop()
    row = row.iloc[0]

    league_label = {"premier-league":"Premier League","la-liga":"La Liga"}.get(row.get("League",""), row.get("League",""))
    st.markdown(f"""
    <div style='background:#0f1419;border:1px solid #1e2a38;border-radius:12px;padding:1.8rem 2rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:2rem'>
        <div style='width:72px;height:72px;background:#161d26;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;flex-shrink:0'>⚽</div>
        <div style='flex:1'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:2.4rem;letter-spacing:0.04em;color:#e8edf2;line-height:1'>{row['Name']}</div>
            <div style='font-size:0.9rem;color:#5a6a7a;margin-top:4px'>{row.get('Team','')} &nbsp;·&nbsp; {league_label} &nbsp;·&nbsp; Age {int(row['Age']) if pd.notna(row['Age']) else 'N/A'}</div>
        </div>
        <div style='text-align:right'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:1.1rem;color:#00e676;letter-spacing:0.08em'>{row.get('Position','')}</div>
            <div style='font-size:0.85rem;color:#5a6a7a;margin-top:2px'>{row.get('Tactical_Role','')}</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#ffd740;margin-top:4px'>{fmt_val(row.get('Market Value',np.nan))}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not is_gk:
        m1,m2,m3,m4,m5 = st.columns(5)
        m1.markdown(card("Performance Score", f"{row.get('Performance_Score',0):.1f}", "Out of 100", color="#00e676"), unsafe_allow_html=True)
        m2.markdown(card("Overall Rank",  f"#{int(row.get('Overall_Rank',0))}" if pd.notna(row.get('Overall_Rank')) else "N/A", "Across all positions"), unsafe_allow_html=True)
        m3.markdown(card("Goals (P90)",   f"{row.get('Goals Scored (Per90)',0):.2f}"), unsafe_allow_html=True)
        m4.markdown(card("Assists (P90)", f"{row.get('Assists (Per90)',0):.2f}"),      unsafe_allow_html=True)
        pcr = row.get('Pass Completion Rate', 0)
        m5.markdown(card("Pass %", f"{pcr*100:.0f}%" if pd.notna(pcr) and pcr<=1 else f"{pcr:.0f}%"), unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        sp = row.get('Save Percentage', 0)
        m1.markdown(card("Save %",       f"{sp*100:.1f}%" if pd.notna(sp) and sp<=1 else f"{sp:.1f}%"), unsafe_allow_html=True)
        m2.markdown(card("Saves (P90)",  f"{row.get('Saves (Per90)',0):.2f}"), unsafe_allow_html=True)
        m3.markdown(card("Clean Sheets", f"{int(row.get('Clean Sheets',0))}" if pd.notna(row.get('Clean Sheets')) else "N/A"), unsafe_allow_html=True)
        m4.markdown(card("GK Role",      row.get("GK_Role",""), color="#00b0ff"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3,2])

    with col_l:
        section_header("Radar Profile", "Per-90 stats vs position peers")
        if not is_gk:
            stat_cols_map = {
                "Goals (P90)":      "Goals Scored (Per90)",
                "Assists (P90)":    "Assists (Per90)",
                "Key Passes (P90)": "Key Passes (Per90)",
                "Tackles (P90)":    "Tackles (Per90)",
                "Interceptions":    "Interceptions (Per90)",
                "Dribbles (P90)":   "Successful Dribbles (Per90)",
                "Shots OT (P90)":   "Shots On Target (Per90)",
                "xG (P90)":         "Expected Goals (xG) (Per90)",
            }
            pos_df = df_full[df_full["Position"] == row.get("Position","")]
            labels = list(stat_cols_map.keys())
            vals = []
            for label, col_name in stat_cols_map.items():
                if col_name in pos_df.columns:
                    col_data = pd.to_numeric(pos_df[col_name], errors="coerce")
                    cmax=col_data.quantile(0.95); cmin=col_data.min()
                    raw=pd.to_numeric(row.get(col_name,0),errors="coerce") or 0
                    vals.append(max(0,min(1,(raw-cmin)/(cmax-cmin) if cmax>cmin else 0)))
                else:
                    vals.append(0)
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=vals+vals[:1], theta=labels+[labels[0]],
                fill="toself", fillcolor="rgba(0,230,118,0.15)",
                line=dict(color="#00e676",width=2), marker=dict(size=6,color="#00e676")))
            fig_r.update_layout(**THEME, height=360,
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True,range=[0,1],showticklabels=False,gridcolor="#1e2a38",linecolor="#1e2a38"),
                    angularaxis=dict(tickfont=dict(color="#e8edf2",size=11),gridcolor="#1e2a38",linecolor="#1e2a38")),
                showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            gk_labels   = ["Saves (P90)","Interceptions","Clearances","Pass Comp %","Clean Sheets"]
            gk_cols_map = ["Saves (Per90)","Interceptions (Per90)","Clearances (Per90)","Pass Completion Rate","Clean Sheets"]
            gk_vals = []
            for i, col_name in enumerate(gk_cols_map):
                if col_name in df_gk.columns:
                    col_data=pd.to_numeric(df_gk[col_name],errors="coerce")
                    cmax=col_data.quantile(0.95); cmin=col_data.min()
                    raw=pd.to_numeric(row.get(col_name,0),errors="coerce") or 0
                    gk_vals.append(max(0,min(1,(raw-cmin)/(cmax-cmin) if cmax>cmin else 0)))
                else:
                    gk_vals.append(0)
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=gk_vals+gk_vals[:1], theta=gk_labels+[gk_labels[0]],
                fill="toself", fillcolor="rgba(0,176,255,0.15)",
                line=dict(color="#00b0ff",width=2), marker=dict(size=6,color="#00b0ff")))
            fig_r.update_layout(**THEME, height=360,
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True,range=[0,1],showticklabels=False,gridcolor="#1e2a38",linecolor="#1e2a38"),
                    angularaxis=dict(tickfont=dict(color="#e8edf2",size=11),gridcolor="#1e2a38",linecolor="#1e2a38")),
                showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)

    with col_r:
        section_header("Role Scores", "Fit for each tactical role")
        if not is_gk:
            score_cols = [c for c in df_full.columns if c.endswith("_Score") and pd.notna(row.get(c))]
            if score_cols:
                scores = {c.replace("_Score","").replace("_"," "): round(row[c],1) for c in score_cols if pd.notna(row.get(c))}
                scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
                role_df = pd.DataFrame({"Role":list(scores.keys()),"Score":list(scores.values())})
                fig_s = px.bar(role_df, x="Score", y="Role", orientation="h",
                               color="Score", color_continuous_scale=["#1e2a38","#ffd740"], range_x=[0,100])
                fig_s.update_layout(**THEME, height=360, coloraxis_showscale=False)
                fig_s.update_traces(marker_line_width=0)
                fig_s.update_yaxes(title="", categoryorder="total ascending")
                st.plotly_chart(fig_s, use_container_width=True)
        else:
            gk_scores = {c.replace("_Score","").replace("_"," "): round(row[c],1)
                         for c in ["Shot Stopper_Score","Sweeper Keeper_Score"]
                         if c in row.index and pd.notna(row[c])}
            if gk_scores:
                gk_df = pd.DataFrame({"Role":list(gk_scores.keys()),"Score":list(gk_scores.values())})
                fig_s = px.bar(gk_df, x="Score", y="Role", orientation="h",
                               color="Score", color_continuous_scale=["#1e2a38","#00b0ff"], range_x=[0,100])
                fig_s.update_layout(**THEME, height=180, coloraxis_showscale=False)
                fig_s.update_traces(marker_line_width=0)
                st.plotly_chart(fig_s, use_container_width=True)

        if not is_gk and pd.notna(row.get("Predicted_Market_Value")):
            section_header("Market Value", "Actual vs predicted")
            actual=row["Market Value"]; predicted=row["Predicted_Market_Value"]
            gap=predicted-actual; color="#00e676" if gap>0 else "#ff5252"
            label="Undervalued" if gap>0 else "Overvalued"
            st.markdown(f"""
            <div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1.2rem'>
                <div style='display:flex;justify-content:space-between;margin-bottom:0.8rem'>
                    <div><div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Actual</div>
                         <div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem'>{fmt_val(actual)}</div></div>
                    <div style='text-align:right'><div style='font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:0.08em'>Predicted</div>
                         <div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem'>{fmt_val(predicted)}</div></div>
                </div>
                <div style='height:4px;background:#1e2a38;border-radius:2px;margin-bottom:0.8rem'>
                    <div style='height:100%;width:{min(100,abs(gap)/max(actual,predicted)*100+50):.0f}%;background:{color};border-radius:2px'></div>
                </div>
                <div style='font-size:0.85rem;color:{color};font-weight:600'>{label} by {fmt_val(abs(gap))}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Full Stats Breakdown")
    tab_g,tab_att,tab_def,tab_pass,tab_drib = st.tabs(["📋 General","⚽ Attacking","🛡 Defending","📤 Passing","🏃 Dribbling"])

    def stat_row(label, val, per90=None):
        v = f"{val:.2f}" if isinstance(val,(float,np.floating)) and pd.notna(val) else (str(int(val)) if pd.notna(val) else "—")
        p = f"{per90:.2f}" if per90 is not None and pd.notna(per90) else "—"
        return f"<tr><td style='padding:6px 12px;color:#5a6a7a;font-size:0.83rem'>{label}</td><td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right'>{v}</td><td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right;color:#5a6a7a'>{p}</td></tr>"
    tbl_h = "<table style='width:100%;border-collapse:collapse'><tr style='border-bottom:1px solid #1e2a38'><th style='padding:6px 12px;text-align:left;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>STAT</th><th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>TOTAL</th><th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>PER 90</th></tr>"
    with tab_g:
        h=tbl_h+stat_row("Matches Played",row.get("Matches Played"))+stat_row("Minutes",row.get("Minutes"))+stat_row("Matches Started",row.get("Matches Started"))+stat_row("Yellow Cards",row.get("Yellow Cards"))+stat_row("Red Cards",row.get("Red Cards"))+stat_row("Fouls Committed",row.get("Fouls Committed"),row.get("Fouls Committed (Per90)"))+stat_row("Fouled Against",row.get("Fouled Against"),row.get("Fouled Against (Per90)"))+"</table>"
        st.markdown(h, unsafe_allow_html=True)
    with tab_att:
        h=tbl_h+stat_row("Goals Scored",row.get("Goals Scored"),row.get("Goals Scored (Per90)"))+stat_row("xG",row.get("Expected Goals (xG)"),row.get("Expected Goals (xG) (Per90)"))+stat_row("Shots Taken",row.get("Shots Taken"),row.get("Shots Taken (Per90)"))+stat_row("Shots On Target",row.get("Shots On Target"),row.get("Shots On Target (Per90)"))+stat_row("Shot Accuracy",row.get("Shot Accuracy"))+stat_row("Goal Involvement",row.get("Goal Involvement"),row.get("Goal Involvement (Per90)"))+"</table>"
        st.markdown(h, unsafe_allow_html=True)
    with tab_def:
        h=tbl_h+stat_row("Tackles",row.get("Tackles"),row.get("Tackles (Per90)"))+stat_row("Interceptions",row.get("Interceptions"),row.get("Interceptions (Per90)"))+stat_row("Clearances",row.get("Clearances"),row.get("Clearances (Per90)"))+stat_row("Shots Blocked",row.get("Shots Blocked"),row.get("Shots Blocked (Per90)"))+stat_row("Aerial Duels Won",row.get("Aerial Duels Won"),row.get("Aerial Duels Won (Per90)"))+stat_row("Ground Duels Won",row.get("Ground Duels Won"),row.get("Ground Duels Won (Per90)"))+stat_row("Dribbled Past",row.get("Dribbled Past"),row.get("Dribbled Past (Per90)"))+"</table>"
        st.markdown(h, unsafe_allow_html=True)
    with tab_pass:
        h=tbl_h+stat_row("Assists",row.get("Assists"),row.get("Assists (Per90)"))+stat_row("xA",row.get("Expected Assists (xA)"),row.get("Expected Assists (xA) (Per90)"))+stat_row("Key Passes",row.get("Key Passes"),row.get("Key Passes (Per90)"))+stat_row("Passes",row.get("Passes"),row.get("Passes (Per90)"))+stat_row("Successful Passes",row.get("Successful Passes"),row.get("Successful Passes (Per90)"))+stat_row("Pass Completion %",row.get("Pass Completion Rate"))+stat_row("Crosses",row.get("Crosses"),row.get("Crosses (Per90)"))+"</table>"
        st.markdown(h, unsafe_allow_html=True)
    with tab_drib:
        h=tbl_h+stat_row("Dribbles",row.get("Dribbles"),row.get("Dribbles (Per90)"))+stat_row("Successful Dribbles",row.get("Successful Dribbles"),row.get("Successful Dribbles (Per90)"))+stat_row("Dribble Success %",row.get("Dribble Success Rate"))+stat_row("Dispossessed",row.get("Dispossesed"),row.get("Dispossesed (Per90)"))+stat_row("Offsides",row.get("Offsides"),row.get("Offsides (Per90)"))+"</table>"
        st.markdown(h, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — SCOUTING REPORT
# ══════════════════════════════════════════════════════════════════════════
elif page == "🕵️  Scouting Report":
    st.markdown("""
    <div style='padding:2rem 0 1.2rem 0;border-bottom:1px solid #1e2a38;margin-bottom:2rem'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:3rem;letter-spacing:0.06em;line-height:1;color:#e8edf2'>
            SCOUTING <span style='color:#00e676'>REPORT</span>
        </div>
        <div style='font-size:0.9rem;color:#5a6a7a;margin-top:0.6rem'>
            Data-driven intelligence on the players shaping the 2025/26 season · 1,500+ min filter applied
        </div>
    </div>""", unsafe_allow_html=True)

    df_scout = df_base.copy()
    for col in ["Age","Minutes","Market Value","Goals Scored","Assists","Goals Scored (Per90)","Assists (Per90)"]:
        df_scout[col] = pd.to_numeric(df_scout[col], errors="coerce")

    top_performers = df_scout.nlargest(6, "Performance_Score")
    df_scout["G_A_per90"] = df_scout["Goals Scored (Per90)"].fillna(0) + df_scout["Assists (Per90)"].fillna(0)
    on_fire    = df_scout.nlargest(6, "G_A_per90")
    rising     = df_scout[df_scout["Age"] <= 21].nlargest(6, "Performance_Score")
    undervalued= df_scout[(df_scout["Value_Gap"] > 0) & (df_scout["Age"] <= 26)].nlargest(6, "Value_Gap")
    defenders  = df_scout[df_scout["Position"].isin(["Centre-Back","Full-Back","Defensive Midfield"])].nlargest(6, "Performance_Score")

    all_val = pd.concat(list(pos_dfs.values()), ignore_index=True)
    if sel_league != "All":
        lkey = "premier-league" if sel_league == "Premier League" else "la-liga"
        all_val = all_val[all_val["League"] == lkey]
    all_val["Age"] = pd.to_numeric(all_val["Age"], errors="coerce")
    all_val["Market Value"] = pd.to_numeric(all_val["Market Value"], errors="coerce")
    best_value = all_val[all_val["Age"] <= 25].nlargest(6, "Value_Score") if "Value_Score" in all_val.columns else pd.DataFrame()

    def render_section(title, emoji, subtitle, df_rows, badge_label, badge_color, stat_fn):
        st.markdown(f"""
        <div style='display:flex;align-items:baseline;gap:0.8rem;margin:2.2rem 0 0.3rem 0'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:1.7rem;letter-spacing:0.05em;color:#e8edf2'>{emoji} {title}</div>
            <div style='font-size:0.78rem;color:#5a6a7a'>{subtitle}</div>
        </div>
        <div style='height:2px;background:linear-gradient({badge_color},{badge_color}33,transparent);border-radius:1px;margin-bottom:1.2rem'></div>
        """, unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (_, row) in enumerate(df_rows.iterrows()):
            with cols[i % 3]:
                st.markdown(scout_player_card(row, badge_label, badge_color, stat_fn(row)), unsafe_allow_html=True)

    render_section("TOP PERFORMERS","🏆","Highest performance scores — the elite of two leagues",
        top_performers,"ELITE","#ffd740",
        lambda r: f"Perf. Score <strong style='color:#ffd740'>{r.get('Performance_Score',0):.1f}</strong> &nbsp;·&nbsp; {int(r.get('Minutes',0))} mins &nbsp;·&nbsp; Rank #{int(r.get('Overall_Rank',0)) if pd.notna(r.get('Overall_Rank')) else '—'}")

    render_section("ON FIRE","🔥","Best goals + assists per 90 minutes right now",
        on_fire,"HOT FORM","#ff5252",
        lambda r: f"G+A/90 <strong style='color:#ff5252'>{r.get('G_A_per90',0):.2f}</strong> &nbsp;·&nbsp; {int(r.get('Goals Scored',0) or 0)}G {int(r.get('Assists',0) or 0)}A &nbsp;·&nbsp; {int(r.get('Minutes',0))} mins")

    if not rising.empty:
        render_section("RISING STARS","⭐","U21 talent already making a serious impact",
            rising,"U21","#00b0ff",
            lambda r: f"Age <strong style='color:#00b0ff'>{int(r.get('Age',0))}</strong> &nbsp;·&nbsp; Score {r.get('Performance_Score',0):.1f} &nbsp;·&nbsp; {int(r.get('Minutes',0))} mins")

    if not undervalued.empty:
        render_section("UNDERVALUED GEMS","💎","Young players worth far more than their price tag",
            undervalued,"UNDERVALUED","#00e676",
            lambda r: f"Actual <strong style='color:#e8edf2'>{fmt_val(r.get('Market Value',np.nan))}</strong> &nbsp;·&nbsp; Predicted <strong style='color:#00e676'>{fmt_val(r.get('Predicted_Market_Value',np.nan))}</strong> &nbsp;·&nbsp; Gap +{fmt_val(r.get('Value_Gap',0))}")

    render_section("DEFENSIVE WALLS","🛡","Best defenders & defensive midfielders in both leagues",
        defenders,"DEFENDER","#bc8cff",
        lambda r: f"Tackles/90 <strong style='color:#bc8cff'>{r.get('Tackles (Per90)',0):.2f}</strong> &nbsp;·&nbsp; Interceptions/90 {r.get('Interceptions (Per90)',0):.2f} &nbsp;·&nbsp; Score {r.get('Performance_Score',0):.1f}")

    if not best_value.empty:
        render_section("BEST VALUE FOR MONEY","💰","U25 players delivering elite output at a bargain price",
            best_value,"VALUE PICK","#ff6d00",
            lambda r: f"Value Score <strong style='color:#ff6d00'>{r.get('Value_Score',0):.1f}</strong> &nbsp;·&nbsp; {fmt_val(r.get('Market Value',np.nan))} &nbsp;·&nbsp; Age {int(r.get('Age',0)) if pd.notna(r.get('Age')) else '—'}")

# ══════════════════════════════════════════════════════════════════════════
# PAGE 5 — MARKET VALUES
# ══════════════════════════════════════════════════════════════════════════
elif page == "💰  Market Values":
    section_header("Market Value Analysis", "Actual vs predicted — who's over or undervalued?")

    df_mv = df_full_base.dropna(subset=["Market Value","Predicted_Market_Value","Value_Gap"]).copy()

    most_under = df_mv.nlargest(1,"Value_Gap").iloc[0]
    most_over  = df_mv.nsmallest(1,"Value_Gap").iloc[0]
    avg_gap    = df_mv["Value_Gap"].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(card("Players With Predictions", f"{len(df_mv):,}"), unsafe_allow_html=True)
    c2.markdown(card("Most Undervalued", most_under["Name"].split()[-1], f"+{fmt_val(most_under['Value_Gap'])}", color="#00e676"), unsafe_allow_html=True)
    c3.markdown(card("Most Overvalued",  most_over["Name"].split()[-1],  f"{fmt_val(most_over['Value_Gap'])}",  color="#ff5252"), unsafe_allow_html=True)
    c4.markdown(card("Avg Prediction Gap", fmt_val(abs(avg_gap)), "Undervalued" if avg_gap>0 else "Overvalued", color="#ffd740"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Actual vs Predicted Market Value", "Points above the line = undervalued · Points below = overvalued")

    df_mv["Gap_Color"] = df_mv["Value_Gap"].apply(lambda x: "Undervalued" if x>0 else "Overvalued")
    fig_mv = px.scatter(df_mv, x="Market Value", y="Predicted_Market_Value",
                        color="Gap_Color", hover_name="Name",
                        hover_data={"Team":True,"Position":True,"Value_Gap":True},
                        color_discrete_map={"Undervalued":"#00e676","Overvalued":"#ff5252"}, opacity=0.75)
    max_v = df_mv[["Market Value","Predicted_Market_Value"]].max().max()
    fig_mv.add_trace(go.Scatter(x=[0,max_v], y=[0,max_v], mode="lines",
                                line=dict(color="#5a6a7a",dash="dot",width=1), name="Fair Value"))
    fig_mv.update_layout(**THEME, height=450)
    fig_mv.update_xaxes(title="Actual Market Value (€)")
    fig_mv.update_yaxes(title="Predicted Market Value (€)")
    st.plotly_chart(fig_mv, use_container_width=True)

    col_u, col_o = st.columns(2)
    with col_u:
        section_header("Most Undervalued", "Predicted value >> Actual value")
        under = df_mv.nlargest(15,"Value_Gap")[["Name","Team","Position","Market Value","Predicted_Market_Value","Value_Gap"]].copy()
        under["Market Value"]           = under["Market Value"].apply(fmt_val)
        under["Predicted_Market_Value"] = under["Predicted_Market_Value"].apply(fmt_val)
        under["Value_Gap"]              = under["Value_Gap"].apply(lambda x: f"+{fmt_val(x)}")
        under.columns = ["Player","Team","Position","Actual","Predicted","Gap"]
        st.dataframe(under, use_container_width=True, hide_index=True, height=420)

    with col_o:
        section_header("Most Overvalued", "Actual value >> Predicted value")
        over = df_mv.nsmallest(15,"Value_Gap")[["Name","Team","Position","Market Value","Predicted_Market_Value","Value_Gap"]].copy()
        over["Market Value"]           = over["Market Value"].apply(fmt_val)
        over["Predicted_Market_Value"] = over["Predicted_Market_Value"].apply(fmt_val)
        over["Value_Gap"]              = over["Value_Gap"].apply(lambda x: fmt_val(x))
        over.columns = ["Player","Team","Position","Actual","Predicted","Gap"]
        st.dataframe(over, use_container_width=True, hide_index=True, height=420)