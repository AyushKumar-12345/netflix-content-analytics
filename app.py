import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Netflix Content Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED NETFLIX THEME STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(229, 9, 20, 0.08) 0%, rgba(14, 14, 16, 1) 40%),
                    radial-gradient(circle at 90% 85%, rgba(178, 7, 16, 0.06) 0%, rgba(14, 14, 16, 1) 45%);
        background-color: #0E0E10;
        color: #F3F4F6;
    }

    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #121214 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Header & Branding */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-bottom: 8px;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0;
    }
    .brand-title span {
        color: #E50914;
    }
    .brand-subtitle {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 0px;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(22, 22, 26, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(229, 9, 20, 0.4);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #E50914, transparent);
    }
    .metric-header {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #9CA3AF;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 8px;
        line-height: 1;
    }
    .metric-badge {
        display: inline-block;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 9999px;
        background-color: rgba(229, 9, 20, 0.15);
        color: #FF5A5F;
        font-weight: 600;
        margin-top: 10px;
    }

    /* Chart Containers */
    .chart-box {
        background: rgba(22, 22, 26, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 18px 20px 10px 20px;
        margin-bottom: 20px;
    }
    .chart-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-subtitle {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 12px;
    }

    /* Streamlit Widget Polish */
    .stSelectbox label, .stSlider label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #D1D5DB !important;
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

# --- SIDEBAR INTERFACE ---
with st.sidebar:
    st.markdown("### 🎛️ Catalog Controls")

    content_type_options = ["All Types"] + sorted(titles["type"].dropna().unique().tolist())
    selected_type = st.selectbox("Content Segment", content_type_options)

    min_yr = int(titles["release_year"].min())
    max_yr = int(titles["release_year"].max())
    selected_years = st.slider(
        "Release Horizon",
        min_value=min_yr,
        max_value=max_yr,
        value=(2008, max_yr)
    )

    all_genres = ["All Genres"] + sorted(genres["genre"].dropna().unique().tolist())
    selected_genre = st.selectbox("Genre Category", all_genres)

    all_ratings = ["All Ratings"] + sorted(titles["rating"].dropna().unique().tolist())
    selected_rating = st.selectbox("Maturity Rating", all_ratings)

# --- FILTERING LOGIC ---
filtered = titles[
    (titles["release_year"] >= selected_years[0]) &
    (titles["release_year"] <= selected_years[1])
]

if selected_type != "All Types":
    filtered = filtered[filtered["type"] == selected_type]

if selected_genre != "All Genres":
    matching_show_ids = genres[genres["genre"] == selected_genre]["show_id"]
    filtered = filtered[filtered["show_id"].isin(matching_show_ids)]

if selected_rating != "All Ratings":
    filtered = filtered[filtered["rating"] == selected_rating]


# --- TOP BANNER ---
st.markdown("""
<div class="brand-container">
    <div>
        <h1 class="brand-title">NETFLIX <span>INSIGHTS</span></h1>
        <p class="brand-subtitle">Global Streaming Intelligence & Content Production Architecture</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- KEY PERFORMANCE INDICATORS ---
total_count = len(filtered)
movies_count = len(filtered[filtered["type"] == "Movie"])
shows_count = len(filtered[filtered["type"] == "TV Show"])

movie_subset = filtered[filtered["type"] == "Movie"]
avg_duration = round(movie_subset["duration_value"].mean(), 1) if not movie_subset.empty else 0

movie_pct = round((movies_count / total_count * 100), 1) if total_count > 0 else 0
show_pct = round((shows_count / total_count * 100), 1) if total_count > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Total Titles Filtered</div>
        <div class="metric-value">{total_count:,}</div>
        <div class="metric-badge">Catalog Scope</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Feature Films</div>
        <div class="metric-value">{movies_count:,}</div>
        <div class="metric-badge">{movie_pct}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Television Series</div>
        <div class="metric-value">{shows_count:,}</div>
        <div class="metric-badge">{show_pct}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">Avg Film Duration</div>
        <div class="metric-value">{avg_duration}<span style="font-size:1.1rem;font-weight:500;color:#9CA3AF;"> m</span></div>
        <div class="metric-badge">Runtime Benchmark</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
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

    fig_donut = go.Figure(data=[go.Pie(
        labels=type_counts["Type"],
        values=type_counts["Count"],
        hole=0.62,
        marker=dict(colors=["#E50914", "#2B2B30"], line=dict(color="#141416", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#FFFFFF", size=12),
        hoverinfo="label+value+percent",
    )])
    fig_donut.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="chart-box">
        <div class="chart-title">Release Timeline & Volume Growth</div>
        <div class="chart-subtitle">Annual releases indexed by historical original air date</div>
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
        height=320,
        margin=dict(t=10, b=10, l=10, r=10),
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
        <div class="chart-subtitle">Category saturation across selected filter parameters</div>
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
        height=350,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)")
    )
    fig_genre.update_traces(marker=dict(line=dict(width=0)))
    st.plotly_chart(fig_genre, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="chart-box">
        <div class="chart-title">Top 10 Production Territories</div>
        <div class="chart-subtitle">Leading origin countries by overall release footprint</div>
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
        height=350,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)")
    )
    st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- SEARCH & EXPLORATION TABLE ---
st.markdown("""
<div class="chart-box">
    <div class="chart-title">Catalog Explorer & Deep Search</div>
    <div class="chart-subtitle">Search specific titles, actors, or directors in the active filter selection</div>
""", unsafe_allow_html=True)

search_term = st.text_input("Search catalog", placeholder="Search by title, director, cast...")

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
