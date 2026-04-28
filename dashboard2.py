import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pitch IQ",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:        #080c10;
    --surface:   #0f1419;
    --surface2:  #161d26;
    --border:    #1e2a38;
    --accent:    #00e676;
    --accent2:   #00b0ff;
    --gold:      #ffd740;
    --red:       #ff5252;
    --text:      #e8edf2;
    --muted:     #5a6a7a;
    --font-display: 'Bebas Neue', sans-serif;
    --font-body:    'DM Sans', sans-serif;
    --font-mono:    'DM Mono', monospace;
}

html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] .block-container { padding: 1rem !important; }
[data-testid="stSidebarNav"] { display: none; }

/* Inputs */
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
    font-family: var(--font-body) !important;
}
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(0,230,118,0.15) !important; }

/* Slider */
.stSlider [data-baseweb="slider"] { padding: 0 !important; }
.stSlider [data-testid="stTickBar"] { display: none; }

/* Metrics */
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
    font-family: var(--font-display) !important;
    font-size: 2rem !important;
    letter-spacing: 0.02em !important;
}
[data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: var(--muted) !important;
    font-family: var(--font-body) !important;
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

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-testid="stDataFrame"] th {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text) !important;
    font-size: 0.85rem !important;
}

/* Buttons */
.stButton button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.15s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

