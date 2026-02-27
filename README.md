# ApexPlanet Data Analytics Internship

A collection of production-grade data analytics tasks completed during the **ApexPlanet Data Analytics Internship** program.

---

## Task 1: Data Immersion & Wrangling

A robust CLI tool built with Python that automates end-to-end data cleaning, profiling, and feature engineering.

### Features

- **Data Quality Assessment** — Missing values, duplicates, IQR outlier detection
- **Automated Cleaning** — Median/mode imputation, deduplication, snake_case standardization
- **Feature Engineering** — Auto-detects date columns, extracts year/month/day_name
- **Data Dictionary** — Auto-generates a Markdown data dictionary with column metadata
- **CLI Interface** — Fully automated via `argparse`, no interactive inputs

### Tech Stack

`Python 3.x` · `pandas` · `numpy` · `argparse`

### Usage

```bash
cd Task-1-Data-Immersion-Wrangling
python task1_wrangler.py --input data/raw_data.csv --output ./Task_1_Output
```

### Output Artifacts

| File | Description |
|------|-------------|
| `cleaned_data.csv` | Analysis-ready dataset with imputed values, no duplicates |
| `data_dictionary.md` | Markdown table documenting every column's type, stats, and description |

### Class Architecture: `GravityWrangler`

| Method | Purpose |
|--------|---------|
| `__init__(file_path)` | Load CSV/XLSX with error handling |
| `assess_quality()` | Profile missing values, duplicates, outliers (IQR) |
| `clean_and_transform()` | Impute, deduplicate, standardize column names |
| `engineer_features()` | Auto-detect dates, extract temporal features |
| `generate_data_dictionary()` | Build structured column metadata |
| `save_artifacts(output_folder)` | Export cleaned CSV + data dictionary |

---

## Task 2: Exploratory Data Analysis & Business Intelligence

A comprehensive EDA pipeline that uncovers patterns, trends, and relationships in the data using statistical analysis, SQL queries, and advanced visualizations.

### Features

- **Descriptive & Univariate Analysis** — Summary statistics, histograms, bar charts, box plots
- **SQL Business Questions** — 7 real-world queries answered via SQLite (revenue, customers, products, trends)
- **Multivariate Analysis** — Correlation heatmap, scatter plots, year×month heatmap, pair plots
- **Static Dashboard Mock-up** — Full KPI dashboard with 6 panels (revenue, orders, customers, trends)
- **Auto-generated Reports** — EDA report + SQL queries report in Markdown

### Tech Stack

`Python 3.x` · `pandas` · `NumPy` · `matplotlib` · `seaborn` · `SQLite`

### Usage

```bash
cd Task-2-EDA-Business-Intelligence
python task2_eda.py --input ../Task-1-Data-Immersion-Wrangling/Task_1_Output/cleaned_data.csv
```

### Output Artifacts

| File | Description |
|------|-------------|
| `dashboard_mockup.png` | Full KPI dashboard with 6 visualization panels |
| `eda_report.md` | Comprehensive EDA findings and insights |
| `sql_results/sql_queries_report.md` | 7 SQL business questions with results |
| `charts/` (11 files) | Individual analysis charts (dark-themed, publication-ready) |

---

## Repository Structure

```
ApexPlanet-DataAnalytics-Internship/
├── Task-1-Data-Immersion-Wrangling/
│   ├── task1_wrangler.py
│   ├── data/
│   │   └── raw_data.csv               # (not tracked - too large)
│   └── Task_1_Output/
│       └── data_dictionary.md
├── Task-2-EDA-Business-Intelligence/
│   ├── task2_eda.py
│   └── Task_2_Output/
│       ├── dashboard_mockup.png
│       ├── eda_report.md
│       ├── charts/                     # 11 visualization PNGs
│       └── sql_results/
│           └── sql_queries_report.md
├── .gitignore
└── README.md
```

---

**Author:** Hemang Dubey
