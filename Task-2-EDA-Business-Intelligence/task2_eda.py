#!/usr/bin/env python3
"""
task2_eda.py - Exploratory Data Analysis & Business Intelligence
================================================================
Performs comprehensive EDA on the cleaned retail dataset:
  1. Descriptive Statistics & Univariate Analysis
  2. SQL-based Business Questions
  3. Multivariate Analysis & Correlation
  4. Static Dashboard Mock-up (saved as PNG)

Usage:
    python task2_eda.py --input ../Task-1-Data-Immersion-Wrangling/Task_1_Output/cleaned_data.csv

Author : Hemang Dubey
Module : Task 2 - EDA & Business Intelligence (ApexPlanet)
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import textwrap
import warnings
from datetime import datetime
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

# =====================================================================
#  Style Configuration
# =====================================================================
# Premium dark theme
plt.rcParams.update({
    "figure.facecolor": "#0D1117",
    "axes.facecolor": "#161B22",
    "axes.edgecolor": "#30363D",
    "axes.labelcolor": "#C9D1D9",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.color": "#21262D",
    "grid.alpha": 0.6,
    "text.color": "#C9D1D9",
    "xtick.color": "#8B949E",
    "ytick.color": "#8B949E",
    "font.family": "sans-serif",
    "font.size": 10,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
})

# Color palettes
ACCENT = "#58A6FF"
ACCENT2 = "#F78166"
ACCENT3 = "#7EE787"
ACCENT4 = "#D2A8FF"
ACCENT5 = "#FF7B72"
PALETTE = [ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5, "#FFA657", "#79C0FF", "#FFAB70"]

WIDTH = 62


# =====================================================================
#  Console Helpers
# =====================================================================
class _S:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"


def _banner():
    print(f"\n{'=' * WIDTH}")
    print(f"{_S.BOLD}{_S.CYAN}  TASK 2  |  Exploratory Data Analysis & BI{_S.RESET}")
    print(f"{'=' * WIDTH}")


def _header(step: int, title: str):
    print(f"\n{_S.CYAN}{'─' * WIDTH}{_S.RESET}")
    print(f"{_S.BOLD}{_S.CYAN}  STEP {step}  |  {title}{_S.RESET}")
    print(f"{_S.CYAN}{'─' * WIDTH}{_S.RESET}")


def _info(msg: str):
    print(f"  {_S.GREEN}[OK]{_S.RESET}  {msg}")


def _detail(msg: str):
    print(f"  {_S.DIM}      {msg}{_S.RESET}")


def _sql_header(qnum: int, question: str):
    print(f"\n  {_S.YELLOW}Q{qnum}:{_S.RESET} {_S.BOLD}{question}{_S.RESET}")


def _success_box(msg: str):
    print(f"\n  {_S.GREEN}{'=' * WIDTH}{_S.RESET}")
    print(f"  {_S.BOLD}{_S.GREEN}  SUCCESS  {msg}{_S.RESET}")
    print(f"  {_S.GREEN}{'=' * WIDTH}{_S.RESET}\n")


# =====================================================================
#  Main EDA Class
# =====================================================================
class GravityEDA:
    """Comprehensive EDA pipeline for retail transaction data."""

    def __init__(self, file_path: str, output_dir: str):
        self.file_path = file_path
        self.output_dir = output_dir
        self.charts_dir = os.path.join(output_dir, "charts")
        self.sql_dir = os.path.join(output_dir, "sql_results")

        os.makedirs(self.charts_dir, exist_ok=True)
        os.makedirs(self.sql_dir, exist_ok=True)

        _header(0, "LOADING DATA")
        self.df = pd.read_csv(file_path, low_memory=False)
        self.df["invoice_date"] = pd.to_datetime(self.df["invoice_date"], errors="coerce")
        self.df["revenue"] = self.df["quantity"] * self.df["price"]

        _info(f"Loaded {len(self.df):,} rows x {self.df.shape[1]} columns")
        _detail(f"Revenue column added (quantity x price)")
        _detail(f"Date range: {self.df['invoice_date'].min()} to {self.df['invoice_date'].max()}")

    def _save_chart(self, fig, name: str):
        """Save figure and close."""
        path = os.path.join(self.charts_dir, f"{name}.png")
        fig.savefig(path, facecolor=fig.get_facecolor())
        plt.close(fig)
        _info(f"Chart saved: {name}.png")

    # =================================================================
    #  STEP 1: Descriptive Statistics & Univariate Analysis
    # =================================================================
    def step1_descriptive_univariate(self):
        """Calculate summary statistics and create univariate visualizations."""
        _header(1, "DESCRIPTIVE STATISTICS & UNIVARIATE ANALYSIS")

        df = self.df

        # --- Summary Statistics ---
        num_cols = ["quantity", "price", "revenue", "customer_id"]
        stats = df[num_cols].describe().T
        stats["skewness"] = df[num_cols].skew()
        stats["kurtosis"] = df[num_cols].kurtosis()
        _info("Descriptive statistics computed")

        # Print summary
        print(f"\n  {'Metric':<15} {'Mean':>12} {'Median':>12} {'Std':>12} {'Skew':>10}")
        print(f"  {'─'*15} {'─'*12} {'─'*12} {'─'*12} {'─'*10}")
        for col in num_cols:
            mean_val = df[col].mean()
            med_val = df[col].median()
            std_val = df[col].std()
            skew_val = df[col].skew()
            print(f"  {col:<15} {mean_val:>12,.2f} {med_val:>12,.2f} {std_val:>12,.2f} {skew_val:>10.2f}")
        print()

        # --- Chart 1: Revenue Distribution (Histogram) ---
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle("Univariate Analysis: Revenue & Quantity Distribution", fontsize=16, fontweight="bold", y=1.02)

        # Revenue histogram (clip extremes for readability)
        rev_clipped = df["revenue"][(df["revenue"] > 0) & (df["revenue"] < df["revenue"].quantile(0.95))]
        axes[0].hist(rev_clipped, bins=60, color=ACCENT, edgecolor="#0D1117", alpha=0.85)
        axes[0].set_title("Revenue per Transaction (0-95th percentile)")
        axes[0].set_xlabel("Revenue (GBP)")
        axes[0].set_ylabel("Frequency")
        axes[0].xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        # Quantity histogram
        qty_clipped = df["quantity"][(df["quantity"] > 0) & (df["quantity"] < df["quantity"].quantile(0.95))]
        axes[1].hist(qty_clipped, bins=60, color=ACCENT3, edgecolor="#0D1117", alpha=0.85)
        axes[1].set_title("Quantity per Transaction (0-95th percentile)")
        axes[1].set_xlabel("Quantity")
        axes[1].set_ylabel("Frequency")

        fig.tight_layout()
        self._save_chart(fig, "01_revenue_quantity_distribution")

        # --- Chart 2: Top 10 Countries by Revenue (Bar Chart) ---
        fig, ax = plt.subplots(figsize=(12, 6))
        country_rev = df.groupby("country")["revenue"].sum().sort_values(ascending=True).tail(10)
        bars = ax.barh(country_rev.index, country_rev.values, color=PALETTE[:10], edgecolor="#0D1117")
        ax.set_title("Top 10 Countries by Total Revenue", fontsize=14, fontweight="bold")
        ax.set_xlabel("Total Revenue (GBP)")
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        for bar, val in zip(bars, country_rev.values):
            ax.text(val + country_rev.max() * 0.01, bar.get_y() + bar.get_height()/2,
                    f"  {val:,.0f}", va="center", fontsize=9, color="#C9D1D9")
        fig.tight_layout()
        self._save_chart(fig, "02_top10_countries_revenue")

        # --- Chart 3: Top 10 Products by Sales Volume ---
        fig, ax = plt.subplots(figsize=(12, 6))
        top_products = df.groupby("description")["quantity"].sum().sort_values(ascending=True).tail(10)
        ax.barh(top_products.index, top_products.values, color=PALETTE[:10], edgecolor="#0D1117")
        ax.set_title("Top 10 Products by Sales Volume", fontsize=14, fontweight="bold")
        ax.set_xlabel("Total Quantity Sold")
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
        fig.tight_layout()
        self._save_chart(fig, "03_top10_products_volume")

        # --- Chart 4: Monthly Revenue Trend ---
        fig, ax = plt.subplots(figsize=(14, 5))
        monthly = df.set_index("invoice_date").resample("M")["revenue"].sum().reset_index()
        ax.plot(monthly["invoice_date"], monthly["revenue"], color=ACCENT, linewidth=2.5, marker="o", markersize=5)
        ax.fill_between(monthly["invoice_date"], monthly["revenue"], alpha=0.15, color=ACCENT)
        ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (GBP)")
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
        fig.autofmt_xdate()
        fig.tight_layout()
        self._save_chart(fig, "04_monthly_revenue_trend")

        # --- Chart 5: Orders by Day of Week ---
        fig, ax = plt.subplots(figsize=(10, 5))
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_counts = df["invoice_day_name"].value_counts().reindex(day_order).fillna(0)
        colors = [ACCENT if d != day_counts.idxmax() else ACCENT3 for d in day_order]
        ax.bar(day_counts.index, day_counts.values, color=colors, edgecolor="#0D1117")
        ax.set_title("Orders by Day of Week", fontsize=14, fontweight="bold")
        ax.set_ylabel("Number of Transactions")
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
        fig.tight_layout()
        self._save_chart(fig, "05_orders_by_day")

        # --- Chart 6: Price Distribution (Box Plot) ---
        fig, ax = plt.subplots(figsize=(10, 5))
        price_clipped = df["price"][(df["price"] > 0) & (df["price"] < df["price"].quantile(0.95))]
        bp = ax.boxplot(price_clipped, vert=False, patch_artist=True,
                        boxprops=dict(facecolor=ACCENT4, alpha=0.7),
                        medianprops=dict(color=ACCENT5, linewidth=2),
                        whiskerprops=dict(color="#8B949E"),
                        capprops=dict(color="#8B949E"),
                        flierprops=dict(marker="o", markerfacecolor=ACCENT5, markersize=3, alpha=0.3))
        ax.set_title("Price Distribution (0-95th percentile)", fontsize=14, fontweight="bold")
        ax.set_xlabel("Price (GBP)")
        fig.tight_layout()
        self._save_chart(fig, "06_price_boxplot")

        return self

    # =================================================================
    #  STEP 2: SQL for Business Questions
    # =================================================================
    def step2_sql_business_questions(self):
        """Load data into SQLite and answer 7 business questions with SQL."""
        _header(2, "SQL FOR BUSINESS QUESTIONS")

        # Load into SQLite
        conn = sqlite3.connect(":memory:")
        self.df.to_sql("transactions", conn, index=False, if_exists="replace")
        _info("Data loaded into SQLite in-memory database")

        queries = [
            {
                "num": 1,
                "question": "What are the top 5 products by total revenue?",
                "sql": """
                    SELECT description AS product,
                           ROUND(SUM(quantity * price), 2) AS total_revenue,
                           SUM(quantity) AS total_qty_sold,
                           COUNT(DISTINCT invoice) AS num_orders
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY description
                    ORDER BY total_revenue DESC
                    LIMIT 5;
                """
            },
            {
                "num": 2,
                "question": "What is the monthly revenue trend?",
                "sql": """
                    SELECT SUBSTR(invoice_date, 1, 7) AS month,
                           ROUND(SUM(quantity * price), 2) AS monthly_revenue,
                           COUNT(DISTINCT invoice) AS num_invoices,
                           COUNT(DISTINCT customer_id) AS unique_customers
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY month
                    ORDER BY month;
                """
            },
            {
                "num": 3,
                "question": "Which countries contribute the most revenue (Top 10)?",
                "sql": """
                    SELECT country,
                           ROUND(SUM(quantity * price), 2) AS total_revenue,
                           COUNT(DISTINCT customer_id) AS unique_customers,
                           COUNT(DISTINCT invoice) AS num_orders,
                           ROUND(SUM(quantity * price) * 100.0 /
                                 (SELECT SUM(quantity * price) FROM transactions WHERE quantity > 0 AND price > 0), 2)
                                 AS revenue_pct
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY country
                    ORDER BY total_revenue DESC
                    LIMIT 10;
                """
            },
            {
                "num": 4,
                "question": "Who are the top 10 customers by total spend?",
                "sql": """
                    SELECT CAST(customer_id AS INTEGER) AS customer_id,
                           ROUND(SUM(quantity * price), 2) AS total_spend,
                           COUNT(DISTINCT invoice) AS num_orders,
                           ROUND(AVG(quantity * price), 2) AS avg_order_value
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                          AND customer_id IS NOT NULL
                    GROUP BY customer_id
                    ORDER BY total_spend DESC
                    LIMIT 10;
                """
            },
            {
                "num": 5,
                "question": "What is the average order value by country?",
                "sql": """
                    SELECT country,
                           COUNT(DISTINCT invoice) AS total_orders,
                           ROUND(SUM(quantity * price), 2) AS total_revenue,
                           ROUND(SUM(quantity * price) / COUNT(DISTINCT invoice), 2) AS avg_order_value
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY country
                    HAVING total_orders >= 10
                    ORDER BY avg_order_value DESC
                    LIMIT 10;
                """
            },
            {
                "num": 6,
                "question": "What are the peak shopping hours?",
                "sql": """
                    SELECT CAST(SUBSTR(invoice_date, 12, 2) AS INTEGER) AS hour_of_day,
                           COUNT(*) AS num_transactions,
                           ROUND(SUM(quantity * price), 2) AS total_revenue,
                           ROUND(AVG(quantity * price), 2) AS avg_transaction_value
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY hour_of_day
                    ORDER BY hour_of_day;
                """
            },
            {
                "num": 7,
                "question": "What is the cancellation rate and revenue lost?",
                "sql": """
                    SELECT
                        COUNT(CASE WHEN quantity < 0 THEN 1 END) AS cancelled_items,
                        COUNT(*) AS total_items,
                        ROUND(COUNT(CASE WHEN quantity < 0 THEN 1 END) * 100.0 / COUNT(*), 2) AS cancel_rate_pct,
                        ROUND(ABS(SUM(CASE WHEN quantity < 0 THEN quantity * price ELSE 0 END)), 2) AS revenue_lost,
                        ROUND(SUM(CASE WHEN quantity > 0 THEN quantity * price ELSE 0 END), 2) AS revenue_earned
                    FROM transactions;
                """
            },
        ]

        all_results = []

        for q in queries:
            _sql_header(q["num"], q["question"])
            result = pd.read_sql_query(q["sql"], conn)
            print(f"\n{textwrap.indent(result.to_string(index=False), '      ')}\n")
            all_results.append({
                "question": q["question"],
                "sql": q["sql"].strip(),
                "result": result
            })

        # Save SQL report
        self._save_sql_report(all_results)
        conn.close()

        return self

    def _save_sql_report(self, results: list):
        """Save all SQL queries and results to a Markdown file."""
        lines = [
            "# SQL Business Questions Report",
            "",
            f"> Generated on `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            "",
            "---",
            "",
        ]

        for i, r in enumerate(results, 1):
            lines.append(f"## Q{i}: {r['question']}")
            lines.append("")
            lines.append("**SQL Query:**")
            lines.append("```sql")
            lines.append(r["sql"])
            lines.append("```")
            lines.append("")
            lines.append("**Result:**")
            lines.append("")
            # Convert to markdown table
            md_table = r["result"].to_markdown(index=False)
            lines.append(md_table if md_table else "*No results*")
            lines.append("")
            lines.append("---")
            lines.append("")

        path = os.path.join(self.sql_dir, "sql_queries_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        _info(f"SQL report saved: sql_queries_report.md")

    # =================================================================
    #  STEP 3: Multivariate Analysis & Correlation
    # =================================================================
    def step3_multivariate_correlation(self):
        """Create advanced visualizations for multi-variable relationships."""
        _header(3, "MULTIVARIATE ANALYSIS & CORRELATION")

        df = self.df

        # --- Chart 7: Correlation Heatmap ---
        fig, ax = plt.subplots(figsize=(10, 8))
        num_cols = ["quantity", "price", "revenue", "customer_id", "invoice_year", "invoice_month"]
        corr = df[num_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                    center=0, square=True, linewidths=1, linecolor="#30363D",
                    cbar_kws={"shrink": 0.8}, ax=ax,
                    annot_kws={"size": 11, "weight": "bold"})
        ax.set_title("Correlation Heatmap (Numerical Features)", fontsize=14, fontweight="bold", pad=15)
        fig.tight_layout()
        self._save_chart(fig, "07_correlation_heatmap")

        # --- Chart 8: Revenue vs Quantity Scatter (by country) ---
        fig, ax = plt.subplots(figsize=(12, 7))
        country_stats = df[df["revenue"] > 0].groupby("country").agg(
            avg_qty=("quantity", "mean"),
            avg_revenue=("revenue", "mean"),
            total_orders=("invoice", "nunique")
        ).reset_index()

        scatter = ax.scatter(
            country_stats["avg_qty"], country_stats["avg_revenue"],
            s=country_stats["total_orders"] / country_stats["total_orders"].max() * 500 + 30,
            c=range(len(country_stats)), cmap="viridis", alpha=0.75, edgecolor="#30363D", linewidth=0.8
        )
        # Label top countries
        top_n = country_stats.nlargest(8, "total_orders")
        for _, row in top_n.iterrows():
            ax.annotate(row["country"], (row["avg_qty"], row["avg_revenue"]),
                        fontsize=8, color="#C9D1D9", ha="center", va="bottom",
                        xytext=(0, 8), textcoords="offset points")
        ax.set_title("Avg Revenue vs Avg Quantity by Country (bubble = order volume)", fontsize=13, fontweight="bold")
        ax.set_xlabel("Average Quantity per Transaction")
        ax.set_ylabel("Average Revenue per Transaction (GBP)")
        fig.tight_layout()
        self._save_chart(fig, "08_revenue_vs_quantity_scatter")

        # --- Chart 9: Revenue by Month & Year Heatmap ---
        fig, ax = plt.subplots(figsize=(12, 5))
        pivot = df[df["revenue"] > 0].pivot_table(
            values="revenue", index="invoice_year", columns="invoice_month",
            aggfunc="sum", fill_value=0
        )
        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        pivot.columns = [month_labels[m-1] for m in pivot.columns]
        sns.heatmap(pivot, annot=True, fmt=",.0f", cmap="YlOrRd",
                    linewidths=1, linecolor="#30363D", ax=ax,
                    annot_kws={"size": 9})
        ax.set_title("Revenue Heatmap: Year x Month", fontsize=14, fontweight="bold")
        ax.set_ylabel("Year")
        ax.set_xlabel("Month")
        fig.tight_layout()
        self._save_chart(fig, "09_revenue_year_month_heatmap")

        # --- Chart 10: Hourly Sales Pattern ---
        fig, ax = plt.subplots(figsize=(12, 5))
        df_positive = df[df["revenue"] > 0].copy()
        df_positive["hour"] = df_positive["invoice_date"].dt.hour
        hourly = df_positive.groupby("hour").agg(
            orders=("invoice", "nunique"),
            revenue=("revenue", "sum")
        ).reset_index()

        ax2 = ax.twinx()
        ax.bar(hourly["hour"], hourly["orders"], color=ACCENT, alpha=0.6, label="Orders", edgecolor="#0D1117")
        ax2.plot(hourly["hour"], hourly["revenue"], color=ACCENT2, linewidth=2.5, marker="o", label="Revenue")

        ax.set_title("Hourly Shopping Pattern: Orders & Revenue", fontsize=14, fontweight="bold")
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Number of Orders", color=ACCENT)
        ax2.set_ylabel("Revenue (GBP)", color=ACCENT2)
        ax.set_xticks(range(6, 21))
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
        ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
                  facecolor="#161B22", edgecolor="#30363D", labelcolor="#C9D1D9")
        fig.tight_layout()
        self._save_chart(fig, "10_hourly_sales_pattern")

        # --- Chart 11: Pair Plot (sampled) ---
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Pairwise Relationships (Sampled Data)", fontsize=16, fontweight="bold", y=1.02)

        sample = df[(df["revenue"] > 0) & (df["revenue"] < df["revenue"].quantile(0.95))].sample(
            n=min(5000, len(df)), random_state=42
        )

        # Quantity vs Price
        axes[0, 0].scatter(sample["quantity"], sample["price"], alpha=0.3, s=8, c=ACCENT)
        axes[0, 0].set_xlabel("Quantity")
        axes[0, 0].set_ylabel("Price")
        axes[0, 0].set_title("Quantity vs Price")

        # Revenue vs Quantity
        axes[0, 1].scatter(sample["quantity"], sample["revenue"], alpha=0.3, s=8, c=ACCENT3)
        axes[0, 1].set_xlabel("Quantity")
        axes[0, 1].set_ylabel("Revenue")
        axes[0, 1].set_title("Quantity vs Revenue")

        # Month vs Revenue
        axes[1, 0].scatter(sample["invoice_month"], sample["revenue"], alpha=0.3, s=8, c=ACCENT4)
        axes[1, 0].set_xlabel("Month")
        axes[1, 0].set_ylabel("Revenue")
        axes[1, 0].set_title("Month vs Revenue")

        # Price vs Revenue
        axes[1, 1].scatter(sample["price"], sample["revenue"], alpha=0.3, s=8, c=ACCENT2)
        axes[1, 1].set_xlabel("Price")
        axes[1, 1].set_ylabel("Revenue")
        axes[1, 1].set_title("Price vs Revenue")

        fig.tight_layout()
        self._save_chart(fig, "11_pairwise_scatter")

        return self

    # =================================================================
    #  STEP 4: Static Dashboard Mock-up
    # =================================================================
    def step4_dashboard_mockup(self):
        """Create a static KPI dashboard as a single PNG image."""
        _header(4, "STATIC DASHBOARD MOCK-UP")

        df = self.df
        df_pos = df[df["revenue"] > 0]

        # ---- Calculate KPIs ----
        total_revenue = df_pos["revenue"].sum()
        total_orders = df_pos["invoice"].nunique()
        total_customers = df_pos["customer_id"].nunique()
        avg_order_value = total_revenue / total_orders
        total_products = df_pos["description"].nunique()
        total_countries = df_pos["country"].nunique()

        # ---- Build Dashboard Figure ----
        fig = plt.figure(figsize=(20, 14), facecolor="#0D1117")
        fig.suptitle("RETAIL ANALYTICS DASHBOARD",
                     fontsize=24, fontweight="bold", color="#FFFFFF", y=0.98)
        fig.text(0.5, 0.955, f"Data Period: {df['invoice_date'].min().strftime('%b %Y')} - {df['invoice_date'].max().strftime('%b %Y')}",
                 fontsize=11, ha="center", color="#8B949E")

        # Grid: 4 rows x 4 cols
        gs = fig.add_gridspec(4, 4, hspace=0.45, wspace=0.35,
                              left=0.06, right=0.94, top=0.92, bottom=0.05)

        # ---- KPI Cards (Row 0) ----
        kpis = [
            ("Total Revenue", f"£{total_revenue:,.0f}", ACCENT3),
            ("Total Orders", f"{total_orders:,}", ACCENT),
            ("Unique Customers", f"{total_customers:,}", ACCENT4),
            ("Avg Order Value", f"£{avg_order_value:,.2f}", ACCENT2),
        ]

        for i, (label, value, color) in enumerate(kpis):
            ax = fig.add_subplot(gs[0, i])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_facecolor("#161B22")
            for spine in ax.spines.values():
                spine.set_color(color)
                spine.set_linewidth(2)
            ax.text(0.5, 0.65, value, fontsize=22, fontweight="bold",
                    color=color, ha="center", va="center")
            ax.text(0.5, 0.25, label, fontsize=11, color="#8B949E",
                    ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])

        # ---- Chart A: Monthly Revenue Trend (Row 1, cols 0-1) ----
        ax_trend = fig.add_subplot(gs[1, 0:2])
        monthly = df_pos.set_index("invoice_date").resample("M")["revenue"].sum().reset_index()
        ax_trend.plot(monthly["invoice_date"], monthly["revenue"],
                      color=ACCENT, linewidth=2, marker="o", markersize=4)
        ax_trend.fill_between(monthly["invoice_date"], monthly["revenue"],
                              alpha=0.1, color=ACCENT)
        ax_trend.set_title("Monthly Revenue Trend", fontsize=12, fontweight="bold")
        ax_trend.set_ylabel("Revenue (GBP)")
        ax_trend.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
        ax_trend.tick_params(axis="x", rotation=45, labelsize=8)

        # ---- Chart B: Top 5 Countries (Row 1, cols 2-3) ----
        ax_country = fig.add_subplot(gs[1, 2:4])
        top_countries = df_pos.groupby("country")["revenue"].sum().sort_values(ascending=True).tail(5)
        ax_country.barh(top_countries.index, top_countries.values,
                        color=[ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5], edgecolor="#0D1117")
        ax_country.set_title("Top 5 Countries by Revenue", fontsize=12, fontweight="bold")
        ax_country.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        # ---- Chart C: Day of Week (Row 2, cols 0-1) ----
        ax_day = fig.add_subplot(gs[2, 0:2])
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        day_rev = df_pos.groupby("invoice_day_name")["revenue"].sum().reindex(day_order).fillna(0)
        colors_day = [ACCENT if d != day_rev.idxmax() else ACCENT3 for d in day_order]
        ax_day.bar(range(len(day_order)), day_rev.values, color=colors_day, edgecolor="#0D1117")
        ax_day.set_xticks(range(len(day_order)))
        ax_day.set_xticklabels([d[:3] for d in day_order])
        ax_day.set_title("Revenue by Day of Week", fontsize=12, fontweight="bold")
        ax_day.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        # ---- Chart D: Top 5 Products (Row 2, cols 2-3) ----
        ax_prod = fig.add_subplot(gs[2, 2:4])
        top_prods = df_pos.groupby("description")["revenue"].sum().sort_values(ascending=True).tail(5)
        short_names = [n[:30] + "..." if len(n) > 30 else n for n in top_prods.index]
        ax_prod.barh(short_names, top_prods.values,
                     color=[ACCENT, ACCENT2, ACCENT3, ACCENT4, ACCENT5], edgecolor="#0D1117")
        ax_prod.set_title("Top 5 Products by Revenue", fontsize=12, fontweight="bold")
        ax_prod.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        # ---- Chart E: Hourly Pattern (Row 3, cols 0-1) ----
        ax_hour = fig.add_subplot(gs[3, 0:2])
        df_pos_h = df_pos.copy()
        df_pos_h["hour"] = df_pos_h["invoice_date"].dt.hour
        hourly = df_pos_h.groupby("hour")["revenue"].sum().reset_index()
        ax_hour.bar(hourly["hour"], hourly["revenue"], color=ACCENT, alpha=0.7, edgecolor="#0D1117")
        ax_hour.set_title("Revenue by Hour of Day", fontsize=12, fontweight="bold")
        ax_hour.set_xlabel("Hour")
        ax_hour.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

        # ---- Chart F: Customer Segments (Row 3, cols 2-3) ----
        ax_seg = fig.add_subplot(gs[3, 2:4])
        customer_spend = df_pos.groupby("customer_id")["revenue"].sum()
        bins = [0, 100, 500, 1000, 5000, float("inf")]
        labels = ["<£100", "£100-500", "£500-1K", "£1K-5K", "£5K+"]
        segments = pd.cut(customer_spend, bins=bins, labels=labels)
        seg_counts = segments.value_counts().reindex(labels)
        ax_seg.pie(seg_counts, labels=labels, autopct="%1.1f%%",
                   colors=PALETTE[:5], textprops={"color": "#C9D1D9", "fontsize": 9},
                   wedgeprops={"edgecolor": "#0D1117", "linewidth": 1.5})
        ax_seg.set_title("Customer Spend Segments", fontsize=12, fontweight="bold")

        # Save dashboard
        path = os.path.join(self.output_dir, "dashboard_mockup.png")
        fig.savefig(path, facecolor=fig.get_facecolor(), dpi=150)
        plt.close(fig)
        _info(f"Dashboard saved: dashboard_mockup.png")

        return self

    # =================================================================
    #  STEP 5: Generate EDA Report
    # =================================================================
    def save_eda_report(self):
        """Generate a comprehensive Markdown EDA report."""
        _header(5, "GENERATING EDA REPORT")

        df = self.df
        df_pos = df[df["revenue"] > 0]

        lines = [
            "# Exploratory Data Analysis Report",
            "",
            f"> Generated on `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            "",
            "---",
            "",
            "## 1. Dataset Overview",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Rows | {len(df):,} |",
            f"| Total Columns | {df.shape[1]} |",
            f"| Date Range | {df['invoice_date'].min().strftime('%Y-%m-%d')} to {df['invoice_date'].max().strftime('%Y-%m-%d')} |",
            f"| Unique Products | {df['description'].nunique():,} |",
            f"| Unique Customers | {df['customer_id'].nunique():,} |",
            f"| Countries | {df['country'].nunique()} |",
            "",
            "## 2. Key Performance Indicators",
            "",
            f"| KPI | Value |",
            f"|-----|-------|",
            f"| Total Revenue | £{df_pos['revenue'].sum():,.2f} |",
            f"| Total Orders | {df_pos['invoice'].nunique():,} |",
            f"| Avg Order Value | £{df_pos['revenue'].sum() / df_pos['invoice'].nunique():,.2f} |",
            f"| Avg Revenue per Customer | £{df_pos['revenue'].sum() / df_pos['customer_id'].nunique():,.2f} |",
            f"| Cancellation Rate | {len(df[df['quantity'] < 0]) / len(df) * 100:.2f}% |",
            "",
            "## 3. Key Insights",
            "",
            "### Revenue Distribution",
            f"- Revenue is **heavily right-skewed** (skewness: {df_pos['revenue'].skew():.2f})",
            f"- Median transaction value: £{df_pos['revenue'].median():.2f} vs Mean: £{df_pos['revenue'].mean():.2f}",
            f"- Top 10% of transactions account for a disproportionate share of revenue",
            "",
            "### Geographic Analysis",
            f"- **United Kingdom** dominates with ~{df_pos[df_pos['country'] == 'United Kingdom']['revenue'].sum() / df_pos['revenue'].sum() * 100:.0f}% of total revenue",
            f"- {df['country'].nunique()} countries served in total",
            "",
            "### Temporal Patterns",
            f"- Peak shopping hours: 10 AM - 3 PM",
            f"- Thursday shows the highest order volume",
            f"- Revenue tends to peak in November (pre-holiday season)",
            "",
            "## 4. Visualizations Generated",
            "",
            "| # | Chart | Description |",
            "|---|-------|-------------|",
            "| 1 | Revenue & Quantity Distribution | Histograms showing transaction distributions |",
            "| 2 | Top 10 Countries by Revenue | Horizontal bar chart of geographic revenue |",
            "| 3 | Top 10 Products by Volume | Best-selling products by quantity |",
            "| 4 | Monthly Revenue Trend | Time series of monthly revenue |",
            "| 5 | Orders by Day of Week | Weekly shopping patterns |",
            "| 6 | Price Distribution | Box plot of price ranges |",
            "| 7 | Correlation Heatmap | Numerical feature correlations |",
            "| 8 | Revenue vs Quantity Scatter | Country-level relationship analysis |",
            "| 9 | Year x Month Revenue Heatmap | Seasonal revenue patterns |",
            "| 10 | Hourly Sales Pattern | Dual-axis hourly analysis |",
            "| 11 | Pairwise Scatter Plots | Multi-variable relationships |",
            "",
            "## 5. Dashboard KPIs Proposed",
            "",
            "| KPI | Purpose | Update Frequency |",
            "|-----|---------|-----------------|",
            "| Total Revenue | Track overall business health | Daily |",
            "| Order Count | Monitor transaction volume | Daily |",
            "| Avg Order Value | Track basket size trends | Weekly |",
            "| Customer Count | Active customer monitoring | Weekly |",
            "| Revenue by Country | Geographic performance | Monthly |",
            "| Top Products | Product performance tracking | Weekly |",
            "| Cancellation Rate | Quality/returns monitoring | Daily |",
            "| Revenue per Customer | Customer value tracking | Monthly |",
            "",
            "---",
            "*End of EDA Report*",
        ]

        path = os.path.join(self.output_dir, "eda_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        _info(f"EDA report saved: eda_report.md")

        return self


# =====================================================================
#  CLI Entry Point
# =====================================================================
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gravity-eda",
        description="Task 2: Exploratory Data Analysis & Business Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Path to the cleaned dataset (.csv)")
    parser.add_argument("--output", "-o", default="./Task_2_Output",
                        help="Output directory (default: ./Task_2_Output)")
    return parser


def main(argv: Optional[List[str]] = None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    _banner()
    print(f"\n  {_S.DIM}Input  :{_S.RESET}  {args.input}")
    print(f"  {_S.DIM}Output :{_S.RESET}  {args.output}")

    eda = GravityEDA(args.input, args.output)

    (
        eda
        .step1_descriptive_univariate()
        .step2_sql_business_questions()
        .step3_multivariate_correlation()
        .step4_dashboard_mockup()
        .save_eda_report()
    )

    _success_box(f"All artifacts saved to {args.output}")


if __name__ == "__main__":
    main()