/* Labels */
label, .stSelectbox label, .stMultiSelect label, .stSlider label,
.stTextInput label, .stRadio label { 
    color: var(--muted) !important; 
    font-size: 0.72rem !important; 
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* Hide the collapse/expand button entirely — sidebar is always open */
[data-testid="collapsedControl"] { display: none !important; }
button[kind="header"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ───────────────────────────────────────────────────────────
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
    base = "data/clean"
    df_master    = pd.read_csv(f"{base}/master_player_ranking.csv")
    df_gk        = pd.read_csv(f"{base}/classified_goalkeepers.csv")
    df_pred      = pd.read_csv("data/processed/all_player_predictions.csv")

    pos_files = {
        "Centre-Back":        f"{base}/value_ranked_centre-backs.csv",
        "Full-Back":          f"{base}/value_ranked_full-backs.csv",
        "Defensive Midfield": f"{base}/value_ranked_defensive_midfields.csv",
        "Central Midfield":   f"{base}/value_ranked_central_midfields.csv",
        "Attacking Midfield": f"{base}/value_ranked_attacking_midfields.csv",
        "Winger":             f"{base}/value_ranked_wingers.csv",
        "Striker":            f"{base}/value_ranked_strikers.csv",
    }
    pos_dfs = {k: pd.read_csv(v) for k, v in pos_files.items()}

    # clean up
    for df in [df_master] + list(pos_dfs.values()):
        if "Unnamed: 0" in df.columns:
            df.drop(columns=["Unnamed: 0"], inplace=True)
    if "Unnamed: 0" in df_gk.columns:
        df_gk.drop(columns=["Unnamed: 0"], inplace=True)

    df_master["Market Value"] = pd.to_numeric(df_master["Market Value"], errors="coerce")
    df_master["Age"]          = pd.to_numeric(df_master["Age"],          errors="coerce")
    df_gk["Market Value"]     = pd.to_numeric(df_gk["Market Value"],     errors="coerce")
    df_gk["Age"]              = pd.to_numeric(df_gk["Age"],              errors="coerce")

    # merge predictions
    df_master = df_master.merge(df_pred[["Name","Predicted_Market_Value"]], on="Name", how="left")
    df_master["Value_Gap"] = df_master["Predicted_Market_Value"] - df_master["Market Value"]

    # gk role
    df_gk["GK_Role"] = df_gk.apply(
        lambda r: "Sweeper Keeper"
        if pd.notna(r.get("Sweeper Keeper_Score")) and pd.notna(r.get("Shot Stopper_Score"))
           and r["Sweeper Keeper_Score"] > r["Shot Stopper_Score"]
        else "Shot Stopper", axis=1
    )

    # league label
    df_master["League_Label"] = df_master["League"].map({"premier-league":"Premier League","la-liga":"La Liga"}).fillna(df_master["League"])
    df_gk["League_Label"]     = df_gk["League"].map({"premier-league":"Premier League","la-liga":"La Liga"}).fillna(df_gk["League"])

    return df_master, df_gk, df_pred, pos_dfs

df_master, df_gk, df_pred, pos_dfs = load_data()

# ── Helpers ────────────────────────────────────────────────────────────────
def fmt_val(v):
    if pd.isna(v): return "N/A"
    if v >= 1e9:   return f"€{v/1e9:.2f}B"
    if v >= 1e6:   return f"€{v/1e6:.1f}M"
    if v >= 1e3:   return f"€{v/1e3:.0f}K"
    return f"€{v:.0f}"

def card(label, value, sub=None, color="#00e676"):
    sub_html = f"<div style='font-size:0.72rem;color:#5a6a7a;margin-top:2px'>{sub}</div>" if sub else ""
    return f"""
    <div style='background:#0f1419;border:1px solid #1e2a38;border-radius:10px;padding:1.1rem 1.4rem;'>
        <div style='font-size:0.65rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#5a6a7a;margin-bottom:6px'>{label}</div>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.9rem;letter-spacing:0.02em;color:{color}'>{value}</div>
        {sub_html}
    </div>"""

def section_header(text, sub=None):
    sub_html = f"<div style='font-size:0.85rem;color:#5a6a7a;margin-top:4px;font-weight:400'>{sub}</div>" if sub else ""
    st.markdown(f"""
    <div style='margin:2rem 0 1.2rem 0;'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;letter-spacing:0.05em;color:#e8edf2'>{text}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)

# ── Sidebar nav ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.5rem 0.5rem 1rem 0.5rem;border-bottom:1px solid #1e2a38;margin-bottom:1rem'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;letter-spacing:0.08em;color:#00e676;line-height:1'>PITCH IQ</div>
        <div style='font-size:0.72rem;color:#5a6a7a;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px'>Football Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Overview", "🔍  Player Explorer", "👤  Player Profile", "🏆  Rankings & Scouting", "💰  Market Values"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1.5rem;padding-top:1rem;border-top:1px solid #1e2a38'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.65rem;color:#5a6a7a;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem'>GLOBAL FILTERS</div>", unsafe_allow_html=True)

    league_opts = ["All"] + sorted(df_master["League_Label"].dropna().unique().tolist())
    sel_league  = st.selectbox("League", league_opts)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Global filter ──────────────────────────────────────────────────────────
df_base = df_master.copy()
if sel_league != "All":
    df_base = df_base[df_base["League_Label"] == sel_league]

# ── Sidebar reopen hint (shown always, helps if collapsed) ─────────────────
st.markdown("""
<div style='position:fixed;bottom:1.2rem;right:1.2rem;z-index:9999;
            background:#0f1419;border:1px solid #1e2a38;border-radius:8px;
            padding:0.5rem 0.9rem;font-size:0.72rem;color:#5a6a7a;
            letter-spacing:0.06em;cursor:default;'>
    ← SIDEBAR HIDDEN? PRESS <kbd style='background:#1e2a38;border-radius:3px;padding:1px 5px;color:#e8edf2'>&gt;</kbd> ON LEFT EDGE
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
if page == "🏠  Overview":
    # Hero
    st.markdown("""
    <div style='padding:2.5rem 0 1.5rem 0;border-bottom:1px solid #1e2a38;margin-bottom:2rem'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:3.5rem;letter-spacing:0.06em;line-height:1;color:#e8edf2'>
            THE BEAUTIFUL <span style='color:#00e676'>GAME</span><br>BY THE NUMBERS
        </div>
        <div style='font-size:0.9rem;color:#5a6a7a;margin-top:0.8rem'>
            Premier League & La Liga · 2025/26 Season · {n} Players Analyzed
        </div>
    </div>
    """.format(n=len(df_master)), unsafe_allow_html=True)

    # KPI row
    top_perf  = df_base.nlargest(1, "Performance_Score").iloc[0]
    top_val   = df_base.nlargest(1, "Market Value").iloc[0]
    underval  = df_base[df_base["Value_Gap"].notna()].nlargest(1, "Value_Gap").iloc[0]
    avg_age   = df_base["Age"].mean()
    total_val = df_base["Market Value"].sum()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(card("Players Tracked",    f"{len(df_base):,}",              f"{df_base['League_Label'].nunique()} Leagues"), unsafe_allow_html=True)
    c2.markdown(card("Total Market Value", fmt_val(total_val),               "Combined squad value"), unsafe_allow_html=True)
    c3.markdown(card("Average Age",        f"{avg_age:.1f}",                 "Years old"), unsafe_allow_html=True)
    c4.markdown(card("Top Performer",      top_perf["Name"].split()[-1],     top_perf["Team"], color="#ffd740"), unsafe_allow_html=True)
    c5.markdown(card("Most Undervalued",   underval["Name"].split()[-1],     f"+{fmt_val(underval['Value_Gap'])} gap", color="#00b0ff"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # Top players table
    section_header("Top 10 Performers", "Ranked by performance score")
    top10 = df_base.nlargest(10, "Performance_Score")[
        ["Name","Team","League_Label","Position","Tactical_Role","Age","Market Value","Performance_Score","Overall_Rank"]
    ].copy()
    top10["Market Value"] = top10["Market Value"].apply(fmt_val)
    top10["Performance_Score"] = top10["Performance_Score"].round(1)
    top10.columns = ["Player","Team","League","Position","Role","Age","Market Value","Perf. Score","Rank"]
    st.dataframe(top10, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLAYER EXPLORER
# ══════════════════════════════════════════════════════════════════════════
elif page == "🔍  Player Explorer":
    section_header("Player Explorer", "Browse, filter and search the full player database")

    # Filters row
    f1,f2,f3,f4,f5 = st.columns([2,2,2,2,1])
    with f1:
        search = st.text_input("Search", placeholder="Player name or team...")
    with f2:
        pos_opts = ["All Positions"] + sorted(df_base["Position"].dropna().unique().tolist())
        sel_pos  = st.selectbox("Position", pos_opts)
    with f3:
        role_opts = ["All Roles"] + sorted(df_base["Tactical_Role"].dropna().unique().tolist())
        sel_role  = st.selectbox("Tactical Role", role_opts)
    with f4:
        min_age, max_age = int(df_base["Age"].min()), int(df_base["Age"].max())
        age_range = st.slider("Age Range", min_age, max_age, (min_age, max_age))
    with f5:
        sort_by = st.selectbox("Sort By", ["Performance Score","Market Value","Age","Name"])

    # Apply filters
    df_exp = df_base.copy()
    if search:
        mask = (df_exp["Name"].str.contains(search, case=False, na=False) |
                df_exp["Team"].str.contains(search, case=False, na=False))
        df_exp = df_exp[mask]
    if sel_pos  != "All Positions": df_exp = df_exp[df_exp["Position"]      == sel_pos]
    if sel_role != "All Roles":     df_exp = df_exp[df_exp["Tactical_Role"] == sel_role]
    df_exp = df_exp[df_exp["Age"].between(*age_range)]

    sort_col_map = {"Performance Score":"Performance_Score","Market Value":"Market Value","Age":"Age","Name":"Name"}
    df_exp = df_exp.sort_values(sort_col_map[sort_by], ascending=(sort_by=="Name"))

    # Count
    st.markdown(f"<div style='font-size:0.8rem;color:#5a6a7a;margin-bottom:0.8rem'>{len(df_exp)} players found</div>", unsafe_allow_html=True)

    # Display cols
    disp = df_exp[["Name","Team","League_Label","Position","Tactical_Role","Age","Market Value","Performance_Score","Overall_Rank"]].copy()
    disp["Market Value"]      = disp["Market Value"].apply(fmt_val)
    disp["Performance_Score"] = disp["Performance_Score"].round(1)
    disp.columns = ["Player","Team","League","Position","Role","Age","Market Value","Score","Rank"]
    st.dataframe(disp, use_container_width=True, hide_index=True, height=520)

    # Quick stats below
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Filtered Summary")
    s1,s2,s3,s4 = st.columns(4)
    s1.markdown(card("Players",          f"{len(df_exp):,}"), unsafe_allow_html=True)
    s2.markdown(card("Avg Market Value", fmt_val(df_exp["Market Value_raw"].mean() if "Market Value_raw" in df_exp else pd.to_numeric(df_exp["Market Value"].str.replace("€","").str.replace("M","e6").str.replace("K","e3"), errors="coerce").mean())), unsafe_allow_html=True)
    s3.markdown(card("Avg Age",          f"{df_exp['Age'].mean():.1f}"), unsafe_allow_html=True)
    s4.markdown(card("Avg Perf. Score",  f"{df_exp['Score'].mean():.1f}"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — PLAYER PROFILE
# ══════════════════════════════════════════════════════════════════════════
elif page == "👤  Player Profile":
    section_header("Player Profile", "Deep dive into any player's stats and tactical role")

    all_names = sorted(df_master["Name"].dropna().unique().tolist()) + sorted(df_gk["Name"].dropna().unique().tolist())
    sel_name  = st.selectbox("Select Player", all_names)

    # find player
    row = df_master[df_master["Name"] == sel_name]
    is_gk = False
    if row.empty:
        row = df_gk[df_gk["Name"] == sel_name]
        is_gk = True
    if row.empty:
        st.warning("Player not found.")
        st.stop()
    row = row.iloc[0]

    # Header card
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
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    if not is_gk:
        m1,m2,m3,m4,m5 = st.columns(5)
        m1.markdown(card("Performance Score", f"{row.get('Performance_Score',0):.1f}", "Out of 100", color="#00e676"), unsafe_allow_html=True)
        m2.markdown(card("Overall Rank",       f"#{int(row.get('Overall_Rank',0))}" if pd.notna(row.get('Overall_Rank')) else "N/A", "Across all positions"), unsafe_allow_html=True)
        m3.markdown(card("Goals (P90)",         f"{row.get('Goals Scored (Per90)',0):.2f}"), unsafe_allow_html=True)
        m4.markdown(card("Assists (P90)",        f"{row.get('Assists (Per90)',0):.2f}"),      unsafe_allow_html=True)
        m5.markdown(card("Pass %",               f"{row.get('Pass Completion Rate',0)*100:.0f}%" if pd.notna(row.get('Pass Completion Rate')) and row.get('Pass Completion Rate',0) <= 1 else f"{row.get('Pass Completion Rate',0):.0f}%"), unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        m1.markdown(card("Save %",      f"{row.get('Save Percentage',0)*100:.1f}%" if pd.notna(row.get('Save Percentage')) and row.get('Save Percentage',0) <= 1 else f"{row.get('Save Percentage',0):.1f}%"), unsafe_allow_html=True)
        m2.markdown(card("Saves (P90)", f"{row.get('Saves (Per90)',0):.2f}"), unsafe_allow_html=True)
        m3.markdown(card("Clean Sheets",f"{int(row.get('Clean Sheets',0))}" if pd.notna(row.get('Clean Sheets')) else "N/A"), unsafe_allow_html=True)
        m4.markdown(card("GK Role",     row.get("GK_Role",""), color="#00b0ff"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2])

    with col_l:
        section_header("Radar Profile", "Per-90 stats vs position peers")
        if not is_gk:
            radar_stats = [
                ("Goals (P90)",      row.get("Goals Scored (Per90)", 0)),
                ("Assists (P90)",    row.get("Assists (Per90)", 0)),
                ("Key Passes (P90)", row.get("Key Passes (Per90)", 0)),
                ("Tackles (P90)",    row.get("Tackles (Per90)", 0)),
                ("Interceptions",    row.get("Interceptions (Per90)", 0)),
                ("Dribbles (P90)",   row.get("Successful Dribbles (Per90)", 0)),
                ("Shots OT (P90)",   row.get("Shots On Target (Per90)", 0)),
                ("xG (P90)",         row.get("Expected Goals (xG) (Per90)", 0)),
            ]
            # normalize against position group
            pos_df = df_master[df_master["Position"] == row.get("Position","")]
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
            labels = [s[0] for s in radar_stats]
            vals   = []
            for label, _ in radar_stats:
                col_name = stat_cols_map[label]
                if col_name in pos_df.columns:
                    col_data = pd.to_numeric(pos_df[col_name], errors="coerce")
                    cmax = col_data.quantile(0.95)
                    cmin = col_data.min()
                    raw  = pd.to_numeric(row.get(col_name, 0), errors="coerce") or 0
                    v    = (raw - cmin) / (cmax - cmin) if cmax > cmin else 0
                    vals.append(max(0, min(1, v)))
                else:
                    vals.append(0)

            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            angles += angles[:1]
            vals_c  = vals + vals[:1]

            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=vals_c, theta=labels + [labels[0]],
                fill="toself", fillcolor="rgba(0,230,118,0.15)",
                line=dict(color="#00e676", width=2),
                marker=dict(size=6, color="#00e676"),
                name=row["Name"]
            ))
            fig_r.update_layout(
                **THEME, height=360,
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0,1], showticklabels=False, gridcolor="#1e2a38", linecolor="#1e2a38"),
                    angularaxis=dict(tickfont=dict(color="#e8edf2", size=11), gridcolor="#1e2a38", linecolor="#1e2a38"),
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            # GK radar
            gk_labels = ["Saves (P90)","Interceptions","Clearances","Pass Comp %","Clean Sheets"]
            gk_raw    = [
                row.get("Saves (Per90)", 0),
                row.get("Interceptions (Per90)", 0),
                row.get("Clearances (Per90)", 0),
                row.get("Pass Completion Rate", 0),
                row.get("Clean Sheets", 0),
            ]
            gk_cols_map = ["Saves (Per90)","Interceptions (Per90)","Clearances (Per90)","Pass Completion Rate","Clean Sheets"]
            gk_vals = []
            for i, col_name in enumerate(gk_cols_map):
                if col_name in df_gk.columns:
                    col_data = pd.to_numeric(df_gk[col_name], errors="coerce")
                    cmax = col_data.quantile(0.95); cmin = col_data.min()
                    raw  = pd.to_numeric(gk_raw[i], errors="coerce") or 0
                    gk_vals.append(max(0, min(1, (raw - cmin)/(cmax - cmin) if cmax > cmin else 0)))
                else:
                    gk_vals.append(0)
            gk_vals_c = gk_vals + gk_vals[:1]
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=gk_vals_c, theta=gk_labels+[gk_labels[0]],
                fill="toself", fillcolor="rgba(0,176,255,0.15)",
                line=dict(color="#00b0ff", width=2),
                marker=dict(size=6, color="#00b0ff"),
            ))
            fig_r.update_layout(**THEME, height=360,
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True,range=[0,1],showticklabels=False,gridcolor="#1e2a38",linecolor="#1e2a38"),
                    angularaxis=dict(tickfont=dict(color="#e8edf2",size=11),gridcolor="#1e2a38",linecolor="#1e2a38")),
                showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)

    with col_r:
        section_header("Role Scores", "Fit for each tactical role")
        if not is_gk:
            score_cols = [c for c in df_master.columns if c.endswith("_Score") and pd.notna(row.get(c))]
            if score_cols:
                scores = {c.replace("_Score","").replace("_"," "): round(row[c], 1) for c in score_cols if pd.notna(row.get(c))}
                scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
                role_df = pd.DataFrame({"Role": list(scores.keys()), "Score": list(scores.values())})
                fig_s = px.bar(role_df, x="Score", y="Role", orientation="h",
                               color="Score", color_continuous_scale=["#1e2a38","#ffd740"],
                               range_x=[0,100])
                fig_s.update_layout(**THEME, height=360, coloraxis_showscale=False)
                fig_s.update_traces(marker_line_width=0)
                fig_s.update_yaxes(title="", categoryorder="total ascending")
                st.plotly_chart(fig_s, use_container_width=True)
        else:
            gk_scores = {}
            for c in ["Shot Stopper_Score","Sweeper Keeper_Score"]:
                if c in row.index and pd.notna(row[c]):
                    gk_scores[c.replace("_Score","").replace("_"," ")] = round(row[c], 1)
            if gk_scores:
                gk_df = pd.DataFrame({"Role":list(gk_scores.keys()),"Score":list(gk_scores.values())})
                fig_s = px.bar(gk_df, x="Score", y="Role", orientation="h",
                               color="Score", color_continuous_scale=["#1e2a38","#00b0ff"], range_x=[0,100])
                fig_s.update_layout(**THEME, height=180, coloraxis_showscale=False)
                fig_s.update_traces(marker_line_width=0)
                st.plotly_chart(fig_s, use_container_width=True)

        # Market value vs prediction
        if not is_gk and pd.notna(row.get("Predicted_Market_Value")):
            section_header("Market Value", "Actual vs predicted")
            actual    = row["Market Value"]
            predicted = row["Predicted_Market_Value"]
            gap       = predicted - actual
            color     = "#00e676" if gap > 0 else "#ff5252"
            label     = "Undervalued" if gap > 0 else "Overvalued"
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
            </div>
            """, unsafe_allow_html=True)

    # Stats table
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Full Stats Breakdown")
    tab_g, tab_att, tab_def, tab_pass, tab_drib = st.tabs(["📋 General","⚽ Attacking","🛡 Defending","📤 Passing","🏃 Dribbling"])

    def stat_row(label, val, per90=None):
        v = f"{val:.2f}" if isinstance(val,(float,np.floating)) and pd.notna(val) else (str(int(val)) if pd.notna(val) else "—")
        p = f"{per90:.2f}" if per90 is not None and pd.notna(per90) else "—"
        return f"<tr><td style='padding:6px 12px;color:#5a6a7a;font-size:0.83rem'>{label}</td><td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right'>{v}</td><td style='padding:6px 12px;font-family:DM Mono,monospace;font-size:0.83rem;text-align:right;color:#5a6a7a'>{p}</td></tr>"

    tbl_header = "<table style='width:100%;border-collapse:collapse'><tr style='border-bottom:1px solid #1e2a38'><th style='padding:6px 12px;text-align:left;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>STAT</th><th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>TOTAL</th><th style='padding:6px 12px;text-align:right;font-size:0.65rem;color:#5a6a7a;letter-spacing:0.08em;text-transform:uppercase'>PER 90</th></tr>"

    with tab_g:
        html = tbl_header
        html += stat_row("Matches Played",  row.get("Matches Played"))
        html += stat_row("Minutes",         row.get("Minutes"))
        html += stat_row("Matches Started", row.get("Matches Started"))
        html += stat_row("Yellow Cards",    row.get("Yellow Cards"))
        html += stat_row("Red Cards",       row.get("Red Cards"))
        html += stat_row("Fouls Committed", row.get("Fouls Committed"), row.get("Fouls Committed (Per90)"))
        html += stat_row("Fouled Against",  row.get("Fouled Against"),  row.get("Fouled Against (Per90)"))
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)

    with tab_att:
        html = tbl_header
        html += stat_row("Goals Scored",      row.get("Goals Scored"),      row.get("Goals Scored (Per90)"))
        html += stat_row("xG",                row.get("Expected Goals (xG)"), row.get("Expected Goals (xG) (Per90)"))
        html += stat_row("Shots Taken",       row.get("Shots Taken"),       row.get("Shots Taken (Per90)"))
        html += stat_row("Shots On Target",   row.get("Shots On Target"),   row.get("Shots On Target (Per90)"))
        html += stat_row("Shot Accuracy",     row.get("Shot Accuracy"))
        html += stat_row("Goal Involvement",  row.get("Goal Involvement"),  row.get("Goal Involvement (Per90)"))
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)

    with tab_def:
        html = tbl_header
        html += stat_row("Tackles",           row.get("Tackles"),          row.get("Tackles (Per90)"))
        html += stat_row("Interceptions",     row.get("Interceptions"),    row.get("Interceptions (Per90)"))
        html += stat_row("Clearances",        row.get("Clearances"),       row.get("Clearances (Per90)"))
        html += stat_row("Shots Blocked",     row.get("Shots Blocked"),    row.get("Shots Blocked (Per90)"))
        html += stat_row("Aerial Duels Won",  row.get("Aerial Duels Won"), row.get("Aerial Duels Won (Per90)"))
        html += stat_row("Ground Duels Won",  row.get("Ground Duels Won"), row.get("Ground Duels Won (Per90)"))
        html += stat_row("Dribbled Past",     row.get("Dribbled Past"),    row.get("Dribbled Past (Per90)"))
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)

    with tab_pass:
        html = tbl_header
        html += stat_row("Assists",           row.get("Assists"),           row.get("Assists (Per90)"))
        html += stat_row("xA",                row.get("Expected Assists (xA)"), row.get("Expected Assists (xA) (Per90)"))
        html += stat_row("Key Passes",        row.get("Key Passes"),        row.get("Key Passes (Per90)"))
        html += stat_row("Passes",            row.get("Passes"),            row.get("Passes (Per90)"))
        html += stat_row("Successful Passes", row.get("Successful Passes"), row.get("Successful Passes (Per90)"))
        html += stat_row("Pass Completion %", row.get("Pass Completion Rate"))
        html += stat_row("Crosses",           row.get("Crosses"),           row.get("Crosses (Per90)"))
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)

    with tab_drib:
        html = tbl_header
        html += stat_row("Dribbles",           row.get("Dribbles"),            row.get("Dribbles (Per90)"))
        html += stat_row("Successful Dribbles", row.get("Successful Dribbles"), row.get("Successful Dribbles (Per90)"))
        html += stat_row("Dribble Success %",  row.get("Dribble Success Rate"))
        html += stat_row("Dispossessed",       row.get("Dispossesed"),         row.get("Dispossesed (Per90)"))
        html += stat_row("Offsides",           row.get("Offsides"),            row.get("Offsides (Per90)"))
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — RANKINGS & SCOUTING
# ══════════════════════════════════════════════════════════════════════════
elif page == "🏆  Rankings & Scouting":
    section_header("Rankings & Scouting", "Best performers and best value players by position")

    tab_perf, tab_val, tab_gk = st.tabs(["🏆 Performance Rankings","💎 Best Value","🥅 Goalkeepers"])

    with tab_perf:
        f1,f2,f3 = st.columns([2,2,2])
        with f1:
            pos_opts = ["All Positions"] + sorted(df_base["Position"].dropna().unique().tolist())
            r_pos    = st.selectbox("Position", pos_opts, key="rank_pos")
        with f2:
            r_league = st.selectbox("League", ["All"]+sorted(df_base["League_Label"].dropna().unique().tolist()), key="rank_league")
        with f3:
            r_age = st.slider("Max Age", 16, 40, 40, key="rank_age")

        df_rank = df_base.copy()
        if r_pos    != "All Positions": df_rank = df_rank[df_rank["Position"]      == r_pos]
        if r_league != "All":           df_rank = df_rank[df_rank["League_Label"]  == r_league]
        df_rank = df_rank[df_rank["Age"] <= r_age]
        df_rank = df_rank.nlargest(50, "Performance_Score")

        # Bar chart top 15
        top15 = df_rank.head(15).copy()
        fig = px.bar(top15, x="Performance_Score", y="Name", orientation="h",
                     color="Position",
                     hover_data={"Team":True,"Tactical_Role":True,"Market Value":True},
                     color_discrete_sequence=["#00e676","#00b0ff","#ffd740","#ff5252","#bc8cff","#ff6d00","#69f0ae"])
        fig.update_layout(**THEME, height=420, showlegend=True)
        fig.update_traces(marker_line_width=0)
        fig.update_yaxes(title="", categoryorder="total ascending")
        fig.update_xaxes(title="Performance Score")
        st.plotly_chart(fig, use_container_width=True)

        disp = df_rank[["Name","Team","League_Label","Position","Tactical_Role","Age","Market Value","Performance_Score","Overall_Rank"]].copy()
        disp["Market Value"]      = disp["Market Value"].apply(fmt_val)
        disp["Performance_Score"] = disp["Performance_Score"].round(1)
        disp.columns = ["Player","Team","League","Position","Role","Age","Market Value","Score","Rank"]
        st.dataframe(disp, use_container_width=True, hide_index=True, height=420)

    with tab_val:
        st.markdown("<div style='font-size:0.85rem;color:#5a6a7a;margin-bottom:1rem'>Best value players — high performance relative to market value and age. Perfect for scouting undervalued talent.</div>", unsafe_allow_html=True)

        v1,v2 = st.columns([2,2])
        with v1:
            v_pos = st.selectbox("Position", ["All Positions"]+sorted(df_base["Position"].dropna().unique().tolist()), key="val_pos")
        with v2:
            v_age = st.slider("Max Age", 16, 40, 26, key="val_age")

        # build value ranking from pos_dfs
        if v_pos == "All Positions":
            val_dfs = []
            for pos, vdf in pos_dfs.items():
                if sel_league != "All":
                    lkey = "premier-league" if sel_league == "Premier League" else "la-liga"
                    vdf = vdf[vdf["League"] == lkey]
                val_dfs.append(vdf)
            df_val = pd.concat(val_dfs, ignore_index=True)
        else:
            df_val = pos_dfs.get(v_pos, pd.DataFrame()).copy()
            if sel_league != "All":
                lkey = "premier-league" if sel_league == "Premier League" else "la-liga"
                df_val = df_val[df_val["League"] == lkey]

        if "Age" in df_val.columns:
            df_val["Age"] = pd.to_numeric(df_val["Age"], errors="coerce")
            df_val = df_val[df_val["Age"] <= v_age]

        if "Value_Score" in df_val.columns:
            df_val = df_val.sort_values("Value_Score", ascending=False)
            top_val_15 = df_val.head(15)

            fig_v = px.scatter(df_val.head(80).dropna(subset=["Market Value","Performance_Score"]),
                               x="Market Value", y="Performance_Score",
                               hover_name="Name",
                               color="Position" if "Position" in df_val.columns else None,
                               size="Value_Score" if "Value_Score" in df_val.columns else None,
                               size_max=24,
                               color_discrete_sequence=["#00e676","#00b0ff","#ffd740","#ff5252","#bc8cff","#ff6d00","#69f0ae"])
            fig_v.update_layout(**THEME, height=360)
            fig_v.update_traces(marker_line_width=0, marker_opacity=0.8)
            fig_v.update_xaxes(title="Market Value (€)")
            fig_v.update_yaxes(title="Performance Score")
            st.plotly_chart(fig_v, use_container_width=True)

            show_cols = [c for c in ["Name","Team","Position","Tactical_Role","Age","Market Value","Performance_Score","Value_Score","Value_Rank"] if c in df_val.columns]
            disp_v = df_val[show_cols].head(50).copy()
            if "Market Value" in disp_v.columns:
                disp_v["Market Value"] = disp_v["Market Value"].apply(fmt_val)
            if "Performance_Score" in disp_v.columns:
                disp_v["Performance_Score"] = disp_v["Performance_Score"].round(1)
            if "Value_Score" in disp_v.columns:
                disp_v["Value_Score"] = disp_v["Value_Score"].round(1)
            st.dataframe(disp_v, use_container_width=True, hide_index=True, height=380)
        else:
            st.info("Value rankings not available for this selection.")

    with tab_gk:
        df_gk_disp = df_gk.copy()
        if sel_league != "All":
            lkey = "premier-league" if sel_league == "Premier League" else "la-liga"
            df_gk_disp = df_gk_disp[df_gk_disp["League"] == lkey]

        g1,g2 = st.columns(2)
        with g1:
            # GK role pie
            role_counts = df_gk_disp["GK_Role"].value_counts().reset_index()
            role_counts.columns = ["Role","Count"]
            fig_gp = px.pie(role_counts, values="Count", names="Role",
                            color_discrete_sequence=["#00e676","#00b0ff"], hole=0.55)
            fig_gp.update_layout(**THEME, height=280, title="GK Role Distribution")
            st.plotly_chart(fig_gp, use_container_width=True)
        with g2:
            # GK score comparison
            if "Shot Stopper_Score" in df_gk_disp.columns and "Sweeper Keeper_Score" in df_gk_disp.columns:
                top_gks = df_gk_disp.nlargest(10,"Shot Stopper_Score")[["Name","Shot Stopper_Score","Sweeper Keeper_Score"]].melt("Name")
                fig_gb = px.bar(top_gks, x="value", y="Name", color="variable", orientation="h",
                                barmode="group", color_discrete_sequence=["#00e676","#00b0ff"])
                fig_gb.update_layout(**THEME, height=280, title="Top GKs — Role Scores")
                fig_gb.update_traces(marker_line_width=0)
                fig_gb.update_yaxes(title="")
                st.plotly_chart(fig_gb, use_container_width=True)

        gk_cols = [c for c in ["Name","Team","League_Label","Age","Market Value","GK_Role","Shot Stopper_Score","Sweeper Keeper_Score","Save Percentage","Clean Sheets"] if c in df_gk_disp.columns]
        gk_show = df_gk_disp[gk_cols].copy()
        if "Market Value" in gk_show.columns:
            gk_show["Market Value"] = gk_show["Market Value"].apply(fmt_val)
        if "Save Percentage" in gk_show.columns:
            gk_show["Save Percentage"] = gk_show["Save Percentage"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) and x<=1 else (f"{x:.1f}%" if pd.notna(x) else "—"))
        if "Shot Stopper_Score" in gk_show.columns:
            gk_show["Shot Stopper_Score"] = gk_show["Shot Stopper_Score"].round(1)
        if "Sweeper Keeper_Score" in gk_show.columns:
            gk_show["Sweeper Keeper_Score"] = gk_show["Sweeper Keeper_Score"].round(1)
        st.dataframe(gk_show, use_container_width=True, hide_index=True, height=380)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 5 — MARKET VALUES
# ══════════════════════════════════════════════════════════════════════════
elif page == "💰  Market Values":
    section_header("Market Value Analysis", "Actual vs predicted — who's over or undervalued?")

    df_mv = df_base.dropna(subset=["Market Value","Predicted_Market_Value","Value_Gap"]).copy()

    # Top summary cards
    most_under = df_mv.nlargest(1,"Value_Gap").iloc[0]
    most_over  = df_mv.nsmallest(1,"Value_Gap").iloc[0]
    avg_gap    = df_mv["Value_Gap"].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(card("Players With Predictions", f"{len(df_mv):,}"),                                                                                          unsafe_allow_html=True)
    c2.markdown(card("Most Undervalued",          most_under["Name"].split()[-1], f"+{fmt_val(most_under['Value_Gap'])}", color="#00e676"),                   unsafe_allow_html=True)
    c3.markdown(card("Most Overvalued",           most_over["Name"].split()[-1],  f"{fmt_val(most_over['Value_Gap'])}",   color="#ff5252"),                   unsafe_allow_html=True)
    c4.markdown(card("Avg Prediction Gap",        fmt_val(abs(avg_gap)),          "Undervalued" if avg_gap > 0 else "Overvalued",                            color="#ffd740"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # Main scatter
    section_header("Actual vs Predicted Market Value", "Points above the line = undervalued · Points below = overvalued")

    df_mv["Gap_Color"] = df_mv["Value_Gap"].apply(lambda x: "Undervalued" if x > 0 else "Overvalued")
    fig_mv = px.scatter(df_mv, x="Market Value", y="Predicted_Market_Value",
                        color="Gap_Color",
                        hover_name="Name",
                        hover_data={"Team":True,"Position":True,"Value_Gap":True},
                        color_discrete_map={"Undervalued":"#00e676","Overvalued":"#ff5252"},
                        opacity=0.75,
                        size_max=12)

    # perfect prediction line
    max_v = df_mv[["Market Value","Predicted_Market_Value"]].max().max()
    fig_mv.add_trace(go.Scatter(x=[0,max_v], y=[0,max_v],
                                mode="lines", line=dict(color="#5a6a7a",dash="dot",width=1),
                                name="Fair Value", showlegend=True))
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
        st.dataframe(under, use_container_width=True, hide_index=True, height=380)

    with col_o:
        section_header("Most Overvalued", "Actual value >> Predicted value")
        over = df_mv.nsmallest(15,"Value_Gap")[["Name","Team","Position","Market Value","Predicted_Market_Value","Value_Gap"]].copy()
        over["Market Value"]           = over["Market Value"].apply(fmt_val)
        over["Predicted_Market_Value"] = over["Predicted_Market_Value"].apply(fmt_val)
        over["Value_Gap"]              = over["Value_Gap"].apply(lambda x: fmt_val(x))
        over.columns = ["Player","Team","Position","Actual","Predicted","Gap"]
        st.dataframe(over, use_container_width=True, hide_index=True, height=380)

    # Value gap by position
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Average Value Gap by Position")
    pos_gap = df_mv.groupby("Position")["Value_Gap"].mean().reset_index().sort_values("Value_Gap", ascending=True)
    pos_gap["Color"] = pos_gap["Value_Gap"].apply(lambda x: "#00e676" if x>0 else "#ff5252")
    fig_pg = px.bar(pos_gap, x="Value_Gap", y="Position", orientation="h",
                    color="Color", color_discrete_map="identity")
    fig_pg.update_layout(**THEME, height=320, showlegend=False)
    fig_pg.update_traces(marker_line_width=0)
    fig_pg.update_xaxes(title="Average Gap (€)")
    fig_pg.update_yaxes(title="")
    st.plotly_chart(fig_pg, use_container_width=True)