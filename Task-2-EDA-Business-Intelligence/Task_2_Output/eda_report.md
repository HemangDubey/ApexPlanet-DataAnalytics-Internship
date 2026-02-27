# Exploratory Data Analysis Report

> Generated on `2026-02-27 16:47:44`

---

## 1. Dataset Overview

| Metric | Value |
|--------|-------|
| Total Rows | 1,033,036 |
| Total Columns | 12 |
| Date Range | 2009-12-01 to 2011-12-09 |
| Unique Products | 5,655 |
| Unique Customers | 5,942 |
| Countries | 43 |

## 2. Key Performance Indicators

| KPI | Value |
|-----|-------|
| Total Revenue | £20,476,634.02 |
| Total Orders | 40,078 |
| Avg Order Value | £510.92 |
| Avg Revenue per Customer | £3,483.61 |
| Cancellation Rate | 2.18% |

## 3. Key Insights

### Revenue Distribution
- Revenue is **heavily right-skewed** (skewness: 608.61)
- Median transaction value: £10.08 vs Mean: £20.32
- Top 10% of transactions account for a disproportionate share of revenue

### Geographic Analysis
- **United Kingdom** dominates with ~85% of total revenue
- 43 countries served in total

### Temporal Patterns
- Peak shopping hours: 10 AM - 3 PM
- Thursday shows the highest order volume
- Revenue tends to peak in November (pre-holiday season)

## 4. Visualizations Generated

| # | Chart | Description |
|---|-------|-------------|
| 1 | Revenue & Quantity Distribution | Histograms showing transaction distributions |
| 2 | Top 10 Countries by Revenue | Horizontal bar chart of geographic revenue |
| 3 | Top 10 Products by Volume | Best-selling products by quantity |
| 4 | Monthly Revenue Trend | Time series of monthly revenue |
| 5 | Orders by Day of Week | Weekly shopping patterns |
| 6 | Price Distribution | Box plot of price ranges |
| 7 | Correlation Heatmap | Numerical feature correlations |
| 8 | Revenue vs Quantity Scatter | Country-level relationship analysis |
| 9 | Year x Month Revenue Heatmap | Seasonal revenue patterns |
| 10 | Hourly Sales Pattern | Dual-axis hourly analysis |
| 11 | Pairwise Scatter Plots | Multi-variable relationships |

## 5. Dashboard KPIs Proposed

| KPI | Purpose | Update Frequency |
|-----|---------|-----------------|
| Total Revenue | Track overall business health | Daily |
| Order Count | Monitor transaction volume | Daily |
| Avg Order Value | Track basket size trends | Weekly |
| Customer Count | Active customer monitoring | Weekly |
| Revenue by Country | Geographic performance | Monthly |
| Top Products | Product performance tracking | Weekly |
| Cancellation Rate | Quality/returns monitoring | Daily |
| Revenue per Customer | Customer value tracking | Monthly |

---
*End of EDA Report*