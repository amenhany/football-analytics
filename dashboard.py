"""
Football Analytics Dashboard — Streamlit GUI
============================================
Interactive dashboard for football player analysis with real data

Run with:
    pip install streamlit plotly pandas
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS  (dark, refined, editorial look)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* App background */
.stApp {
    background: #0d0f14;
    color: #e8e6e1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #12151c !important;
    border-right: 1px solid #1e2330;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] p {
    color: #8892a4 !important;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: #161a24;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]:hover {
    border-color: #4f6ef7;
}
div[data-testid="metric-container"] label {
    color: #6b7a99 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #e8e6e1 !important;
    font-family: 'DM Serif Display', serif;
    font-size: 2rem !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}

/* Section headers */
h1 { font-family: 'DM Serif Display', serif; color: #e8e6e1 !important; font-size: 2.2rem !important; }
h2 { font-family: 'DM Serif Display', serif; color: #c5c0b8 !important; font-size: 1.4rem !important; letter-spacing: -0.01em; }
h3 { font-family: 'DM Sans', sans-serif; color: #8892a4 !important; font-size: 0.8rem !important;
     letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #1e2330;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    color: #6b7a99;
    background: transparent;
    border: none;
    padding: 0.6rem 1.4rem;
    font-size: 0.82rem;
    letter-spacing: 0.06em;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #4f6ef7 !important;
    border-bottom: 2px solid #4f6ef7 !important;
    background: transparent !important;
}

/* DataFrames */
.dataframe { font-family: 'DM Mono', monospace; font-size: 0.8rem; }
[data-testid="stDataFrame"] { border: 1px solid #1e2330; border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: #1e2330 !important; }

/* Plotly chart backgrounds */
.js-plotly-plot { border-radius: 12px; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2330; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor="#161a24",
    plot_bgcolor="#161a24",
    font=dict(family="DM Sans", color="#8892a4", size=12),
    title_font=dict(family="DM Serif Display", color="#c5c0b8", size=16),
    colorway=["#4f6ef7", "#38c9b0", "#f76b4f", "#f7c44f", "#b04ff7", "#4ff7a0"],
    xaxis=dict(gridcolor="#1e2330", linecolor="#1e2330", zeroline=False),
    yaxis=dict(gridcolor="#1e2330", linecolor="#1e2330", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4")),
    margin=dict(t=50, l=10, r=10, b=10),
)

# ─────────────────────────────────────────────
# LOAD ACTUAL FOOTBALL DATA
# ─────────────────────────────────────────────

@st.cache_data
def load_data():
    """Load all football analytics data"""
    base_path = "data/clean"
    
    # Main player rankings
    df_master = pd.read_csv(f"{base_path}/master_player_ranking.csv")
    
    # Goalkeeper data with classification
    df_goalkeepers = pd.read_csv(f"{base_path}/classified_goalkeepers.csv")
    
    # Position-specific data
    df_strikers = pd.read_csv(f"{base_path}/position_strikers_clean.csv")
    df_midfielders = pd.read_csv(f"{base_path}/position_central_midfielders_clean.csv")
    df_defenders = pd.read_csv(f"{base_path}/position_centre_backs_clean.csv")
    
    # Value rankings
    df_value_strikers = pd.read_csv(f"{base_path}/value_ranked_strikers.csv")
    
    return {
        'master': df_master,
        'goalkeepers': df_goalkeepers,
        'strikers': df_strikers,
        'midfielders': df_midfielders,
        'defenders': df_defenders,
        'value_strikers': df_value_strikers
    }

# Load data
data = load_data()

# Extract main datasets
df_master = data['master']
df_goalkeepers = data['goalkeepers']
df_strikers = data['strikers']
df_midfielders = data['midfielders']
df_defenders = data['defenders']
df_value_strikers = data['value_strikers']

# ─────────────────────────────────────────────
# DATA PROCESSING
# ─────────────────────────────────────────────

# Clean and prepare master data
df_master = df_master.dropna(subset=['Name', 'Position'])
df_master['Market Value'] = pd.to_numeric(df_master['Market Value'], errors='coerce')
df_master['Age'] = pd.to_numeric(df_master['Age'], errors='coerce')

# Create goalkeeper classification (2 categories as requested)
def classify_goalkeeper_simple(row):
    """Classify goalkeeper as Shot Stopper or Sweeper Keeper"""
    if pd.isna(row['Shot Stopper_Score']) or pd.isna(row['Sweeper Keeper_Score']):
        return 'Insufficient Data'
    
    if row['Sweeper Keeper_Score'] > row['Shot Stopper_Score']:
        return 'Sweeper Keeper'
    else:
        return 'Shot Stopper'

df_goalkeepers['GK_Role'] = df_goalkeepers.apply(classify_goalkeeper_simple, axis=1)

# Create performance categories for outfield players
def create_performance_category(row):
    """Create performance categories based on scores"""
    if pd.notna(row.get('Performance_Score')):
        score = row['Performance_Score']
        if score >= 65:
            return 'Elite'
        elif score >= 55:
            return 'Excellent'
        elif score >= 45:
            return 'Good'
        elif score >= 35:
            return 'Average'
        else:
            return 'Below Average'
    return 'Unknown'

df_master['Performance_Category'] = df_master.apply(create_performance_category, axis=1)

# ─────────────────────────────────────────────
# STATISTICAL SUMMARY
# ─────────────────────────────────────────────
stat_summary = {
    "Total Players": len(df_master),
    "Avg Market Value": df_master['Market Value'].mean(),
    "Total Market Value": df_master['Market Value'].sum(),
    "Avg Age": df_master['Age'].mean(),
    "Goalkeepers": len(df_goalkeepers),
    "Elite Players": len(df_master[df_master['Performance_Category'] == 'Elite']),
}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Football Analytics")
    st.markdown("---")

    st.markdown("**Position Filter**")
    positions = ['All'] + sorted(df_master['Position'].dropna().unique().tolist())
    selected_position = st.selectbox(
        "Select Position",
        options=positions,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("**League Filter**")
    leagues = ['All'] + sorted(df_master['League'].dropna().unique().tolist())
    selected_league = st.selectbox(
        "Select League",
        options=leagues,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("**Performance Category**")
    performance_cats = ['All'] + sorted(df_master['Performance_Category'].dropna().unique().tolist())
    selected_performance = st.selectbox(
        "Performance Level",
        options=performance_cats,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("**Age Range**")
    min_age = int(df_master['Age'].min())
    max_age = int(df_master['Age'].max())
    age_range = st.slider("", min_age, max_age, (min_age, max_age), step=1, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Goalkeeper Analysis**")
    show_gk_analysis = st.checkbox("Show Goalkeeper Dashboard", value=False)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
df_filtered = df_master.copy()

if selected_position != 'All':
    df_filtered = df_filtered[df_filtered['Position'] == selected_position]

if selected_league != 'All':
    df_filtered = df_filtered[df_filtered['League'] == selected_league]

if selected_performance != 'All':
    df_filtered = df_filtered[df_filtered['Performance_Category'] == selected_performance]

df_filtered = df_filtered[df_filtered['Age'].between(*age_range)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Football Analytics Dashboard")
st.markdown("### Player Performance · Market Values · Tactical Analysis")
st.markdown("---")

# ─────────────────────────────────────────────
# KPI METRICS ROW
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Players", f"{stat_summary['Total Players']:,}")
c2.metric("Avg Market Value", f"€{stat_summary['Avg Market Value']/1e6:.1f}M")
c3.metric("Total Market Value", f"€{stat_summary['Total Market Value']/1e9:.1f}B")
c4.metric("Avg Age", f"{stat_summary['Avg Age']:.1f}")
c5.metric("Elite Players", f"{stat_summary['Elite Players']}")

st.markdown("")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
if show_gk_analysis:
    tab1, tab2, tab3, tab4 = st.tabs(["🥅 Goalkeepers", "📊 Player Analysis", "📋 Data Table", "📐 Statistics"])
else:
    tab1, tab2, tab3 = st.tabs(["📊 Player Analysis", "📋 Data Table", "📐 Statistics"])

# ── GOALKEEPER TAB ───────────────────────────
if show_gk_analysis:
    with tab1:
        st.markdown("## Goalkeeper Role Analysis")
        
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            # GK Role distribution
            gk_role_dist = df_goalkeepers['GK_Role'].value_counts()
            fig_gk_pie = px.pie(
                values=gk_role_dist.values,
                names=gk_role_dist.index,
                title="Goalkeeper Role Distribution",
                color_discrete_sequence=["#4f6ef7", "#38c9b0", "#f76b4f"],
                hole=0.4,
            )
            fig_gk_pie.update_layout(**CHART_THEME, height=350)
            fig_gk_pie.update_traces(textfont_color="#e8e6e1")
            st.plotly_chart(fig_gk_pie, use_container_width=True)
        
        with col_r:
            # GK Performance comparison
            gk_performance = df_goalkeepers.groupby('GK_Role')[['Shot Stopper_Score', 'Sweeper Keeper_Score']].mean().reset_index()
            
            fig_gk_bar = go.Figure()
            fig_gk_bar.add_trace(go.Bar(
                name='Shot Stopper Score',
                x=gk_performance['GK_Role'],
                y=gk_performance['Shot Stopper_Score'],
                marker_color="#4f6ef7"
            ))
            fig_gk_bar.add_trace(go.Bar(
                name='Sweeper Keeper Score',
                x=gk_performance['GK_Role'],
                y=gk_performance['Sweeper Keeper_Score'],
                marker_color="#38c9b0"
            ))
            fig_gk_bar.update_layout(
                **CHART_THEME,
                height=350,
                title="Average Scores by Role",
                barmode='group'
            )
            st.plotly_chart(fig_gk_bar, use_container_width=True)
        
        st.markdown("")
        
        # Detailed GK table
        st.markdown("## Goalkeeper Rankings")
        gk_display = df_goalkeepers[['Name', 'Team', 'Age', 'Market Value', 'GK_Role', 
                                   'Shot Stopper_Score', 'Sweeper Keeper_Score', 'Save Percentage']].copy()
        gk_display = gk_display.sort_values(['Shot Stopper_Score', 'Sweeper Keeper_Score'], ascending=False)
        gk_display.columns = ['Name', 'Team', 'Age', 'Market Value', 'Role', 'Shot Stopper', 'Sweeper Keeper', 'Save %']
        
        st.dataframe(
            gk_display.style.format({
                'Market Value': lambda x: f"€{x/1e6:.1f}M" if pd.notna(x) else 'N/A',
                'Shot Stopper': '{:.1f}',
                'Sweeper Keeper': '{:.1f}',
                'Save %': '{:.1%}'
            }).set_properties(**{
                "background-color": "#161a24",
                "color": "#c5c0b8",
                "font-family": "DM Mono, monospace",
                "font-size": "12px",
            }).set_table_styles([{
                "selector": "th",
                "props": [
                    ("background-color", "#0d0f14"),
                    ("color", "#6b7a99"),
                    ("font-size", "11px"),
                    ("letter-spacing", "0.08em"),
                    ("text-transform", "uppercase"),
                ],
            }]),
            use_container_width=True,
            height=400
        )

# ── TAB 1 — CHARTS ───────────────────────────
if show_gk_analysis:
    charts_tab = tab2
else:
    charts_tab = tab1

with charts_tab:
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.markdown("## Market Value Distribution")
        fig_value = px.histogram(
            df_filtered.dropna(subset=['Market Value']), 
            x='Market Value', 
            nbins=30,
            color='Position',
            title="Player Market Values",
            color_discrete_sequence=["#4f6ef7", "#38c9b0", "#f76b4f", "#f7c44f", "#b04ff7"]
        )
        fig_value.update_layout(**CHART_THEME, height=320)
        fig_value.update_xaxes(title_text="Market Value (€)")
        st.plotly_chart(fig_value, use_container_width=True)

    with col_r:
        st.markdown("## Position Distribution")
        pos_dist = df_filtered['Position'].value_counts()
        fig_pos_pie = px.pie(
            names=pos_dist.index,
            values=pos_dist.values,
            title="Players by Position",
            color_discrete_sequence=["#4f6ef7","#38c9b0","#f76b4f","#f7c44f","#b04ff7"],
            hole=0.55,
        )
        fig_pos_pie.update_layout(**CHART_THEME, height=320, showlegend=True)
        fig_pos_pie.update_traces(textfont_color="#e8e6e1")
        st.plotly_chart(fig_pos_pie, use_container_width=True)

    st.markdown("")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("## Performance Score Distribution")
        if 'Performance_Score' in df_filtered.columns:
            fig_perf = px.histogram(
                df_filtered.dropna(subset=['Performance_Score']), 
                x='Performance_Score', 
                nbins=25,
                color_discrete_sequence=["#4f6ef7"],
                title="Performance Scores"
            )
            fig_perf.update_layout(**CHART_THEME, height=260, bargap=0.05)
            fig_perf.update_xaxes(title_text="Performance Score")
            st.plotly_chart(fig_perf, use_container_width=True)

    with col_b:
        st.markdown("## Age vs Market Value")
        fig_age_value = px.scatter(
            df_filtered.dropna(subset=['Market Value', 'Age']), 
            x='Age', 
            y='Market Value',
            color='Position',
            size='Market Value',
            color_discrete_sequence=["#4f6ef7","#38c9b0","#f76b4f","#f7c44f","#b04ff7"],
            opacity=0.75,
            title="Age vs Market Value"
        )
        fig_age_value.update_layout(**CHART_THEME, height=260)
        fig_age_value.update_yaxes(title_text="Market Value (€)")
        st.plotly_chart(fig_age_value, use_container_width=True)

    st.markdown("")

    st.markdown("## Performance by Position")
    if 'Performance_Score' in df_filtered.columns:
        pos_performance = df_filtered.groupby('Position')['Performance_Score'].agg(['mean', 'count']).reset_index()
        pos_performance.columns = ['Position', 'Avg_Performance', 'Player_Count']
        
        fig_pos_bar = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pos_bar.add_trace(go.Bar(
            x=pos_performance['Position'], 
            y=pos_performance['Player_Count'],
            name='Player Count', 
            marker_color="#4f6ef7", 
            opacity=0.7,
        ), secondary_y=False)
        
        fig_pos_bar.add_trace(go.Scatter(
            x=pos_performance['Position'], 
            y=pos_performance['Avg_Performance'],
            name='Avg Performance', 
            mode='lines+markers',
            line=dict(color="#38c9b0", width=2),
            marker=dict(size=8),
        ), secondary_y=True)
        
        fig_pos_bar.update_layout(**CHART_THEME, height=300, title="Player Count & Avg Performance by Position")
        fig_pos_bar.update_yaxes(title_text="Player Count", secondary_y=False, gridcolor="#1e2330", color="#8892a4")
        fig_pos_bar.update_yaxes(title_text="Avg Performance", secondary_y=True, gridcolor="rgba(0,0,0,0)", color="#38c9b0")
        st.plotly_chart(fig_pos_bar, use_container_width=True)

# ── TAB 2 — DATA TABLE ───────────────────────
if show_gk_analysis:
    table_tab = tab3
else:
    table_tab = tab2

with table_tab:
    st.markdown("## Player Database")

    search = st.text_input("🔍 Search Players", placeholder="Search by name, team, position...", label_visibility="collapsed")
    
    if search:
        mask = df_filtered.apply(
            lambda col: col.astype(str).str.contains(search, case=False)
        ).any(axis=1)
        df_show = df_filtered[mask]
    else:
        df_show = df_filtered

    col_info, _ = st.columns([3, 5])
    col_info.caption(f"Showing **{len(df_show)}** of **{len(df_master)}** players")

    # Prepare display columns
    display_cols = ['Name', 'Team', 'Age', 'Position', 'Market Value', 'Matches Played', 'Performance_Score']
    available_cols = [col for col in display_cols if col in df_show.columns]
    df_display = df_show[available_cols].copy()

    # Style the dataframe
    def colour_performance(val):
        if pd.isna(val):
            return ""
        if val >= 65:
            return "color: #4f6ef7; font-weight: 600"
        elif val >= 55:
            return "color: #38c9b0"
        elif val >= 45:
            return "color: #f7c44f"
        elif val >= 35:
            return "color: #f7c44f"
        else:
            return "color: #f76b4f"

    styled = (
        df_display.style
        .map(colour_performance, subset=['Performance_Score'])
        .format({
            'Market Value': lambda x: f"€{x/1e6:.1f}M" if pd.notna(x) else 'N/A',
            'Performance_Score': '{:.1f}',
            'Age': '{:.0f}'
        })
        .set_properties(**{
            "background-color": "#161a24",
            "color": "#c5c0b8",
            "font-family": "DM Mono, monospace",
            "font-size": "12px",
        })
        .set_table_styles([{
            "selector": "th",
            "props": [
                ("background-color", "#0d0f14"),
                ("color", "#6b7a99"),
                ("font-size", "11px"),
                ("letter-spacing", "0.08em"),
                ("text-transform", "uppercase"),
            ],
        }])
    )

    st.dataframe(styled, use_container_width=True, height=480)

    col_dl, _ = st.columns([1, 5])
    csv = df_display.to_csv(index=False).encode("utf-8")
    col_dl.download_button("⬇ Export CSV", csv, "players.csv", "text/csv")

# ── TAB 3 — STATISTICAL SUMMARY ──────────────
if show_gk_analysis:
    stats_tab = tab4
else:
    stats_tab = tab3

with stats_tab:
    st.markdown("## Statistical Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Descriptive Statistics")
        numeric_cols = ['Market Value', 'Age', 'Performance_Score']
        available_numeric = [col for col in numeric_cols if col in df_filtered.columns]
        
        if available_numeric:
            desc = df_filtered[available_numeric].describe().round(2)
            st.dataframe(
                desc.style.set_properties(**{
                    "background-color": "#161a24",
                    "color": "#c5c0b8",
                    "font-family": "DM Mono, monospace",
                    "font-size": "12px",
                }).set_table_styles([{
                    "selector": "th",
                    "props": [
                        ("background-color", "#0d0f14"), 
                        ("color", "#6b7a99"),
                        ("font-size", "11px"), 
                        ("text-transform", "uppercase")
                    ],
                }]),
                use_container_width=True,
                height=300,
            )

    with col2:
        st.markdown("### Performance by Position")
        if 'Performance_Score' in df_filtered.columns:
            fig_box = px.box(
                df_filtered.dropna(subset=['Performance_Score']), 
                x='Position', 
                y='Performance_Score', 
                color='Position',
                color_discrete_sequence=["#4f6ef7","#38c9b0","#f76b4f","#f7c44f","#b04ff7"],
                points="outliers",
            )
            fig_box.update_layout(**CHART_THEME, height=300, showlegend=False, title="Performance Distribution")
            st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("")
    st.markdown("### Correlation Matrix")

    if 'Performance_Score' in df_filtered.columns:
        correlation_cols = ['Market Value', 'Age', 'Performance_Score', 'Matches Played']
        available_corr = [col for col in correlation_cols if col in df_filtered.columns]
        
        if len(available_corr) > 1:
            corr = df_filtered[available_corr].corr().round(3)

            fig_corr = px.imshow(
                corr,
                color_continuous_scale=[[0,"#f76b4f"],[0.5,"#161a24"],[1,"#4f6ef7"]],
                zmin=-1, zmax=1,
                text_auto=True,
            )
            fig_corr.update_layout(**CHART_THEME, height=320, title="Feature Correlation")
            fig_corr.update_traces(textfont=dict(color="#e8e6e1", size=14))
            st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("")
    st.markdown("### Summary Cards")
    s1, s2, s3, s4 = st.columns(4)
    
    if 'Performance_Score' in df_filtered.columns:
        s1.metric("Mean Performance", f"{df_filtered['Performance_Score'].mean():.1f}")
        s2.metric("Std Dev", f"{df_filtered['Performance_Score'].std():.1f}")
        s3.metric("Median", f"{df_filtered['Performance_Score'].median():.1f}")
        s4.metric("IQR", f"{(df_filtered['Performance_Score'].quantile(0.75) - df_filtered['Performance_Score'].quantile(0.25)):.1f}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("Football Analytics Dashboard  ·  Built with Streamlit & Plotly")
