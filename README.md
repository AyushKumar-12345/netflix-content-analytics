# 🎬 Netflix Content Analytics Dashboard

An end-to-end data analytics project exploring 8,800+ titles from Netflix's global catalog. Built with a custom cinematic dark theme, Star Schema dimensional data modeling in Python, and an interactive Power BI dashboard.

---

## 🎯 Project Overview
This project cleans raw Netflix catalog data and transforms it into an optimized dimensional model to analyze catalog trends, global production footprints, genre popularity, and release patterns over time.

---

## 📊 Key KPIs
* Total Titles: 8,807
* Movies: 6,131 (69.6%)
* TV Shows: 2,676 (30.4%)
* Average Movie Duration: 99.57 minutes
* Total Genres Covered: 42
* Total Producing Countries: 121

---

## 🏗️ Data Architecture (Star Schema)
To avoid duplicate counting caused by comma-separated values, the data was split into three normalized tables:
* Fact Table (Titles.csv): Stores title ID, type, release year, date added, duration, rating, director, and cast.
* Bridge Table (Genre.csv): Links title IDs to individual exploded genre tags.
* Bridge Table (Country.csv): Links title IDs to individual producing countries.

---

## 🛠️ Tech Stack & Scripts
* Python (Pandas, NumPy, Pillow):
  * process_netflix_data.py: Handles data sanitation, resolves schema shifts, extracts duration values, and exports the Star Schema CSV files.
  * generate_netflix_bg.py: Generates the custom 1920x1080 cinematic dark gradient background image.
* Power BI Desktop:
  * Interactive dark-mode dashboard styled with Netflix_Theme.json.
  * Custom DAX measures for dynamic filtering and KPI calculations.

---

## 📐 Core DAX Measures Used
* Total Titles = COUNTROWS('Titles')
* Total Movies = CALCULATE([Total Titles], 'Titles'[type] = "Movie")
* Total TV Shows = CALCULATE([Total Titles], 'Titles'[type] = "TV Show")
* Movie Share % = DIVIDE([Total Movies], [Total Titles], 0)
* Avg Movie Duration = AVERAGEX(FILTER('Titles', 'Titles'[type] = "Movie"), 'Titles'[duration_value])

---

## 💡 Key Business Insights
1. Catalog Split: Movies dominate the catalog acquisitions, accounting for nearly 70% of all titles.
2. Top Markets: The United States, India, and the United Kingdom represent the largest content production hubs.
3. Target Audience: TV-MA and TV-14 ratings comprise the majority of the streaming library.
4. Seasonality: Content additions consistently peak between October and January during the holiday and winter viewing season.

---

## 🚀 How to Run the Project
1. Run `python process_netflix_data.py` to generate the cleaned Titles.csv, Genre.csv, and Country.csv.
2. Run `python generate_netflix_bg.py` to produce Netflix_Background.png.
3. Open Netflix Content Analytics Dashboard.pbix in Power BI Desktop and click Refresh to load the data.

---

## 📁 Repository Structure
* Titles.csv - Cleaned fact table
* Genre.csv - Normalized genre dimension table
* Country.csv - Normalized country dimension table
* Netflix_Theme.json - Custom Power BI color palette and styling
* process_netflix_data.py - Data processing script
* generate_netflix_bg.py - Background canvas script
* Netflix Content Analytics Dashboard.pbix - Power BI report file
* Screenshots/ - Dashboard preview captures
* README.md - Project documentation

---

## 👤 Author
* Name: Ayush Kumar Dandapat
* GitHub: [AyushKumar-12345](https://github.com/AyushKumar-12345)
