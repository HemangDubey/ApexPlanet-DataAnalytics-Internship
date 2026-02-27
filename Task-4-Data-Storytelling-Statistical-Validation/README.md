# 📊 Task 4 — Data Storytelling & Statistical Validation

## Overview
This deliverable transforms the raw analytical findings from **Task 3 (Deep-Dive Analysis & Interactive Dashboarding)** into a structured, executive-ready business narrative. It bridges the gap between data exploration and strategic decision-making by presenting insights as a compelling story, supplemented with rigorous statistical testing.

---

## 📂 Deliverables

| # | File | Description |
|---|------|-------------|
| 1 | [Data_Story_Report.pdf](Data_Story_Report.pdf) | Complete **Data Story Report** — converts dashboard analysis into a business narrative with sections covering Executive Summary, Business Problem, KPI Definitions, Deep-Dive Analysis, Key Insights, Business Impact, Strategic Recommendations, and Conclusion. |
| 2 | [Data_Insights_Report.pdf](Data_Insights_Report.pdf) | A focused **Data Insights** document presenting the most impactful findings from the retail dataset, organized for stakeholder consumption. |
| 3 | [Hypothesis_Testing.md](Hypothesis_Testing.md) | A professional **Hypothesis Testing** section using a Chi-Square Test to statistically validate the relationship between order cancellations and customer churn. |

---

## 📑 Data Story Report — Structure

The main report follows a 9-section executive narrative format:

1. **Executive Summary** — High-level overview of £20.48M revenue, 5,878 customers, 50.9% churn rate
2. **Business Problem Statement** — Why the organization faces profitability ceilings despite top-line growth
3. **Dataset Overview** — 40,078 orders across 43 countries over 24 months
4. **KPI Definitions** — Total Revenue, AOV (£510.92), CLV (£1,699), Retention Rate (49.1%), Churn Rate (50.9%), Cancellation Rate (2.18%)
5. **Deep-Dive Analysis Summary** — Pareto distribution, geographic concentration (UK-dominant), time-series peaks
6. **Key Insights** — 6 data-driven findings including Pareto dependency, churn vulnerability, and cancellation impact
7. **Business Impact** — Simulation Lab projections: +115% revenue growth with 10% price optimization + 15% monthly growth
8. **Strategic Recommendations** — 5 actionable strategies (VIP retention, reactivation campaigns, peak-hour flash sales, catalog pruning, fulfillment audit)
9. **Conclusion** — Shift from acquisition to retention for compounding growth

---

## 🧪 Hypothesis Testing — Summary

### Research Question
> *Does experiencing an order cancellation significantly increase a customer's probability of churning?*

### Hypothesis
| | Statement |
|---|---|
| **H₀** | Customer churn is independent of order cancellation experience |
| **H₁** | Customers with cancellations churn at a significantly higher rate |

### Test & Results

| Metric | Value |
|--------|-------|
| **Test Used** | Pearson's Chi-Square (χ²) Test for Independence |
| **Population** | 5,878 unique customers |
| **χ² Statistic** | 214.63 |
| **p-value** | < 0.00001 |
| **Significance (α)** | 0.05 |
| **Decision** | ❌ **Reject H₀** — Cancellations and churn are statistically dependent |

### Key Finding
Customers who experienced a cancellation churn at **82.3%**, compared to **48.1%** for those with seamless fulfillment — a **34.2 percentage point** difference that is statistically significant beyond any reasonable doubt.

### Business Implication
The £1.46M lost to cancellations is only the surface-level impact. The downstream churn acceleration makes fulfillment optimization the single highest-ROI investment the business can make.

---

## 🔗 Connection to Other Tasks

| Task | Relationship |
|------|-------------|
| **Task 1** — Data Immersion & Wrangling | Cleaned dataset used as the foundation for all analysis |
| **Task 2** — Exploratory Data Analysis | Initial EDA patterns (revenue, segmentation) that guided the deep-dive |
| **Task 3** — Deep-Dive Analysis & Dashboarding | Interactive dashboard providing the KPIs, charts, and simulation results referenced throughout this report |
| **Task 4** — Data Storytelling *(this task)* | Converts all findings into an executive-ready narrative with statistical validation |

---

## 🛠️ Tools & Technologies Used
- **Dashboard Platform:** GravityBI (Custom Vanilla HTML/CSS/JS + Node.js + Express)
- **AI Engine:** H.O.N.E.Y (Groq API — Llama 3 70B)
- **Simulation Engine:** Custom 12-month revenue projector with compound growth/churn modeling
- **Statistical Testing:** Chi-Square Test for Independence (scipy.stats)
- **Data Processing:** Python (Pandas, NumPy)

---

*Developed as part of the Apex Planet Data Analytics Internship by Hemang Dubey.*
