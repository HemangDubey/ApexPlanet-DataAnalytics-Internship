# 📈 Task 2 — Exploratory Data Analysis & Business Intelligence

## Objective
Perform a comprehensive **Exploratory Data Analysis (EDA)** on the cleaned retail dataset, answer critical business questions using **SQL**, and produce publication-quality visualizations that reveal hidden patterns in customer behavior, revenue distribution, and product performance.

---

## 📂 Deliverables

| File / Directory | Description |
|------------------|-------------|
| `task2_eda.py` | Full EDA engine (`GravityEDA` class) — CLI tool with 4 analysis steps |
| `Task_2_Output/charts/` | 10+ high-quality, dark-themed analytical charts (PNG) |
| `Task_2_Output/eda_report.md` | Auto-generated comprehensive EDA summary report |
| `Task_2_Output/sql_results/` | SQL query outputs saved as structured results |
| `Task_2_Output/dashboard_mockup.png` | Static KPI dashboard mockup image |

---

## 🔬 Analysis Pipeline

### Step 1: Descriptive & Univariate Analysis
- **Summary Statistics:** Mean, median, standard deviation, skewness, kurtosis across all numerical columns
- **Revenue Distribution:** Histogram with kernel density estimation
- **Quantity Distribution:** Purchase volume frequency analysis
- **Temporal Trends:** Monthly revenue time series, day-of-week patterns, hourly transaction volume

### Step 2: SQL Business Intelligence Queries
Loaded the dataset into an **in-memory SQLite database** and answered 7 critical business questions:
1. Top 10 revenue-generating countries
2. Monthly revenue trends with growth rates
3. Top 15 best-selling products by revenue
4. Customer purchase frequency distribution
5. Revenue contribution by day of week
6. Peak shopping hours analysis
7. Customer segmentation by transaction value

### Step 3: Multivariate & Correlation Analysis
- **Correlation Heatmap:** Identified relationships between price, quantity, and revenue
- **Customer Revenue Distribution:** Pareto analysis showing revenue concentration
- **Country × Product Analysis:** Cross-dimensional revenue breakdowns
- **Scatter Plots:** Price vs. quantity elasticity patterns

### Step 4: Static Dashboard Mockup
- Created a single-image KPI dashboard combining the most important metrics and charts
- Designed with a premium dark theme matching the overall project aesthetic

---

## 📊 Key Findings
- **Revenue:** £20.48M across 40,078 orders
- **Top Market:** United Kingdom (dominant revenue share)
- **Peak Days:** Tuesdays and Thursdays generate highest volume
- **Peak Hours:** 10:00 AM – 12:00 PM (suggesting B2B purchasing patterns)
- **Pareto Rule:** ~20% of customers drive ~80% of total revenue
- **AOV:** £510.92 average order value

---

## 🛠️ Technologies Used
- **Python 3** — Core language
- **Pandas** — Data analysis and aggregation
- **Matplotlib & Seaborn** — Publication-quality visualizations (dark theme)
- **SQLite** — In-memory SQL database for business queries
- **NumPy & SciPy** — Statistical calculations

## ▶️ How to Run

```bash
cd Task-2-EDA-Business-Intelligence
python task2_eda.py --input ../Task-1-Data-Immersion-Wrangling/Task_1_Output/cleaned_data.csv --output Task_2_Output
```

---

*Part of the [Apex Planet Data Analytics Internship](https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio) by [Hemang Dubey](https://www.linkedin.com/in/hemang-dubey-7b801628b/)*
