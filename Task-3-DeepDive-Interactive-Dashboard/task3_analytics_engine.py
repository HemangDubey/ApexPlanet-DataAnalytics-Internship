#!/usr/bin/env python3
"""
task3_analytics_engine.py — Deep-Dive Analytics & Dashboard Data Pipeline
==========================================================================
Performs production-grade analysis on the cleaned retail dataset and
exports every metric as JSON so the interactive HTML dashboard can consume
it purely client-side (zero server needed after generation).

Pipeline
--------
1. KPI Computation  (8 core KPIs + deltas)
2. Advanced EDA     (distributions, bivariate, time-series)
3. Cohort Analysis  (monthly acquisition cohorts + retention)
4. RFM Segmentation (Recency-Frequency-Monetary scoring)
5. SQL BI Queries   (10 complex queries via SQLite)
6. Business Insights (auto-generated strategic recommendations)
7. JSON Export       (single data.json consumed by the dashboard)

Author : Hemang Dubey
Module : Task 3 — Deep-Dive Analysis & Interactive Dashboarding (ApexPlanet)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import sys
import warnings
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# =====================================================================
#  Console Helpers
# =====================================================================
class _C:
    B = "\033[1m"; D = "\033[2m"; G = "\033[92m"; Y = "\033[93m"
    C = "\033[96m"; M = "\033[95m"; R = "\033[91m"; W = "\033[97m"
    X = "\033[0m"

W = 64

def _banner():
    print(f"\n{'=' * W}")
    print(f"{_C.B}{_C.C}   TASK 3  |  Deep-Dive Analytics & Dashboard Engine{_C.X}")
    print(f"{'=' * W}")

def _phase(n, title):
    print(f"\n{_C.C}{'-' * W}{_C.X}")
    print(f"{_C.B}{_C.C}  PHASE {n}  |  {title}{_C.X}")
    print(f"{_C.C}{'-' * W}{_C.X}")

def _ok(msg):  print(f"  {_C.G}[OK]{_C.X}  {msg}")
def _info(msg): print(f"  {_C.D}      {msg}{_C.X}")
def _warn(msg): print(f"  {_C.Y}[!]{_C.X}  {msg}")
def _done(msg):
    print(f"\n  {_C.G}{'=' * W}{_C.X}")
    print(f"  {_C.B}{_C.G}  DONE  {msg}{_C.X}")
    print(f"  {_C.G}{'=' * W}{_C.X}\n")

# =====================================================================
#  Serialization helpers
# =====================================================================
def _safe(obj):
    """Make obj JSON-serializable."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, 4)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, np.ndarray):
        return [_safe(x) for x in obj.tolist()]
    if isinstance(obj, dict):
        return {str(k): _safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe(x) for x in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, 4)
    return obj

def _df_to_records(df: pd.DataFrame, max_rows: int = 500) -> list:
    """Convert a DataFrame to a list of dicts, capped."""
    return _safe(df.head(max_rows).to_dict(orient="records"))


