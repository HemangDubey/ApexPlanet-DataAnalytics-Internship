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

## Repository Structure

```
ApexPlanet-DataAnalytics-Internship/
├── Task-1-Data-Immersion-Wrangling/
│   ├── task1_wrangler.py          # Main wrangling script
│   ├── data/
│   │   └── raw_data.csv           # Raw dataset (not tracked - too large)
│   └── Task_1_Output/
│       ├── cleaned_data.csv       # Cleaned output
│       └── data_dictionary.md     # Auto-generated data dictionary
├── .gitignore
└── README.md
```

---

**Author:** Hemang Dubey
