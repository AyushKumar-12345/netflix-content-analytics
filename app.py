import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Netflix Content Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (NETFLIX BRANDING) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #141414;
        color: #FFFFFF;
    }
    header, footer {
        visibility: hidden;
    }
    .metric-card {
        background-color: #1F1F1F;
        border-radius: 8px;
        padding: 16px 20px;
        border-left: 4px solid #E50914;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #A3A3A3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    base = Path(__file__).resolve().parent
    titles_df = pd.read_csv(base / "Titles.csv")
    genre_df = pd.read_csv(base / "Genre.csv")
    country_df = pd.read_csv(base / "Country.csv")
    return titles_df, genre_df, country_df

try:
    titles, genres, countries = load_data()
except Exception as e:
    st.error(f"Error loading CSV files: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("🎬 Filter Catalog")

# Type filter
content_types = ["All"] + list(titles["type"].dropna().unique())
selected_type = st.sidebar.selectbox("Content Type", content_types)

# Release year filter
min_year = int(titles["release_year"].min())
max_year = int(titles["release_year"].max())
selected_year_range = st.sidebar.slider(
    "Release Year",
    min_value=min_year,
    max_value=max_year,
    value=(2010, max_year)
)

# Genre filter
all_genres = ["All"] + sorted(genres["genre"].dropna().unique().tolist())
selected_genre = st.sidebar.selectbox("Genre", all_genres)

# Apply Filters
filtered_titles = titles[
    (titles["release_year"] >= selected_year_range[0]) &
    (titles["release_year"] <= selected_year_range[1])
]

if selected_type != "All":
    filtered_titles = filtered_titles[filtered_titles["type"] == selected_type]

if selected_genre != "All":
    matching_ids = genres[genres["genre"] == selected_genre]["show_id"]
    filtered_titles = filtered_titles[filtered_titles["show_id"].isin(matching_ids)]

# --- MAIN DASHBOARD HEADER ---
st.title("🎬 Netflix Content Analytics Dashboard")
st.markdown("Interactive portfolio dashboard analyzing catalog volume, genres, and geographic distributions.")

# --- TOP METRIC CARDS ---
total_titles = len(filtered_titles)
movie_count = len(filtered_titles[filtered_titles["type"] == "Movie"])
show_count = len(filtered_titles[filtered_titles["type"] == "TV Show"])

movie_subset = filtered_titles[filtered_titles["type"] == "Movie"]
avg_duration = round(movie_subset["duration_value"].mean(), 1) if not movie_subset.empty else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Titles</div>
            <div class="metric-value">{total_titles:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Movies</div>
            <div class="metric-value">{movie_count:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TV Shows</div>
            <div class="metric-value">{show_count:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Movie Duration</div>
            <div class="metric-value">{avg_duration} <span style="font-size:1rem;color:#A3A3A3;">min</span></div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# --- CHARTS SECTION ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Content Type Split")
    type_counts = filtered_titles["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]
    
    fig_pie = px.pie(
        type_counts,
        names="type",
        values="count",
        color="type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#564D4D"},
        hole=0.45
    )
    fig_pie.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font_color="#FFFFFF",
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with row1_col2:
    st.subheader("Content Additions by Release Year")
    yearly = filtered_titles.groupby("release_year")["show_id"].count().reset_index()
    yearly.columns = ["Release Year", "Count"]

    fig_line = px.line(
        yearly,
        x="Release Year",
        y="Count",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#E50914"]
    )
    fig_line.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font_color="#FFFFFF",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#282828"),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_line, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Top 10 Genres")
    filtered_genre_df = genres[genres["show_id"].isin(filtered_titles["show_id"])]
    top_genres = (
        filtered_genre_df["genre"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_genres.columns = ["Genre", "Count"]

    fig_bar = px.bar(
        top_genres.sort_values("Count", ascending=True),
        x="Count",
        y="Genre",
        orientation="h",
        color_discrete_sequence=["#B20710"]
    )
    fig_bar.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font_color="#FFFFFF",
        xaxis=dict(gridcolor="#282828"),
        yaxis=dict(showgrid=False),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_col2:
    st.subheader("Top 10 Producing Countries")
    filtered_countries = countries[countries["show_id"].isin(filtered_titles["show_id"])]
    top_countries = (
        filtered_countries["country"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_countries.columns = ["Country", "Count"]

    fig_country = px.bar(
        top_countries,
        x="Country",
        y="Count",
        color_discrete_sequence=["#E50914"]
    )
    fig_country.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font_color="#FFFFFF",
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#282828"),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_country, use_container_width=True)

# --- DATA TABLE VIEW ---
with st.expander("🔍 Explore Filtered Catalog Data"):
    st.dataframe(
        filtered_titles[["title", "type", "release_year", "rating", "duration", "country"]],
        use_container_width=True
    )
