import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- PAGE ARCHITECTURE ---
st.set_page_config(
    page_title="Netflix Content Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STUDIO GRADE UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Cinematic Deep Space Dark Canvas */
    .stApp {
        background-color: #0c0d10;
        background-image: 
            radial-gradient(circle at 10% 8%, rgba(229, 9, 20, 0.16) 0%, transparent 35%),
            radial-gradient(circle at 90% 90%, rgba(178, 7, 16, 0.10) 0%, transparent 40%);
        color: #FFFFFF;
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }

    /* Branding Header */
    .brand-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #E50914;
        margin: 0;
        text-shadow: 0 0 24px rgba(229, 9, 20, 0.35);
    }
    .brand-title span {
        color: #FFFFFF;
    }
    .brand-subtitle {
        color: #8C8D94;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 22px;
        font-weight: 400;
    }

    /* Filter Deck Ribbon */
    .filter-ribbon {
        background: rgba(18, 19, 24, 0.8);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 16px 20px 8px 20px;
        margin-bottom: 24px;
    }

    /* Dropdown UI Styling */
    div[data-baseweb="select"] > div {
        background-color: #14151B !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #16171E !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        z-index: 999999 !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: rgba(18, 19, 24, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-left: 3px solid #E50914;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(229, 9, 20, 0.5);
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #8C8D94;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 6px;
        line-height: 1.1;
    }
    .kpi-pill {
        display: inline-block;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 9999px;
        background-color: rgba(229, 9, 20, 0.14);
        color: #FF666B;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Studio Chart Panels */
    .panel-container {
        background: rgba(18, 19, 24, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 18px 20px 10px 20px;
        margin-bottom: 20px;
    }
    .panel-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .panel-caption {
        font-size: 0.8rem;
        color: #71727A;
        margin-top: 2px;
        margin-bottom: 10px;
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

# --- TOP BRAND HEADER ---
st.markdown("""
    <div>
        <h1 class="brand-title">NETFLIX <span>INSIGHTS</span></h1>
        <p class="brand-subtitle">Global Streaming Intelligence & Content Production Architecture</p>
    </div>
""", unsafe_allow_html=True)

# --- MODERN HORIZONTAL FILTER RIBBON ---
with st.container():
    st.markdown('<div class="filter-ribbon">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1.1, 1.6, 1.5, 1.1])

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

# --- DATA FILTERING ENGINE ---
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

# --- KEY PERFORMANCE METRICS ---
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
    <div class="kpi-card">
        <div class="kpi-label">Total Titles Filtered</div>
        <div class="kpi-value">{total_count:,}</div>
        <div class="kpi-pill">Catalog Scope</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Feature Films</div>
        <div class="kpi-value">{movies_count:,}</div>
        <div class="kpi-pill">{movie_pct}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Television Series</div>
        <div class="kpi-value">{shows_count:,}</div>
        <div class="kpi-pill">{show_pct}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Film Duration</div>
        <div class="kpi-value">{avg_duration}<span style="font-size:1.1rem;font-weight:500;color:#8C8D94;"> m</span></div>
        <div class="kpi-pill">Runtime Benchmark</div>
    </div>
    """, unsafe_allow_html=True)

# --- VISUALIZATION SECTION 1 ---
c1, c2 = st.columns([1, 1.45])

with c1:
    st.markdown("""
    <div class="panel-container">
        <div class="panel-title">Content Archetype Split</div>
        <div class="panel-caption">Proportional distribution between Movies and TV Series</div>
    """, unsafe_allow_html=True)

    type_counts = filtered["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]

    fig_donut = px.pie(
        type_counts,
        names="Type",
        values="Count",
        hole=0.68,
        color="Type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#2E303A"}
    )
    fig_donut.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont=dict(color="#D1D5DB", size=11),
        marker=dict(line=dict(color="#0c0d10", width=2.5)),
        pull=[0.02, 0.02]
    )
    fig_donut.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(t=30, b=25, l=30, r=30)
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="panel-container">
        <div class="panel-title">Release Timeline & Volume Growth</div>
        <div class="panel-caption">Annual catalog volume indexed by official production year</div>
    """, unsafe_allow_html=True)

    yearly = filtered.groupby(["release_year", "type"])["show_id"].count().reset_index()
    yearly.columns = ["Release Year", "Type", "Count"]

    fig_timeline = px.line(
        yearly,
        x="Release Year",
        y="Count",
        color="Type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#9CA3AF"},
        markers=True
    )
    fig_timeline.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8C8D94"),
        height=320,
        margin=dict(t=15, b=20, l=55, r=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FFFFFF")),
        xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.08)")
    )
    st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- VISUALIZATION SECTION 2 ---
c3, c4 = st.columns(2)

with c3:
    st.markdown("""
    <div class="panel-container">
        <div class="panel-title">Top 10 Catalog Genres</div>
        <div class="panel-caption">Category saturation based on active filter parameters</div>
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
        font=dict(color="#8C8D94"),
        height=350,
        margin=dict(t=10, b=10, l=15, r=15),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.08)")
    )
    st.plotly_chart(fig_genre, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="panel-container">
        <div class="panel-title">Top 10 Production Hubs</div>
        <div class="panel-caption">Leading origin countries by release volume</div>
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
        font=dict(color="#8C8D94"),
        height=350,
        margin=dict(t=10, b=10, l=55, r=15),
        xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.08)")
    )
    st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- INTERACTIVE SEARCH DECK ---
st.markdown("""
<div class="panel-container">
    <div class="panel-title">Catalog Explorer & Deep Search</div>
    <div class="panel-caption">Search specific titles, actors, or directors across the filtered catalog</div>
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
