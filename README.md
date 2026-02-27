<div align="center">
  
# 🚀 Hemang Dubey — Data Analyst Internship Portfolio

### *A comprehensive, end-to-end Data Analytics portfolio built across 4 progressive tasks*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Hemang%20Dubey-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/hemang-dubey-7b801628b/)
[![GitHub](https://img.shields.io/badge/GitHub-HemangDubey-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/HemangDubey)

---

**Data Wrangling** · **Exploratory Analysis** · **Interactive Dashboarding** · **AI-Powered BI** · **Data Storytelling** · **Statistical Validation**

</div>

---

## 📋 Internship Overview

This repository contains the complete deliverables for the **Apex Planet Data Analytics Internship**, where each task builds progressively on the previous one — forming a cohesive analytics pipeline from raw data ingestion to executive-level business storytelling powered by AI.

> **Dataset:** Global retail transactions (Dec 2009 – Dec 2011) comprising **40,078 orders**, **5,878 customers**, **5,357 products**, and **43 countries**, generating **£20.48M** in gross revenue.

---

## 🎬 Implementation Demo

<div align="center">

[![Watch the Implementation Video](https://img.shields.io/badge/▶%20Watch%20Demo-Implementation%20Video-FF0000?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1-5QFohiZKBhaqQxNyQcRa8vFlKuYau9g/view?usp=drive_link)

</div>

---

## 📂 Task Breakdown

### [`Task 1` — Data Immersion & Wrangling](https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio/tree/main/Task-1-Data-Immersion-Wrangling)

> *Transform raw, messy data into a clean, analysis-ready dataset.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Ingest raw retail data, profile quality issues, clean & transform, engineer features |
| **Key Deliverables** | Production-grade Python CLI tool (`GravityWrangler`), cleaned dataset, auto-generated data dictionary |
| **Techniques** | Missing value imputation, duplicate removal, snake_case standardization, IQR outlier detection, datetime feature engineering |
| **Output** | `cleaned_data.csv` + `data_dictionary.md` |

---

### [`Task 2` — Exploratory Data Analysis & Business Intelligence](https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio/tree/main/Task-2-EDA-Business-Intelligence)

> *Uncover hidden patterns through statistical analysis & SQL-powered business questions.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Perform univariate/bivariate/multivariate analysis, answer 7 SQL business questions, build static KPI dashboard |
| **Key Deliverables** | Python EDA engine (`GravityEDA`), 10+ publication-quality charts, SQL query results, dashboard mockup PNG |
| **Techniques** | Descriptive statistics, revenue distributions, correlation heatmaps, customer segmentation, SQLite-powered queries |
| **Output** | Charts directory, `eda_report.md`, `sql_results/`, `dashboard_mockup.png` |

---

### [`Task 3` — Deep-Dive Analysis & Interactive Dashboarding + AI Modules](https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio/tree/main/Task-3-DeepDive-Interactive-Dashboard)

> *A full-stack, AI-powered interactive BI platform with 8 dashboard modules.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Build a production-ready interactive dashboard with deep analytics, predictive simulation, and AI chatbot |
| **Key Deliverables** | Custom SPA dashboard (Vanilla HTML/CSS/JS), Node.js/Express backend, Groq AI integration |
| **Dashboard Modules** | Overview KPIs, Deep EDA, Cohort & RFM Segmentation, SQL Queries, Strategic Insights, KPI Reference, CSV Engine, Simulation Lab |
| **AI Features** | 🍯 **H.O.N.E.Y** chatbot (Llama 3 70B via Groq), 🧪 Business Simulation Lab, 📁 Dynamic CSV Engine |

**Tech Stack:** `HTML5` · `CSS3 (Glassmorphism)` · `JavaScript ES6+` · `Chart.js` · `Node.js` · `Express` · `Groq SDK` · `PapaParse`

---

### [`Task 4` — Data Storytelling & Statistical Validation](https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio/tree/main/Task-4-Data-Storytelling-Statistical-Validation)

> *Convert analytical findings into a compelling executive narrative backed by statistical proof.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Create a professional Data Story Report and statistically validate business hypotheses |
| **Key Deliverables** | Data Story Report (PDF), Data Insights Report (PDF), Hypothesis Testing (Chi-Square analysis) |
| **Hypothesis Tested** | "Do order cancellations significantly increase customer churn probability?" |
| **Result** | **H₀ Rejected** — χ² = 214.63, p < 0.00001. Cancellation customers churn at **82.3%** vs **48.1%** baseline |

---

## 📊 Key Metrics at a Glance

<div align="center">

| Metric | Value |
|--------|-------|
| 💰 **Total Revenue** | £20,476,634 |
| 📦 **Total Orders** | 40,078 |
| 👥 **Unique Customers** | 5,878 |
| 🌍 **Countries Served** | 43 |
| 📈 **Avg Order Value** | £510.92 |
| 👑 **Customer Lifetime Value** | £1,699 |
| 🔄 **Retention Rate** | 49.1% |
| ⚠️ **Churn Rate** | 50.9% |
| ❌ **Revenue Lost (Cancellations)** | £1,462,424 |
| 🧪 **Simulated Growth Potential** | +115.26% |

</div>

---

## 🧠 Key Learnings & Technical Skills Demonstrated

### Data Engineering & Wrangling
- Designed and implemented a **production-grade data pipeline** capable of processing 500K+ raw records into analysis-ready datasets
- Developed automated **data quality profiling** with IQR outlier detection, missing value diagnostics, and data type inference
- Built reusable **CLI tools** using `argparse` for reproducible data workflows

### Statistical Analysis & EDA
- Applied **descriptive statistics** (mean, median, skewness, kurtosis) to characterize revenue and customer behavior distributions
- Conducted **Pareto (80/20) analysis** revealing that <20% of customers drive 75%+ of revenue
- Performed **hypothesis testing** (Chi-Square, p < 0.00001) to statistically validate the causal link between order cancellations and customer churn

### SQL & Database Querying
- Wrote **10+ complex SQL queries** using CTEs, Window Functions (`ROW_NUMBER`, `LAG`), and CASE statements
- Used **SQLite as an in-memory analytical engine** to answer critical business questions at speed
- Designed queries for cohort analysis, RFM segmentation, and time-series revenue aggregation

### Data Visualization & Dashboard Design
- Created a **custom interactive SPA dashboard** from scratch (zero frameworks, pure HTML/CSS/JS)
- Designed a **premium dark-mode glassmorphism UI** with micro-animations and responsive layout
- Built **8 interconnected dashboard modules** — from KPI cards to cohort heatmaps to correlation matrices
- Implemented **Chart.js** for line/pie charts and **custom HTML/CSS bars** for maximum visual control

### AI / Machine Learning Integration
- Integrated **Groq API (Llama 3.3 70B)** to build a context-aware AI chatbot (H.O.N.E.Y) that reads live dataset metadata
- Designed a **structured prompt engineering pipeline** with system prompts, context injection, and conversational memory
- Implemented server-side **API key protection**, rate limiting, and input sanitization

### Full-Stack Engineering
- Built a **Node.js/Express backend** serving both static files and RESTful API endpoints on a single port
- Developed a **client-side CSV parsing engine** (PapaParse) with automatic schema detection and KPI generation
- Created a **Business Simulation Engine** with compound growth, churn decay, and price elasticity modeling over 12-month projections

### Business Communication & Storytelling
- Translated complex data findings into a **9-section executive narrative** suitable for C-suite presentation
- Formulated **5 actionable strategic recommendations** (VIP retention, peak-hour flash sales, catalog pruning) grounded in quantitative evidence
- Delivered insights on **£1.46M in revenue loss** from cancellations and its downstream impact on customer lifetime value

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Data Processing** | Python, Pandas, NumPy, SciPy |
| **Database** | SQLite (in-memory analytics) |
| **Visualization** | Matplotlib, Seaborn, Chart.js |
| **Frontend** | HTML5, CSS3 (Custom Design System), Vanilla JavaScript |
| **Backend** | Node.js, Express.js |
| **AI/ML** | Groq SDK (Llama 3.3 70B), PapaParse |
| **Version Control** | Git, GitHub |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/HemangDubey/Hemang-Dubey-DataAnalyst-Internship-Portfolio.git
cd Hemang-Dubey-DataAnalyst-Internship-Portfolio

# Task 1: Run the data wrangler
cd Task-1-Data-Immersion-Wrangling
python task1_wrangler.py --input data/raw_data.csv --output Task_1_Output

# Task 2: Run the EDA engine
cd ../Task-2-EDA-Business-Intelligence
python task2_eda.py --input ../Task-1-Data-Immersion-Wrangling/Task_1_Output/cleaned_data.csv

# Task 3: Launch the interactive dashboard
cd ../Task-3-DeepDive-Interactive-Dashboard
npm install
node server.js
# → Open http://localhost:8765/dashboard.html
```

---

<div align="center">

### 👨‍💻 Developed by [Hemang Dubey](https://www.linkedin.com/in/hemang-dubey-7b801628b/)

*Apex Planet Data Analytics Internship — 2026*

</div>
