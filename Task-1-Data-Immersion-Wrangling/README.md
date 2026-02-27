# 🧹 Task 1 — Data Immersion & Wrangling

## Objective
Transform a raw, messy retail transactions dataset into a **clean, analysis-ready** format using a production-grade Python pipeline. This task establishes the data foundation that all subsequent tasks build upon.

---

## 📂 Deliverables

| File | Description |
|------|-------------|
| `task1_wrangler.py` | Production-grade CLI wrangling tool (`GravityWrangler` class) |
| `Task_1_Output/cleaned_data.csv` | Cleaned, transformed, and feature-engineered dataset |
| `Task_1_Output/data_dictionary.md` | Auto-generated data dictionary describing every column |

---

## 🔧 Pipeline Steps

### Step 1: Data Quality Assessment
- Loaded raw dataset and profiled every column
- Identified missing values, duplicates, and data type mismatches
- Detected outliers using the **IQR method** (1.5× Interquartile Range fence)
- Generated a comprehensive quality summary report

### Step 2: Cleaning & Transformation
- **Missing Values:** Intelligent imputation (median for numerics, mode for categoricals)
- **Duplicates:** Identified and removed exact duplicate rows
- **Column Names:** Standardized all headers to `snake_case` format
- **Text Fields:** Stripped whitespace, normalized casing
- **Data Types:** Coerced columns to appropriate types (datetime, numeric, categorical)

### Step 3: Feature Engineering
- **Temporal Features:** Extracted `year`, `month`, `day_of_week`, `hour` from date columns
- **Revenue Column:** Computed `revenue = quantity × unit_price` where not present
- **Customer Age:** Calculated time-based customer tenure metrics

### Step 4: Artifact Generation
- Exported the cleaned dataset as `cleaned_data.csv`
- Auto-generated a Markdown **Data Dictionary** with column names, types, descriptions, and sample values

---

## 🛠️ Technologies Used
- **Python 3** — Core language
- **Pandas** — Data manipulation and transformation
- **NumPy** — Numerical computations
- **argparse** — CLI interface for flexible execution

## ▶️ How to Run

```bash
cd Task-1-Data-Immersion-Wrangling
python task1_wrangler.py --input data/raw_data.csv --output Task_1_Output
```

---

*Part of the [Apex Planet Data Analytics Internship](https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio) by [Hemang Dubey](https://www.linkedin.com/in/hemang-dubey-7b801628b/)*
