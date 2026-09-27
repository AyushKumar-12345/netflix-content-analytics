import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Netflix Content Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN STREAMING UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0E0E10;
        background-image: 
            radial-gradient(circle at 12% 15%, rgba(229, 9, 20, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 88% 85%, rgba(178, 7, 16, 0.08) 0%, transparent 40%);
        color: #F3F4F6;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Top Filter Container */
    .filter-container {
        background: rgba(20, 20, 24, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px 8px 20px;
        margin-bottom: 24px;
    }

    /* Fix Dropdown Popovers */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #1A1A1E !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        z-index: 999999 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #141416 !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }

    /* Header Styling */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.1;
    }
    .brand-title span {
        color: #E50914;
    }
    .brand-subtitle {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 20px;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(22, 22, 26, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        border-left: 3px solid #E50914;
    }
    .metric-header {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #9CA3AF;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 6px;
        line-height: 1;
    }
    .metric-badge {
        display: inline-block;
        font-size: 0.72rem;
        padding: 2px 7px;
        border-radius: 9999px;
        background-color: rgba(229, 9, 20, 0.15);
        color: #FF5A5F;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Chart Containers */
    .chart-box {
        background: rgba(20, 20, 24, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 18px 20px 12px 20px;
        margin-bottom: 20px;
    }
    .chart-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .chart-subtitle {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# --- DATA ENGINE ---
@st.cache_data
def load_datasets():
    base = Path(__file__).resolve().parent
    titles_df = pd.read_csv(base / "Titles.csv")
    genre_df = pd.read_csv(base / "Genre.csv")
    country_df = pd.read_csv(base / "Country.csv")
    return titles_df, genre_df, country_df


titles, genres, countries = load_datasets()

# --- TOP BANNER ---
st.markdown("""
    <div>
        <h1 class="brand-title">NETFLIX <span>INSIGHTS</span></h1>
        <p class="brand-subtitle">Global Streaming Intelligence & Content Production Architecture</p>
    </div>
""", unsafe_allow_html=True)

# --- MODERN HORIZONTAL FILTER RIBBON ---
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1.2, 1.6, 1.6, 1.2])

    with f1:
        content_type_options = ["All Types"] + sorted(titles["type"].dropna().unique().tolist())
        selected_type = st.selectbox("Content Segment", content_type_options)

    with f2:
        min_yr = int(titles["release_year"].min())
        max_yr = int(titles["release_year"].max())
        selected_years = st.slider(
            "Release Horizon",
            min_value=min_yr,
            max_value=max_yr,
            value=(2008, max_yr)
        )

    with f3:
        all_genres = ["All Genres"] + sorted(genres["genre"].dropna().unique().tolist())
        selected_genre = st.selectbox("Genre Category", all_genres)

    with f4:
        all_ratings = ["All Ratings"] + sorted(titles["rating"].dropna().unique().tolist())
        selected_rating = st.selectbox("Maturity Rating", all_ratings)

    st.markdown('</div>', unsafe_allow_html=True)

# --- FILTERING LOGIC ---
filtered = titles[
    (titles["release_year"] >= selected_years[0]) &
    (titles["release_year"] <= selected_years[1])
]

if selected_type != "All Types":
    filtered = filtered[filtered["type"] == selected_type]

if selected_genre != "All Genres":
    matching_ids = genres[genres["genre"] == selected_genre]["show_id"]
    filtered = filtered[filtered["show_id"].isin(matching_ids)]

if selected_rating != "All Ratings":
    filtered = filtered[filtered["rating"] == selected_rating]

# --- KEY PERFORMANCE INDICATORS ---
total_count = len(filtered)
movies_count = len(filtered[filtered["type"] == "Movie"])
shows_count = len(filtered[filtered["type"] == "TV Show"])

movie_subset = filtered[filtered["type"] == "Movie"]
avg_duration = round(movie_subset["duration_value"].mean(), 1) if not movie_subset.empty else 0

movie_pct = round((movies_count / total_count * 100), 1) if total_count > 0 else 0
show_pct = round((shows_count / total_count * 100), 1) if total_count > 0 else 0

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Total Titles Filtered</div>
        <div class="metric-value">{total_count:,}</div>
        <div class="metric-badge">Catalog Scope</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Feature Films</div>
        <div class="metric-value">{movies_count:,}</div>
        <div class="metric-badge">{movie_pct}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Television Series</div>
        <div class="metric-value">{shows_count:,}</div>
        <div class="metric-badge">{show_pct}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Avg Film Duration</div>
        <div class="metric-value">{avg_duration}<span style="font-size:1.1rem;font-weight:500;color:#9CA3AF;"> m</span></div>
        <div class="metric-badge">Runtime Benchmark</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- ROW 1: CONTENT ARCHITECTURE & TIME INTELLIGENCE ---
c1, c2 = st.columns([1, 1.4])

with c1:
    st.markdown("""
    <div class="chart-box">
        <div class="chart-title">Content Archetype Split</div>
        <div class="chart-subtitle">Volume ratio between Movies and Episodic Series</div>
    """, unsafe_allow_html=True)

    type_counts = filtered["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]

    fig_donut = px.pie(
        type_counts,
        names="Type",
        values="Count",
        hole=0.6,
        color="Type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#333338"}
    )
    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent",
        insidetextfont=dict(size=14, color="#FFFFFF"),
        marker=dict(line=dict(color="#141416", width=2))
    )
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color="#FFFFFF")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=330,
        margin=dict(t=20, b=30, l=15, r=15)
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="chart-box">
        <div class="chart-title">Release Timeline & Volume Growth</div>
        <div class="chart-subtitle">Annual catalog additions categorized by content format</div>
    """, unsafe_allow_html=True)

    yearly = filtered.groupby(["release_year", "type"])["show_id"].count().reset_index()
    yearly.columns = ["Release Year", "Type", "Count"]

    fig_timeline = px.line(
        yearly,
        x="Release Year",
        y="Count",
        color="Type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#FFFFFF"},
        markers=True
    )
    fig_timeline.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9CA3AF"),
        height=330,
        margin=dict(t=15, b=20, l=15, r=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FFFFFF")),
        xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)")
    )
    st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- ROW 2: GENRES & GEOGRAPHICS ---
c3, c4 = st.columns(2)

with c3:
    st.markdown("""
    <div class="chart-box">
        <div class="chart-title">Top 10 Catalog Genres</div>
        <div class="chart-subtitle">Category density across active filter scope</div>
    """, unsafe_allow_html=True)

    filtered_genres = genres[genres["show_id"].isin(filtered["show_id"])]
    top_genres = filtered_genres["genre"].value_counts().head(10).reset_index()
    top_genres.columns = ["Genre", "Volume"]

    fig_genre = px.bar(
        top_genres.sort_values("Volume", ascending=True),
        x="Volume",
        y="Genre",
        orientation="h",
        color_discrete_sequence=["#E50914"]
    )
    fig_genre.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9CA3AF"),
        height=360,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)")
    )
    st.plotly_chart(fig_genre, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="chart-box">
        <div class="chart-title">Top 10 Production Territories</div>
        <div class="chart-subtitle">Origin countries by release volume</div>
    """, unsafe_allow_html=True)

    filtered_countries = countries[countries["show_id"].isin(filtered["show_id"])]
    top_countries = filtered_countries["country"].value_counts().head(10).reset_index()
    top_countries.columns = ["Country", "Volume"]

    fig_geo = px.bar(
        top_countries,
        x="Country",
        y="Volume",
        color_discrete_sequence=["#B20710"]
    )
    fig_geo.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9CA3AF"),
        height=360,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)")
    )
    st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- CATALOG SEARCH SECTION ---
st.markdown("""
<div class="chart-box">
    <div class="chart-title">Catalog Explorer & Deep Search</div>
    <div class="chart-subtitle">Search specific titles, actors, or directors in the active filter selection</div>
""", unsafe_allow_html=True)

search_term = st.text_input("Search catalog", placeholder="Search by title, director, cast...", label_visibility="collapsed")

table_view = filtered[["title", "type", "release_year", "rating", "duration", "director", "country"]].copy()

if search_term:
    mask = (
        table_view["title"].astype(str).str.contains(search_term, case=False, na=False) |
        table_view["director"].astype(str).str.contains(search_term, case=False, na=False)
    )
    table_view = table_view[mask]

st.dataframe(
    table_view.rename(columns={
        "title": "Title",
        "type": "Type",
        "release_year": "Release Year",
        "rating": "Rating",
        "duration": "Duration",
        "director": "Director",
        "country": "Country"
    }),
    use_container_width=True,
    height=260
)
st.markdown("</div>", unsafe_allow_html=True)
