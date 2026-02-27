<div align="center">
  
# 🚀 Apex Planet — Data Analytics Internship

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

### [`Task 1` — Data Immersion & Wrangling](https://github.com/HemangDubey/ApexPlanet-DataAnalytics-Internship/tree/main/Task-1-Data-Immersion-Wrangling)

> *Transform raw, messy data into a clean, analysis-ready dataset.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Ingest raw retail data, profile quality issues, clean & transform, engineer features |
| **Key Deliverables** | Production-grade Python CLI tool (`GravityWrangler`), cleaned dataset, auto-generated data dictionary |
| **Techniques** | Missing value imputation, duplicate removal, snake_case standardization, IQR outlier detection, datetime feature engineering |
| **Output** | `cleaned_data.csv` + `data_dictionary.md` |

---

### [`Task 2` — Exploratory Data Analysis & Business Intelligence](https://github.com/HemangDubey/ApexPlanet-DataAnalytics-Internship/tree/main/Task-2-EDA-Business-Intelligence)

> *Uncover hidden patterns through statistical analysis & SQL-powered business questions.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Perform univariate/bivariate/multivariate analysis, answer 7 SQL business questions, build static KPI dashboard |
| **Key Deliverables** | Python EDA engine (`GravityEDA`), 10+ publication-quality charts, SQL query results, dashboard mockup PNG |
| **Techniques** | Descriptive statistics, revenue distributions, correlation heatmaps, customer segmentation, SQLite-powered queries |
| **Output** | Charts directory, `eda_report.md`, `sql_results/`, `dashboard_mockup.png` |

---

### [`Task 3` — Deep-Dive Analysis & Interactive Dashboarding + AI Modules](https://github.com/HemangDubey/ApexPlanet-DataAnalytics-Internship/tree/main/Task-3-DeepDive-Interactive-Dashboard)

> *A full-stack, AI-powered interactive BI platform with 8 dashboard modules.*

| Aspect | Detail |
|--------|--------|
| **Objective** | Build a production-ready interactive dashboard with deep analytics, predictive simulation, and AI chatbot |
| **Key Deliverables** | Custom SPA dashboard (Vanilla HTML/CSS/JS), Node.js/Express backend, Groq AI integration |
| **Dashboard Modules** | Overview KPIs, Deep EDA, Cohort & RFM Segmentation, SQL Queries, Strategic Insights, KPI Reference, CSV Engine, Simulation Lab |
| **AI Features** | 🍯 **H.O.N.E.Y** chatbot (Llama 3 70B via Groq), 🧪 Business Simulation Lab, 📁 Dynamic CSV Engine |

**Tech Stack:** `HTML5` · `CSS3 (Glassmorphism)` · `JavaScript ES6+` · `Chart.js` · `Node.js` · `Express` · `Groq SDK` · `PapaParse`

---

### [`Task 4` — Data Storytelling & Statistical Validation](https://github.com/HemangDubey/ApexPlanet-DataAnalytics-Internship/tree/main/Task-4-Data-Storytelling-Statistical-Validation)

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
git clone https://github.com/HemangDubey/ApexPlanet-DataAnalytics-Internship.git
cd ApexPlanet-DataAnalytics-Internship

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