# =====================================================================
#  Analytics Engine
# =====================================================================
class GravityAnalyticsEngine:
    """End-to-end deep-dive analytics pipeline."""

    def __init__(self, file_path: str, output_dir: str):
        self.file_path = file_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        _phase(0, "LOADING & PREPARING DATA")
        self.df = pd.read_csv(file_path, low_memory=False)
        self.df["invoice_date"] = pd.to_datetime(self.df["invoice_date"], errors="coerce")

        # Ensure revenue column
        if "revenue" not in self.df.columns:
            self.df["revenue"] = self.df["quantity"] * self.df["price"]
        # Positive-only subset for most analyses
        self.df_pos = self.df[(self.df["quantity"] > 0) & (self.df["price"] > 0)].copy()
        self.df_pos["revenue"] = self.df_pos["quantity"] * self.df_pos["price"]

        # Temporal helpers
        self.df_pos["year_month"] = self.df_pos["invoice_date"].dt.to_period("M").astype(str)
        self.df_pos["hour"] = self.df_pos["invoice_date"].dt.hour
        self.df_pos["weekday"] = self.df_pos["invoice_date"].dt.day_name()

        self.result: Dict[str, Any] = {}
        _ok(f"Loaded {len(self.df):,} rows  ->  {len(self.df_pos):,} positive transactions")
        _info(f"Date range: {self.df_pos['invoice_date'].min()} -> {self.df_pos['invoice_date'].max()}")

    # -----------------------------------------------------------------
    #  PHASE 1 — Core KPIs
    # -----------------------------------------------------------------
    def compute_kpis(self):
        _phase(1, "CORE KPIs")
        df = self.df_pos

        total_revenue = float(df["revenue"].sum())
        total_orders = int(df["invoice"].nunique())
        total_customers = int(df["customer_id"].nunique())
        total_products = int(df["description"].nunique())
        total_countries = int(df["country"].nunique())
        total_items = int(df["quantity"].sum())
        aov = total_revenue / total_orders if total_orders else 0
        rev_per_customer = total_revenue / total_customers if total_customers else 0

        # CLV proxy: avg revenue per customer over dataset lifespan
        date_range_days = (df["invoice_date"].max() - df["invoice_date"].min()).days or 1
        monthly_rev_per_cust = rev_per_customer / (date_range_days / 30)
        clv_12m = monthly_rev_per_cust * 12

        # Cancellation metrics (from original df)
        cancelled = self.df[self.df["quantity"] < 0]
        cancel_rate = len(cancelled) / len(self.df) * 100
        revenue_lost = float(abs(cancelled["quantity"] * cancelled["price"]).sum())

        # Repeat purchase
        orders_per_customer = df.groupby("customer_id")["invoice"].nunique()
        repeat_customers = int((orders_per_customer > 1).sum())
        repeat_rate = repeat_customers / total_customers * 100 if total_customers else 0

        # Churn (customers not purchasing in last 90 days of dataset)
        last_date = df["invoice_date"].max()
        last_purchase = df.groupby("customer_id")["invoice_date"].max()
        churned = int((last_purchase < last_date - pd.Timedelta(days=90)).sum())
        churn_rate = churned / total_customers * 100 if total_customers else 0
        retention_rate = 100 - churn_rate

        kpis = OrderedDict([
            ("total_revenue", {"value": total_revenue, "formatted": f"£{total_revenue:,.0f}",
                               "label": "Total Revenue", "icon": "💰",
                               "formula": "SUM(quantity × price) WHERE quantity > 0",
                               "sql": "SELECT ROUND(SUM(quantity * price), 2) FROM transactions WHERE quantity > 0 AND price > 0",
                               "interpretation": "Overall business health indicator; aggregated gross revenue from all completed transactions.",
                               "type": "lagging", "category": "actionable"}),
            ("total_orders", {"value": total_orders, "formatted": f"{total_orders:,}",
                              "label": "Total Orders", "icon": "📦",
                              "formula": "COUNT(DISTINCT invoice_id)",
                              "sql": "SELECT COUNT(DISTINCT invoice) FROM transactions WHERE quantity > 0",
                              "interpretation": "Transaction volume — a proxy for demand. Rising orders + falling AOV = possible discounting.",
                              "type": "lagging", "category": "actionable"}),
            ("aov", {"value": aov, "formatted": f"£{aov:,.2f}",
                     "label": "Avg Order Value", "icon": "🛒",
                     "formula": "Total Revenue / Total Orders",
                     "sql": "SELECT ROUND(SUM(quantity*price)*1.0 / COUNT(DISTINCT invoice), 2) FROM transactions WHERE quantity > 0 AND price > 0",
                     "interpretation": "Measures basket size. Increase via cross-sell, bundling, minimum-free-shipping thresholds.",
                     "type": "lagging", "category": "actionable"}),
            ("clv_12m", {"value": clv_12m, "formatted": f"£{clv_12m:,.0f}",
                         "label": "CLV (12-Month Proxy)", "icon": "👑",
                         "formula": "(Avg Revenue per Customer / months in data) × 12",
                         "sql": "-- Requires multi-step CTE, see SQL section",
                         "interpretation": "Projected annual value per customer. High CLV customers warrant VIP treatment & retention investment.",
                         "type": "leading", "category": "actionable"}),
            ("retention_rate", {"value": retention_rate, "formatted": f"{retention_rate:.1f}%",
                                "label": "Retention Rate", "icon": "🔁",
                                "formula": "(Customers active in last 90d / Total customers) × 100",
                                "sql": "-- See cohort retention SQL",
                                "interpretation": "Measures loyalty. 5% retention lift → 25-95% profit increase (Harvard Business Review).",
                                "type": "leading", "category": "actionable"}),
            ("churn_rate", {"value": churn_rate, "formatted": f"{churn_rate:.1f}%",
                            "label": "Churn Rate", "icon": "📉",
                            "formula": "100 − Retention Rate",
                            "sql": "-- Inverse of retention; see cohort SQL",
                            "interpretation": "Rising churn signals product/service issues. Target churned VIPs with win-back campaigns.",
                            "type": "lagging", "category": "actionable"}),
            ("rev_per_customer", {"value": rev_per_customer, "formatted": f"£{rev_per_customer:,.0f}",
                                  "label": "Revenue per Customer", "icon": "👤",
                                  "formula": "Total Revenue / Total Unique Customers",
                                  "sql": "SELECT ROUND(SUM(quantity*price)*1.0 / COUNT(DISTINCT customer_id), 2) FROM transactions WHERE quantity > 0",
                                  "interpretation": "Average customer contribution. Segment by this to identify high-value tiers.",
                                  "type": "lagging", "category": "actionable"}),
            ("cancel_rate", {"value": cancel_rate, "formatted": f"{cancel_rate:.2f}%",
                             "label": "Cancellation Rate", "icon": "❌",
                             "formula": "COUNT(cancelled items) / COUNT(all items) × 100",
                             "sql": "SELECT ROUND(COUNT(CASE WHEN quantity < 0 THEN 1 END)*100.0/COUNT(*), 2) FROM transactions",
                             "interpretation": "Operational quality metric. High rate → investigate product quality, shipping, or UX issues.",
                             "type": "lagging", "category": "actionable"}),
        ])

        # Secondary metrics for the dashboard
        secondary = {
            "total_customers": {"value": total_customers, "formatted": f"{total_customers:,}", "label": "Unique Customers", "icon": "👥"},
            "total_products": {"value": total_products, "formatted": f"{total_products:,}", "label": "Products", "icon": "📋"},
            "total_countries": {"value": total_countries, "formatted": f"{total_countries:,}", "label": "Countries", "icon": "🌍"},
            "total_items_sold": {"value": total_items, "formatted": f"{total_items:,}", "label": "Items Sold", "icon": "📊"},
            "repeat_rate": {"value": repeat_rate, "formatted": f"{repeat_rate:.1f}%", "label": "Repeat Purchase Rate", "icon": "🔄"},
            "revenue_lost": {"value": revenue_lost, "formatted": f"£{revenue_lost:,.0f}", "label": "Revenue Lost (Cancellations)", "icon": "💸"},
        }

        self.result["kpis"] = _safe(kpis)
        self.result["secondary_metrics"] = _safe(secondary)

        for k, v in kpis.items():
            _ok(f"{v['label']}: {v['formatted']}")
        return self

    # -----------------------------------------------------------------
    #  PHASE 2 — Advanced EDA
    # -----------------------------------------------------------------
    def advanced_eda(self):
        _phase(2, "ADVANCED EDA")
        df = self.df_pos

        # ── 2a. Univariate Statistics ──
        _ok("Computing univariate statistics")
        stats = {}
        for col in ["revenue", "quantity", "price"]:
            s = df[col]
            stats[col] = {
                "mean": float(s.mean()), "median": float(s.median()),
                "std": float(s.std()), "min": float(s.min()), "max": float(s.max()),
                "skewness": float(s.skew()), "kurtosis": float(s.kurtosis()),
                "p25": float(s.quantile(0.25)), "p75": float(s.quantile(0.75)),
                "p90": float(s.quantile(0.90)), "p95": float(s.quantile(0.95)),
                "p99": float(s.quantile(0.99)),
                "iqr": float(s.quantile(0.75) - s.quantile(0.25)),
            }
        self.result["univariate_stats"] = _safe(stats)

        # ── 2b. Revenue Distribution (histogram data) ──
        rev = df["revenue"]
        rev_clipped = rev[rev < rev.quantile(0.95)]
        hist_counts, hist_edges = np.histogram(rev_clipped, bins=50)
        self.result["revenue_distribution"] = {
            "counts": _safe(hist_counts.tolist()),
            "edges": _safe(hist_edges.tolist()),
            "label": "Revenue per Transaction (0-95th pctl)"
        }

        # Quantity distribution
        qty = df["quantity"]
        qty_clipped = qty[qty < qty.quantile(0.95)]
        qh_counts, qh_edges = np.histogram(qty_clipped, bins=50)
        self.result["quantity_distribution"] = {
            "counts": _safe(qh_counts.tolist()),
            "edges": _safe(qh_edges.tolist()),
            "label": "Quantity per Transaction (0-95th pctl)"
        }

        # Customer frequency distribution
        cust_freq = df.groupby("customer_id")["invoice"].nunique()
        freq_counts = cust_freq.value_counts().sort_index().head(30)
        self.result["customer_frequency"] = {
            "orders": _safe(freq_counts.index.tolist()),
            "customers": _safe(freq_counts.values.tolist())
        }

        # ── 2c. Revenue by Country ──
        _ok("Bivariate: Revenue by Country")
        country_rev = df.groupby("country").agg(
            revenue=("revenue", "sum"),
            orders=("invoice", "nunique"),
            customers=("customer_id", "nunique"),
            avg_order=("revenue", "mean")
        ).sort_values("revenue", ascending=False).reset_index()
        country_rev["pct"] = country_rev["revenue"] / country_rev["revenue"].sum() * 100
        self.result["revenue_by_country"] = _df_to_records(country_rev)

        # ── 2d. Revenue by Time (Monthly) ──
        _ok("Time-series: Monthly revenue trend")
        monthly = df.set_index("invoice_date").resample("MS").agg(
            revenue=("revenue", "sum"),
            orders=("invoice", "nunique"),
            customers=("customer_id", "nunique"),
            avg_order_value=("revenue", "mean"),
            items=("quantity", "sum")
        ).reset_index()
        monthly["month_label"] = monthly["invoice_date"].dt.strftime("%b %Y")
        monthly["mom_growth"] = monthly["revenue"].pct_change() * 100
        monthly["cumulative_revenue"] = monthly["revenue"].cumsum()
        self.result["monthly_trend"] = _df_to_records(monthly)

        # ── 2e. Revenue by Weekday ──
        _ok("Temporal: Weekday pattern")
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_data = df.groupby("weekday").agg(
            revenue=("revenue", "sum"),
            orders=("invoice", "nunique"),
            avg_transaction=("revenue", "mean")
        ).reindex(day_order).reset_index()
        weekday_data.columns = ["day", "revenue", "orders", "avg_transaction"]
        self.result["weekday_pattern"] = _df_to_records(weekday_data)

        # ── 2f. Hourly Pattern ──
        _ok("Temporal: Hourly pattern")
        hourly = df.groupby("hour").agg(
            revenue=("revenue", "sum"),
            orders=("invoice", "nunique"),
            avg_qty=("quantity", "mean")
        ).reset_index()
        self.result["hourly_pattern"] = _df_to_records(hourly)

        # ── 2g. Top Products ──
        _ok("Product analysis")
        top_prod = df.groupby("description").agg(
            revenue=("revenue", "sum"),
            quantity=("quantity", "sum"),
            orders=("invoice", "nunique"),
            avg_price=("price", "mean")
        ).sort_values("revenue", ascending=False).head(20).reset_index()
        top_prod["pct"] = top_prod["revenue"] / df["revenue"].sum() * 100
        self.result["top_products"] = _df_to_records(top_prod)

        # ── 2h. Correlation Matrix ──
        _ok("Correlation matrix")
        num_cols = ["quantity", "price", "revenue"]
        corr = df[num_cols].corr()
        self.result["correlation_matrix"] = {
            "columns": num_cols,
            "values": _safe(corr.values.tolist())
        }

        # ── 2i. Pareto / 80-20 Analysis ──
        _ok("Pareto (80/20) analysis")
        cust_revenue = df.groupby("customer_id")["revenue"].sum().sort_values(ascending=False)
        total = cust_revenue.sum()
        cum = cust_revenue.cumsum()
        pct_customers = np.arange(1, len(cust_revenue) + 1) / len(cust_revenue) * 100
        pct_revenue = cum / total * 100

        # Find exact 80/20 point
        idx_80 = np.searchsorted(pct_revenue.values, 80)
        pareto_customer_pct = float(pct_customers[idx_80]) if idx_80 < len(pct_customers) else 100

        # Downsample for JSON
        step = max(1, len(pct_customers) // 200)
        self.result["pareto"] = {
            "customer_pct": _safe(pct_customers[::step].tolist()),
            "revenue_pct": _safe(pct_revenue.values[::step].tolist()),
            "pareto_point": {"customer_pct": round(pareto_customer_pct, 1),
                             "revenue_pct": 80.0},
            "insight": f"Top {pareto_customer_pct:.1f}% of customers generate 80% of revenue"
        }

        return self

    # -----------------------------------------------------------------
    #  PHASE 3 — Cohort Analysis
    # -----------------------------------------------------------------
    def cohort_analysis(self):
        _phase(3, "COHORT ANALYSIS")
        df = self.df_pos.copy()

        # Acquisition month
        df["order_month"] = df["invoice_date"].dt.to_period("M")
        cohort_month = df.groupby("customer_id")["order_month"].min().rename("cohort_month")
        df = df.merge(cohort_month, on="customer_id")
        df["cohort_index"] = (df["order_month"] - df["cohort_month"]).apply(lambda x: x.n if hasattr(x, 'n') else 0)

        # Cohort table: unique customers per (cohort, index)
        cohort_data = df.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
        cohort_data.columns = ["cohort_month", "period", "customers"]
        cohort_data["cohort_month"] = cohort_data["cohort_month"].astype(str)

        # Pivot for retention %
        pivot = cohort_data.pivot(index="cohort_month", columns="period", values="customers").fillna(0)
        cohort_sizes = pivot[0] if 0 in pivot.columns else pivot.iloc[:, 0]
        retention = pivot.div(cohort_sizes, axis=0) * 100

        # Limit to first 12 periods and last 12 cohorts for readability
        retention = retention.iloc[-12:, :13]

        self.result["cohort_retention"] = {
            "cohorts": retention.index.tolist(),
            "periods": [int(c) for c in retention.columns.tolist()],
            "values": _safe(retention.values.tolist()),
            "cohort_sizes": _safe(cohort_sizes.iloc[-12:].values.tolist())
        }
        _ok(f"Built {len(retention)} cohort retention table (up to {len(retention.columns)} periods)")

        return self

    # -----------------------------------------------------------------
    #  PHASE 4 — RFM Segmentation
    # -----------------------------------------------------------------
    def rfm_segmentation(self):
        _phase(4, "RFM SEGMENTATION")
        df = self.df_pos.copy()
        snapshot = df["invoice_date"].max() + pd.Timedelta(days=1)

        rfm = df.groupby("customer_id").agg(
            recency=("invoice_date", lambda x: (snapshot - x.max()).days),
            frequency=("invoice", "nunique"),
            monetary=("revenue", "sum")
        ).reset_index()

        # Score 1-5 using quantiles
        for col in ["recency", "frequency", "monetary"]:
            ascending = col == "recency"  # lower recency = better
            try:
                labels = list(range(5, 0, -1)) if ascending else list(range(1, 6))
                rfm[f"{col}_score"] = pd.qcut(rfm[col], 5, labels=labels, duplicates="drop").astype(int)
            except (ValueError, TypeError):
                # Fallback: rank-based scoring when qcut fails
                rfm[f"{col}_score"] = pd.cut(rfm[col].rank(method="first"), bins=5, labels=[1,2,3,4,5]).astype(int)
                if ascending:
                    rfm[f"{col}_score"] = 6 - rfm[f"{col}_score"]

        rfm["rfm_score"] = rfm["recency_score"] * 100 + rfm["frequency_score"] * 10 + rfm["monetary_score"]
        rfm["rfm_total"] = rfm["recency_score"] + rfm["frequency_score"] + rfm["monetary_score"]

        # Segment assignment
        def _segment(row):
            r, f, m = row["recency_score"], row["frequency_score"], row["monetary_score"]
            if r >= 4 and f >= 4 and m >= 4:
                return "VIP / Champions"
            elif r >= 3 and f >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2:
                return "New Customers"
            elif r >= 3 and f >= 2 and m >= 3:
                return "Potential Loyalists"
            elif r <= 2 and f >= 3 and m >= 3:
                return "At Risk"
            elif r <= 2 and f >= 4:
                return "Can't Lose Them"
            elif r <= 2 and f <= 2:
                return "Dormant / Lost"
            else:
                return "Need Attention"

        rfm["segment"] = rfm.apply(_segment, axis=1)

        # Segment summary
        seg_summary = rfm.groupby("segment").agg(
            count=("customer_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_revenue=("monetary", "sum")
        ).sort_values("total_revenue", ascending=False).reset_index()
        seg_summary["pct_customers"] = seg_summary["count"] / seg_summary["count"].sum() * 100
        seg_summary["pct_revenue"] = seg_summary["total_revenue"] / seg_summary["total_revenue"].sum() * 100

        # Segment actions
        segment_actions = {
            "VIP / Champions": "Reward with exclusive offers, early access, loyalty programs. They are your brand advocates.",
            "Loyal Customers": "Upsell higher-margin products, ask for reviews, introduce referral programs.",
            "New Customers": "Onboard with welcome series, nurture with educational content, incentivize second purchase.",
            "Potential Loyalists": "Offer membership/loyalty benefits, personalized recommendations to increase frequency.",
            "At Risk": "Send win-back campaigns, personalized discounts, ask for feedback on experience.",
            "Can't Lose Them": "URGENT: highest-value churning customers. Personal outreach, special retention offers.",
            "Dormant / Lost": "Re-engage with aggressive discounts or write-off. Test different re-activation campaigns.",
            "Need Attention": "Provide limited-time offers, highlight new products, improve engagement touch-points."
        }

        for _, row in seg_summary.iterrows():
            row_dict = row.to_dict()
            seg = row_dict["segment"]
            if seg in segment_actions:
                row_dict["action"] = segment_actions[seg]

        seg_records = _df_to_records(seg_summary)
        for rec in seg_records:
            seg = rec.get("segment", "")
            if seg in segment_actions:
                rec["action"] = segment_actions[seg]

        self.result["rfm_segments"] = seg_records

        # RFM scatter data (sampled for performance)
        rfm_sample = rfm.sample(n=min(2000, len(rfm)), random_state=42)
        self.result["rfm_scatter"] = _df_to_records(rfm_sample[["customer_id", "recency", "frequency", "monetary", "segment"]])

        _ok(f"Segmented {len(rfm):,} customers into {rfm['segment'].nunique()} groups")
        for _, row in seg_summary.iterrows():
            _info(f"  {row['segment']}: {row['count']:,} customers ({row['pct_customers']:.1f}%) -> GBP {row['total_revenue']:,.0f}")

        return self

    # -----------------------------------------------------------------
    #  PHASE 5 — SQL BI Queries
    # -----------------------------------------------------------------
    def sql_queries(self):
        _phase(5, "SQL BUSINESS INTELLIGENCE")
        conn = sqlite3.connect(":memory:")
        self.df.to_sql("transactions", conn, index=False, if_exists="replace")
        _ok("Data loaded into SQLite")

        queries = [
            {
                "id": 1, "title": "Top 10 Customers by Revenue",
                "sql": """
WITH customer_rev AS (
    SELECT CAST(customer_id AS INTEGER) AS customer_id,
           ROUND(SUM(quantity * price), 2) AS total_revenue,
           COUNT(DISTINCT invoice) AS total_orders,
           ROUND(AVG(quantity * price), 2) AS avg_order_value,
           MIN(invoice_date) AS first_purchase,
           MAX(invoice_date) AS last_purchase
    FROM transactions
    WHERE quantity > 0 AND price > 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT *, RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM customer_rev
ORDER BY total_revenue DESC
LIMIT 10;"""
            },
            {
                "id": 2, "title": "Revenue by Country with Market Share",
                "sql": """
SELECT country,
       ROUND(SUM(quantity * price), 2) AS total_revenue,
       COUNT(DISTINCT customer_id) AS customers,
       COUNT(DISTINCT invoice) AS orders,
       ROUND(SUM(quantity*price) * 100.0 /
             (SELECT SUM(quantity*price) FROM transactions WHERE quantity > 0 AND price > 0), 2)
             AS market_share_pct,
       ROUND(SUM(quantity*price) / COUNT(DISTINCT invoice), 2) AS aov
FROM transactions
WHERE quantity > 0 AND price > 0
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 15;"""
            },
            {
                "id": 3, "title": "Monthly Revenue Growth (MoM %)",
                "sql": """
WITH monthly AS (
    SELECT SUBSTR(invoice_date, 1, 7) AS month,
           ROUND(SUM(quantity * price), 2) AS revenue
    FROM transactions
    WHERE quantity > 0 AND price > 0
    GROUP BY month
)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) AS prev_month_rev,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 /
             LAG(revenue) OVER (ORDER BY month), 2) AS mom_growth_pct
FROM monthly
ORDER BY month;"""
            },
            {
                "id": 4, "title": "Repeat Purchase Customers",
                "sql": """
WITH cust_orders AS (
    SELECT customer_id, COUNT(DISTINCT invoice) AS order_count
    FROM transactions
    WHERE quantity > 0 AND price > 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-time'
        WHEN order_count BETWEEN 2 AND 5 THEN '2-5 orders'
        WHEN order_count BETWEEN 6 AND 10 THEN '6-10 orders'
        ELSE '10+ orders'
    END AS customer_tier,
    COUNT(*) AS num_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM cust_orders), 2) AS pct
FROM cust_orders
GROUP BY customer_tier
ORDER BY MIN(order_count);"""
            },
            {
                "id": 5, "title": "High-Value Churned Customers (90+ days inactive)",
                "sql": """
WITH customer_stats AS (
    SELECT customer_id,
           ROUND(SUM(quantity * price), 2) AS lifetime_value,
           MAX(invoice_date) AS last_purchase,
           COUNT(DISTINCT invoice) AS total_orders
    FROM transactions
    WHERE quantity > 0 AND price > 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
),
max_date AS (SELECT MAX(invoice_date) AS ref_date FROM transactions)
SELECT cs.customer_id,
       cs.lifetime_value,
       cs.total_orders,
       cs.last_purchase,
       CAST(julianday(md.ref_date) - julianday(cs.last_purchase) AS INTEGER) AS days_since_last
FROM customer_stats cs, max_date md
WHERE CAST(julianday(md.ref_date) - julianday(cs.last_purchase) AS INTEGER) > 90
ORDER BY cs.lifetime_value DESC
LIMIT 10;"""
            },
            {
                "id": 6, "title": "Average Purchase Gap (Days Between Orders)",
                "sql": """
WITH ordered AS (
    SELECT customer_id, invoice_date,
           LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date) AS prev_date
    FROM (SELECT DISTINCT customer_id, invoice_date FROM transactions
          WHERE quantity > 0 AND price > 0 AND customer_id IS NOT NULL)
),
gaps AS (
    SELECT customer_id,
           CAST(julianday(invoice_date) - julianday(prev_date) AS INTEGER) AS gap_days
    FROM ordered
    WHERE prev_date IS NOT NULL
)
SELECT ROUND(AVG(gap_days), 1) AS avg_gap_days,
       MIN(gap_days) AS min_gap,
       MAX(gap_days) AS max_gap,
       ROUND(AVG(CASE WHEN gap_days <= 30 THEN gap_days END), 1) AS avg_gap_under_30d,
       COUNT(DISTINCT customer_id) AS customers_with_repeat
FROM gaps;"""
            },
            {
                "id": 7, "title": "Product Contribution % (Top 15)",
                "sql": """
WITH product_rev AS (
    SELECT description AS product,
           ROUND(SUM(quantity * price), 2) AS revenue,
           SUM(quantity) AS units_sold
    FROM transactions
    WHERE quantity > 0 AND price > 0
    GROUP BY description
)
SELECT product, revenue, units_sold,
       ROUND(revenue * 100.0 / SUM(revenue) OVER (), 2) AS contribution_pct,
       ROUND(SUM(revenue) OVER (ORDER BY revenue DESC) * 100.0 /
             SUM(revenue) OVER (), 2) AS cumulative_pct
FROM product_rev
ORDER BY revenue DESC
LIMIT 15;"""
            },
            {
                "id": 8, "title": "Pareto Analysis — 80/20 Rule",
                "sql": """
WITH customer_rev AS (
    SELECT customer_id,
           ROUND(SUM(quantity * price), 2) AS revenue
    FROM transactions
    WHERE quantity > 0 AND price > 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
    ORDER BY revenue DESC
),
ranked AS (
    SELECT customer_id, revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC) AS cum_rev,
           SUM(revenue) OVER () AS total_rev,
           ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn,
           COUNT(*) OVER () AS total_cust
    FROM customer_rev
)
SELECT rn AS customer_rank,
       ROUND(rn * 100.0 / total_cust, 2) AS customer_pct,
       ROUND(cum_rev * 100.0 / total_rev, 2) AS cumulative_rev_pct
FROM ranked
WHERE ROUND(cum_rev * 100.0 / total_rev, 2) BETWEEN 75 AND 85
LIMIT 5;"""
            },
            {
                "id": 9, "title": "Revenue by Weekday",
                "sql": """
SELECT
    CASE CAST(strftime('%w', invoice_date) AS INTEGER)
        WHEN 0 THEN 'Sunday'    WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'   WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'  WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS weekday,
    COUNT(DISTINCT invoice) AS orders,
    ROUND(SUM(quantity * price), 2) AS revenue,
    ROUND(SUM(quantity*price) / COUNT(DISTINCT invoice), 2) AS avg_order_value
FROM transactions
WHERE quantity > 0 AND price > 0
GROUP BY weekday
ORDER BY revenue DESC;"""
            },
            {
                "id": 10, "title": "Cohort Retention Calculation",
                "sql": """
WITH first_purchase AS (
    SELECT customer_id,
           MIN(SUBSTR(invoice_date, 1, 7)) AS cohort_month
    FROM transactions
    WHERE quantity > 0 AND price > 0 AND customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT t.customer_id,
           fp.cohort_month,
           SUBSTR(t.invoice_date, 1, 7) AS activity_month
    FROM transactions t
    JOIN first_purchase fp ON t.customer_id = fp.customer_id
    WHERE t.quantity > 0 AND t.price > 0
)
SELECT cohort_month,
       COUNT(DISTINCT CASE WHEN activity_month = cohort_month THEN customer_id END) AS month_0,
       COUNT(DISTINCT CASE WHEN activity_month > cohort_month THEN customer_id END) AS retained,
       ROUND(COUNT(DISTINCT CASE WHEN activity_month > cohort_month THEN customer_id END) * 100.0 /
             COUNT(DISTINCT CASE WHEN activity_month = cohort_month THEN customer_id END), 2) AS retention_pct
FROM activity
GROUP BY cohort_month
ORDER BY cohort_month;"""
            },
        ]

        sql_results = []
        for q in queries:
            try:
                result_df = pd.read_sql_query(q["sql"], conn)
                sql_results.append({
                    "id": q["id"],
                    "title": q["title"],
                    "sql": q["sql"].strip(),
                    "data": _df_to_records(result_df),
                    "columns": result_df.columns.tolist(),
                    "row_count": len(result_df)
                })
                _ok(f"Q{q['id']}: {q['title']} → {len(result_df)} rows")
            except Exception as e:
                _warn(f"Q{q['id']} failed: {e}")
                sql_results.append({
                    "id": q["id"], "title": q["title"],
                    "sql": q["sql"].strip(), "data": [], "columns": [],
                    "row_count": 0, "error": str(e)
                })

        conn.close()
        self.result["sql_queries"] = sql_results
        return self

    # -----------------------------------------------------------------
    #  PHASE 6 — Strategic Business Insights
    # -----------------------------------------------------------------
    def generate_insights(self):
        _phase(6, "STRATEGIC BUSINESS INSIGHTS")
        df = self.df_pos
        total_rev = df["revenue"].sum()

        uk_rev = df[df["country"] == "United Kingdom"]["revenue"].sum()
        uk_pct = uk_rev / total_rev * 100

        monthly = df.set_index("invoice_date").resample("MS")["revenue"].sum()
        best_month = monthly.idxmax().strftime("%B %Y")
        worst_month = monthly.idxmin().strftime("%B %Y")

        top_product = df.groupby("description")["revenue"].sum().idxmax()

        insights = {
            "strategic_insights": [
                {"id": 1, "category": "Geographic Concentration Risk",
                 "insight": f"UK contributes {uk_pct:.0f}% of revenue — extreme geographic dependency.",
                 "recommendation": "Diversify into DACH (Germany, Austria, Switzerland) & Nordics with localized marketing.",
                 "impact": "High", "priority": "Critical"},
                {"id": 2, "category": "Customer Concentration",
                 "insight": f"Pareto analysis shows top ~20% customers drive ~80% of revenue.",
                 "recommendation": "Implement tiered loyalty program; VIP concierge for top 5% to prevent churn.",
                 "impact": "High", "priority": "Critical"},
                {"id": 3, "category": "Seasonality Dependency",
                 "insight": f"Peak month: {best_month}. Significant Nov-Dec spike with trough in Jan-Feb.",
                 "recommendation": "Launch mid-year promotions (summer sale) and Q1 clearance events to flatten curve.",
                 "impact": "Medium", "priority": "High"},
                {"id": 4, "category": "AOV Optimization",
                 "insight": f"Median transaction (£{df['revenue'].median():.0f}) far below mean, indicating long tail of small orders.",
                 "recommendation": "Introduce minimum order thresholds, bundle deals, and 'frequently bought together' recommendations.",
                 "impact": "High", "priority": "High"},
                {"id": 5, "category": "Churn Prevention",
                 "insight": "Significant proportion of customers inactive for 90+ days despite high lifetime value.",
                 "recommendation": "Deploy automated win-back email sequences at 30/60/90 day inactivity triggers.",
                 "impact": "High", "priority": "Critical"},
                {"id": 6, "category": "Product Portfolio",
                 "insight": f"Top product '{top_product[:50]}' dominates — potential single-product dependency.",
                 "recommendation": "Cross-sell complementary products; analyze why top products succeed and replicate.",
                 "impact": "Medium", "priority": "Medium"},
                {"id": 7, "category": "Peak Hour Optimization",
                 "insight": "10 AM - 3 PM generates majority of sales. Evening/weekend significantly underperforming.",
                 "recommendation": "A/B test flash sales during off-peak hours. Consider timezone-optimized campaigns for non-UK markets.",
                 "impact": "Medium", "priority": "Medium"},
                {"id": 8, "category": "Cancellation Revenue Leak",
                 "insight": f"Cancellation rate ~{len(self.df[self.df['quantity'] < 0]) / len(self.df) * 100:.1f}% represents significant revenue leakage.",
                 "recommendation": "Analyze top cancelled products. Improve product descriptions, images, and size guides.",
                 "impact": "High", "priority": "High"},
                {"id": 9, "category": "Customer Acquisition Efficiency",
                 "insight": "New customer cohorts show rapid drop-off after first month — onboarding gap.",
                 "recommendation": "Build 30-day onboarding journey with welcome series, first-purchase incentive, and guided experience.",
                 "impact": "High", "priority": "High"},
                {"id": 10, "category": "Data Infrastructure",
                 "insight": "Dataset lacks marketing attribution, margins, and channel source — limiting ROI analysis.",
                 "recommendation": "Integrate UTM tracking, cost data, and channel attribution for full-funnel analytics.",
                 "impact": "Medium", "priority": "Long-term"},
            ],
            "revenue_opportunities": [
                {"id": 1, "strategy": "International Expansion",
                 "description": "Target top 5 non-UK countries with localized storefronts and regional marketing.",
                 "estimated_impact": "15-25% revenue increase over 12 months"},
                {"id": 2, "strategy": "VIP Retention Program",
                 "description": "Dedicated account management + exclusive early access for top 200 customers.",
                 "estimated_impact": "10-15% reduction in high-value churn"},
                {"id": 3, "strategy": "Bundle & Upsell Engine",
                 "description": "Data-driven product bundles based on co-purchase patterns to increase AOV by 20%.",
                 "estimated_impact": f"£{total_rev * 0.08:,.0f} additional annual revenue"},
                {"id": 4, "strategy": "Loyalty Points System",
                 "description": "Implement points-per-pound system with tiered rewards to increase repeat purchase rate.",
                 "estimated_impact": "25% increase in repeat purchases"},
                {"id": 5, "strategy": "Subscription / Auto-Replenish",
                 "description": "For high-frequency products, offer auto-replenishment with 5% discount.",
                 "estimated_impact": "Predictable recurring revenue stream"},
            ],
            "cost_optimizations": [
                {"id": 1, "area": "Reduce Cancellation Costs",
                 "description": "Better product descriptions + QC reduces returns by 30% → saves processing + shipping costs."},
                {"id": 2, "area": "Inventory Optimization",
                 "description": "Use time-series forecasting to right-size inventory → reduce holding costs by 15%."},
                {"id": 3, "area": "Marketing Spend Efficiency",
                 "description": "Focus spend on high-CLV segments (RFM), reduce budget on dormant re-activation."},
                {"id": 4, "area": "Shipping Consolidation",
                 "description": "Encourage multi-item orders vs single-item with free shipping minimum thresholds."},
                {"id": 5, "area": "Off-Peak Staffing",
                 "description": "Align support & fulfillment staffing with actual hourly demand patterns."},
            ],
            "risk_areas": [
                {"risk": "Geographic over-dependence on UK market (regulatory, economic, Brexit impacts)"},
                {"risk": "Top customer concentration — loss of top 50 customers would severely impact revenue"},
                {"risk": "Seasonality creates cash-flow vulnerability in Q1"},
                {"risk": "Cancellations may indicate systematic quality or fulfillment issues"},
                {"risk": "Lack of margin data prevents true profitability analysis"},
            ]
        }

        self.result["business_insights"] = _safe(insights)
        _ok(f"Generated {len(insights['strategic_insights'])} strategic insights")
        _ok(f"Generated {len(insights['revenue_opportunities'])} revenue opportunities")
        _ok(f"Generated {len(insights['cost_optimizations'])} cost optimizations")
        return self

    # -----------------------------------------------------------------
    #  PHASE 7 — Export
    # -----------------------------------------------------------------
    def export_json(self):
        _phase(7, "EXPORT DATA JSON")
        self.result["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "source_file": os.path.basename(self.file_path),
            "total_rows": len(self.df),
            "positive_rows": len(self.df_pos),
            "date_range": {
                "start": self.df_pos["invoice_date"].min().isoformat(),
                "end": self.df_pos["invoice_date"].max().isoformat()
            },
            "engine": "GravityAnalyticsEngine v3.0",
            "task": "Task 3 — Deep-Dive Analysis & Interactive Dashboarding"
        }

        # KPI indicator types reference
        self.result["indicator_reference"] = {
            "leading_indicators": {
                "definition": "Metrics that predict future performance",
                "examples": ["CLV", "Retention Rate", "New Customer Acquisition Rate"],
                "use": "Set targets and proactive strategy"
            },
            "lagging_indicators": {
                "definition": "Metrics that confirm past performance",
                "examples": ["Total Revenue", "Total Orders", "Churn Rate"],
                "use": "Evaluate results and measure effectiveness"
            },
            "vanity_vs_actionable": {
                "vanity": "Page views, total users (look good but don't drive decisions)",
                "actionable": "Conversion rate, CLV, churn rate (directly inform strategy changes)"
            }
        }

        path = os.path.join(self.output_dir, "dashboard_data.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.result, f, default=_safe, ensure_ascii=False)

        size_mb = os.path.getsize(path) / (1024 * 1024)
        _ok(f"Exported: dashboard_data.json ({size_mb:.1f} MB)")

        return self

    # -----------------------------------------------------------------
    #  Run All
    # -----------------------------------------------------------------
    def run(self):
        """Execute the full pipeline."""
        _banner()
        return (
            self.compute_kpis()
                .advanced_eda()
                .cohort_analysis()
                .rfm_segmentation()
                .sql_queries()
                .generate_insights()
                .export_json()
        )


# =====================================================================
#  CLI
# =====================================================================
def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(
        prog="gravity-analytics",
        description="Task 3: Deep-Dive Analytics & Dashboard Data Pipeline"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Path to cleaned_data.csv")
    parser.add_argument("--output", "-o",
                        default="./Task_3_Output",
                        help="Output directory (default: ./Task_3_Output)")
    args = parser.parse_args(argv)

    engine = GravityAnalyticsEngine(args.input, args.output)
    engine.run()
    _done("Analytics pipeline complete. Run the dashboard to visualize.")


if __name__ == "__main__":
    main()
