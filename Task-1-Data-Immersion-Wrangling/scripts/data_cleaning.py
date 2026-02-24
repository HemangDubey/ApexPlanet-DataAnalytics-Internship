"""
=============================================================================
 Data Immersion & Wrangling - Task 1
 Online Retail Dataset: Data Cleaning & Transformation Script
=============================================================================
 
 This script performs the complete data wrangling pipeline:
   Step 1: Data Access & Familiarization
   Step 2: Data Quality Assessment  
   Step 3: Data Cleaning & Transformation
 
 Dataset: Online Retail Transaction Dataset
 Source:   UCI Machine Learning Repository (via Apex Planet Internship)
 Records: ~1,067,371 transactions
 
 Author:  Apex Planet Data Analytics Intern
 Date:    2026-02-24
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw_data.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_data.csv")
REPORT_PATH = os.path.join(BASE_DIR, "docs", "data_quality_report.md")
DATA_DICT_PATH = os.path.join(BASE_DIR, "docs", "data_dictionary.md")

# Ensure output directories exist
os.makedirs(os.path.join(BASE_DIR, "docs"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title):
    """Print a formatted sub-section header."""
    print(f"\n--- {title} ---")


# =============================================================================
#  STEP 1: DATA ACCESS & FAMILIARIZATION
# =============================================================================
def step1_data_familiarization(df):
    """
    Step 1: Load and explore the dataset to understand its structure,
    column types, sample values, and basic statistics.
    """
    print_header("STEP 1: DATA ACCESS & FAMILIARIZATION")

    # 1.1 Dataset Shape
    print_subheader("1.1 Dataset Shape")
    print(f"  Total Rows:    {df.shape[0]:,}")
    print(f"  Total Columns: {df.shape[1]}")

    # 1.2 Column Information
    print_subheader("1.2 Column Info (dtypes & non-null counts)")
    print(df.info())

    # 1.3 First 5 Rows
    print_subheader("1.3 First 5 Rows")
    print(df.head().to_string())

    # 1.4 Last 5 Rows
    print_subheader("1.4 Last 5 Rows")
    print(df.tail().to_string())

    # 1.5 Statistical Summary (Numerical Columns)
    print_subheader("1.5 Statistical Summary (Numerical Columns)")
    print(df.describe().to_string())

    # 1.6 Statistical Summary (Categorical Columns)
    print_subheader("1.6 Statistical Summary (Categorical Columns)")
    print(df.describe(include="object").to_string())

    # 1.7 Unique Value Counts
    print_subheader("1.7 Unique Values per Column")
    for col in df.columns:
        print(f"  {col:20s}: {df[col].nunique():>10,} unique values")

    # 1.8 Sample Values per Column
    print_subheader("1.8 Sample Values per Column")
    for col in df.columns:
        sample_vals = df[col].dropna().unique()[:5]
        print(f"  {col:20s}: {list(sample_vals)}")

    return df


# =============================================================================
#  STEP 2: DATA QUALITY ASSESSMENT
# =============================================================================
def step2_data_quality_assessment(df):
    """
    Step 2: Profile the data to identify critical issues including
    missing values, duplicates, inconsistent formatting, and outliers.
    """
    print_header("STEP 2: DATA QUALITY ASSESSMENT")
    
    issues = {}  # Collect all issues for the report

    # 2.1 Missing Values Analysis
    print_subheader("2.1 Missing Values Analysis")
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df)) * 100
    missing_df = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": missing_pct.round(2)
    })
    missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values(
        "Missing Count", ascending=False
    )
    if len(missing_df) > 0:
        print(missing_df.to_string())
        issues["missing_values"] = missing_df.to_dict()
    else:
        print("  No missing values found.")

    # 2.2 Duplicate Records
    print_subheader("2.2 Duplicate Records")
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100
    print(f"  Duplicate Records:  {dup_count:,} ({dup_pct:.2f}%)")
    issues["duplicates"] = {"count": int(dup_count), "percentage": round(dup_pct, 2)}

    # Show sample duplicates
    if dup_count > 0:
        print("\n  Sample Duplicate Records:")
        dups = df[df.duplicated(keep=False)].sort_values(df.columns.tolist()).head(10)
        print(dups.to_string())

    # 2.3 Negative/Invalid Values in Numeric Columns
    print_subheader("2.3 Invalid Values in Numeric Columns")
    
    # Quantity negatives
    neg_qty = (df["Quantity"] < 0).sum()
    neg_qty_pct = (neg_qty / len(df)) * 100
    print(f"  Negative Quantity:  {neg_qty:,} ({neg_qty_pct:.2f}%)")
    print(f"    → Min Quantity:   {df['Quantity'].min():,}")
    issues["negative_quantity"] = {"count": int(neg_qty), "percentage": round(neg_qty_pct, 2)}

    # Zero quantity
    zero_qty = (df["Quantity"] == 0).sum()
    print(f"  Zero Quantity:      {zero_qty:,}")

    # Price negatives
    neg_price = (df["Price"] < 0).sum()
    neg_price_pct = (neg_price / len(df)) * 100
    print(f"  Negative Price:     {neg_price:,} ({neg_price_pct:.2f}%)")
    print(f"    → Min Price:      {df['Price'].min():,.2f}")
    issues["negative_price"] = {"count": int(neg_price), "percentage": round(neg_price_pct, 2)}

    # Zero price
    zero_price = (df["Price"] == 0).sum()
    print(f"  Zero Price:         {zero_price:,}")
    issues["zero_price"] = {"count": int(zero_price)}

    # 2.4 Outlier Detection (IQR Method)
    print_subheader("2.4 Outlier Detection (IQR Method)")
    for col in ["Quantity", "Price"]:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        outlier_pct = (outliers / len(df)) * 100
        print(f"  {col}:")
        print(f"    Q1={Q1:,.2f}, Q3={Q3:,.2f}, IQR={IQR:,.2f}")
        print(f"    Lower Bound={lower:,.2f}, Upper Bound={upper:,.2f}")
        print(f"    Outliers: {outliers:,} ({outlier_pct:.2f}%)")

    # 2.5 Data Type Checks
    print_subheader("2.5 Data Type Assessment")
    print(f"  InvoiceDate dtype: {df['InvoiceDate'].dtype}")
    print(f"    → Should be datetime (currently stored as object/string)")
    print(f"  Customer ID dtype: {df['Customer ID'].dtype}")
    print(f"    → Stored as float due to NaN; should be integer/string identifier")

    # 2.6 Inconsistent Formatting in Text Columns
    print_subheader("2.6 Text Column Consistency Check")
    
    # Check Description for inconsistencies
    desc_non_null = df["Description"].dropna()
    has_lower = (desc_non_null.str.islower()).sum()
    has_upper = (desc_non_null.str.isupper()).sum()
    has_mixed = len(desc_non_null) - has_lower - has_upper
    print(f"  Description casing:")
    print(f"    ALL UPPER:  {has_upper:,}")
    print(f"    all lower:  {has_lower:,}")
    print(f"    Mixed Case: {has_mixed:,}")

    # Check for leading/trailing whitespace
    leading_ws = (desc_non_null.str.startswith(" ")).sum()
    trailing_ws = (desc_non_null.str.endswith(" ")).sum()
    print(f"  Leading whitespace in Description:  {leading_ws:,}")
    print(f"  Trailing whitespace in Description: {trailing_ws:,}")

    # Check Country column
    print(f"\n  Countries found: {df['Country'].nunique()}")
    print(f"  Top 10 Countries by transactions:")
    print(df["Country"].value_counts().head(10).to_string())

    # 2.7 Invoice Number Patterns
    print_subheader("2.7 Invoice Number Patterns")
    cancelled = df["Invoice"].astype(str).str.startswith("C")
    print(f"  Cancelled invoices (starting with 'C'): {cancelled.sum():,}")
    issues["cancelled_invoices"] = {"count": int(cancelled.sum())}

    return df, issues


# =============================================================================
#  STEP 3: DATA CLEANING & TRANSFORMATION
# =============================================================================
def step3_data_cleaning(df):
    """
    Step 3: Clean and transform the dataset based on issues identified
    in the quality assessment.
    """
    print_header("STEP 3: DATA CLEANING & TRANSFORMATION")

    initial_rows = len(df)
    cleaning_log = []

    # 3.1 Remove Duplicate Records
    print_subheader("3.1 Removing Duplicate Records")
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"  Removed: {removed:,} duplicate rows")
    print(f"  Remaining: {len(df):,} rows")
    cleaning_log.append(f"Removed {removed:,} duplicate records")

    # 3.2 Remove Cancelled Transactions (Negative Quantity)
    print_subheader("3.2 Removing Cancelled/Returned Transactions")
    before = len(df)
    df = df[df["Quantity"] > 0]
    removed = before - len(df)
    print(f"  Removed: {removed:,} rows with non-positive quantity")
    print(f"  Remaining: {len(df):,} rows")
    cleaning_log.append(f"Removed {removed:,} rows with non-positive quantity (cancelled/returned)")

    # 3.3 Remove Invalid Prices
    print_subheader("3.3 Removing Invalid Price Records")
    before = len(df)
    df = df[df["Price"] > 0]
    removed = before - len(df)
    print(f"  Removed: {removed:,} rows with non-positive price")
    print(f"  Remaining: {len(df):,} rows")
    cleaning_log.append(f"Removed {removed:,} rows with non-positive price")

    # 3.4 Handle Missing Customer IDs
    print_subheader("3.4 Handling Missing Customer IDs")
    before = len(df)
    df = df.dropna(subset=["Customer ID"])
    removed = before - len(df)
    print(f"  Removed: {removed:,} rows with missing Customer ID")
    print(f"  Remaining: {len(df):,} rows")
    cleaning_log.append(f"Removed {removed:,} rows with missing Customer ID")

    # 3.5 Data Type Conversions
    print_subheader("3.5 Data Type Transformations")
    
    # Convert InvoiceDate to datetime
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    print(f"  ✔ InvoiceDate → datetime64")

    # Convert Customer ID to integer
    df["Customer ID"] = df["Customer ID"].astype(int)
    print(f"  ✔ Customer ID → int (removed decimal)")

    # 3.6 Standardize Text Columns
    print_subheader("3.6 Standardizing Text Columns")
    df["Description"] = df["Description"].str.strip().str.upper()
    print(f"  ✔ Description → stripped whitespace, converted to UPPER")
    
    df["Country"] = df["Country"].str.strip().str.title()
    print(f"  ✔ Country → stripped whitespace, Title Case")

    # 3.7 Feature Engineering
    print_subheader("3.7 Feature Engineering")
    
    # Total Amount (Revenue per line item)
    df["TotalAmount"] = df["Quantity"] * df["Price"]
    print(f"  ✔ Created 'TotalAmount' = Quantity × Price")

    # Extract Date Components
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
    df["Hour"] = df["InvoiceDate"].dt.hour
    print(f"  ✔ Created 'Year', 'Month', 'DayOfWeek', 'Hour' from InvoiceDate")

    # 3.8 Final Validation
    print_subheader("3.8 Final Validation")
    final_rows = len(df)
    total_removed = initial_rows - final_rows
    print(f"  Initial rows:     {initial_rows:,}")
    print(f"  Final rows:       {final_rows:,}")
    print(f"  Total removed:    {total_removed:,} ({(total_removed/initial_rows)*100:.2f}%)")
    print(f"  Remaining nulls:  {df.isnull().sum().sum()}")
    print(f"  Remaining dups:   {df.duplicated().sum()}")
    print(f"\n  Final column types:")
    for col in df.columns:
        print(f"    {col:20s}: {df[col].dtype}")

    print(f"\n  Final Descriptive Statistics:")
    print(df.describe().to_string())

    return df, cleaning_log


# =============================================================================
#  GENERATE DATA DICTIONARY
# =============================================================================
def generate_data_dictionary(df_raw, df_clean):
    """Generate a comprehensive data dictionary markdown file."""
    
    content = """# 📖 Data Dictionary — Online Retail Dataset

## Dataset Overview

| Attribute         | Value                                      |
|-------------------|---------------------------------------------|
| **Dataset Name**  | Online Retail Transaction Data              |
| **Source**         | UCI Machine Learning Repository             |
| **Format**         | CSV                                         |
| **Raw Records**    | {raw_rows:,}                                |
| **Clean Records**  | {clean_rows:,}                              |
| **Time Period**    | {min_date} to {max_date}                    |
| **Geography**      | {n_countries} countries                     |

---

## Column Descriptions (Raw Dataset)

| # | Column Name   | Data Type | Non-Null Count | Null Count | Null %  | Description                                                  | Business Relevance                            |
|---|---------------|-----------|----------------|------------|---------|--------------------------------------------------------------|-----------------------------------------------|
| 1 | `Invoice`     | object    | {raw_rows:,}   | 0          | 0.00%   | 6-digit invoice number. Prefix 'C' = cancelled transaction  | Uniquely identifies each transaction          |
| 2 | `StockCode`   | object    | {raw_rows:,}   | 0          | 0.00%   | 5-digit product/item code                                    | Identifies products for inventory analysis    |
| 3 | `Description` | object    | {desc_nn:,}    | {desc_null:,} | {desc_pct:.2f}%  | Product name/description                       | Product categorization and search             |
| 4 | `Quantity`    | int64     | {raw_rows:,}   | 0          | 0.00%   | Quantity of each product per transaction                      | Sales volume analysis                         |
| 5 | `InvoiceDate` | object    | {raw_rows:,}   | 0          | 0.00%   | Date and time of invoice generation (MM/DD/YYYY HH:MM)       | Time-series and seasonal analysis             |
| 6 | `Price`       | float64   | {raw_rows:,}   | 0          | 0.00%   | Unit price in GBP (£)                                        | Revenue calculation and pricing analysis      |
| 7 | `Customer ID` | float64   | {cust_nn:,}    | {cust_null:,} | {cust_pct:.2f}%  | 5-digit unique customer identifier               | Customer segmentation and retention analysis  |
| 8 | `Country`     | object    | {raw_rows:,}   | 0          | 0.00%   | Country where the customer resides                           | Geographic market analysis                    |

---

## New Columns (After Cleaning & Feature Engineering)

| # | Column Name   | Data Type  | Description                                          | Derivation                          |
|---|---------------|------------|------------------------------------------------------|-------------------------------------|
| 9 | `TotalAmount` | float64    | Total revenue per line item (£)                      | `Quantity × Price`                  |
|10 | `Year`        | int32      | Year extracted from InvoiceDate                      | `InvoiceDate.dt.year`               |
|11 | `Month`       | int32      | Month extracted from InvoiceDate (1–12)              | `InvoiceDate.dt.month`              |
|12 | `DayOfWeek`   | object     | Day name (Monday, Tuesday, …)                       | `InvoiceDate.dt.day_name()`         |
|13 | `Hour`        | int32      | Hour of the transaction (0–23)                       | `InvoiceDate.dt.hour`               |

---

## Data Quality Notes

### Issues Found in Raw Data
1. **Missing Values**: `Description` ({desc_null:,} nulls) and `Customer ID` ({cust_null:,} nulls)
2. **Duplicate Records**: {dup_count:,} exact duplicate rows
3. **Negative Quantity**: Represents cancelled/returned transactions
4. **Negative/Zero Price**: Invalid pricing entries
5. **Cancelled Invoices**: Invoice numbers starting with 'C'
6. **Inconsistent Text Casing**: Mixed casing in Description field

### Cleaning Actions Taken
- Removed all duplicate records
- Filtered out rows with `Quantity ≤ 0` (cancellations/returns)
- Filtered out rows with `Price ≤ 0` (invalid prices)
- Dropped rows with missing `Customer ID`
- Converted `InvoiceDate` from string to `datetime64`
- Converted `Customer ID` from float to integer
- Standardized `Description` to UPPER CASE with trimmed whitespace
- Standardized `Country` to Title Case with trimmed whitespace

---

## Value Ranges (Cleaned Dataset)

| Column        | Min        | Max          | Mean       | Median     |
|---------------|------------|--------------|------------|------------|
| `Quantity`    | {q_min:,}  | {q_max:,}    | {q_mean:.2f} | {q_med:.1f} |
| `Price`       | £{p_min:.3f} | £{p_max:,.2f} | £{p_mean:.2f} | £{p_med:.2f} |
| `TotalAmount` | £{t_min:.2f} | £{t_max:,.2f} | £{t_mean:.2f} | £{t_med:.2f} |

---

*Generated on: {gen_date}*
"""

    # Calculate values for placeholders
    raw_rows = len(df_raw)
    clean_rows = len(df_clean)
    
    desc_null = int(df_raw["Description"].isnull().sum())
    desc_nn = raw_rows - desc_null
    desc_pct = (desc_null / raw_rows) * 100
    
    cust_null = int(df_raw["Customer ID"].isnull().sum())
    cust_nn = raw_rows - cust_null
    cust_pct = (cust_null / raw_rows) * 100
    
    dup_count = int(df_raw.duplicated().sum())
    
    content = content.format(
        raw_rows=raw_rows,
        clean_rows=clean_rows,
        min_date=df_clean["InvoiceDate"].min().strftime("%Y-%m-%d"),
        max_date=df_clean["InvoiceDate"].max().strftime("%Y-%m-%d"),
        n_countries=df_clean["Country"].nunique(),
        desc_nn=desc_nn,
        desc_null=desc_null,
        desc_pct=desc_pct,
        cust_nn=cust_nn,
        cust_null=cust_null,
        cust_pct=cust_pct,
        dup_count=dup_count,
        q_min=int(df_clean["Quantity"].min()),
        q_max=int(df_clean["Quantity"].max()),
        q_mean=df_clean["Quantity"].mean(),
        q_med=df_clean["Quantity"].median(),
        p_min=df_clean["Price"].min(),
        p_max=df_clean["Price"].max(),
        p_mean=df_clean["Price"].mean(),
        p_med=df_clean["Price"].median(),
        t_min=df_clean["TotalAmount"].min(),
        t_max=df_clean["TotalAmount"].max(),
        t_mean=df_clean["TotalAmount"].mean(),
        t_med=df_clean["TotalAmount"].median(),
        gen_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    with open(DATA_DICT_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n  ✔ Data Dictionary saved to: {DATA_DICT_PATH}")


# =============================================================================
#  GENERATE DATA QUALITY REPORT
# =============================================================================
def generate_quality_report(df_raw, df_clean, issues, cleaning_log):
    """Generate a comprehensive data quality report as markdown."""

    report = """# 📊 Data Quality Assessment Report — Online Retail Dataset

> **Report Generated:** {gen_date}  
> **Dataset:** Online Retail Transaction Data  
> **Raw Records:** {raw_rows:,} | **Clean Records:** {clean_rows:,}

---

## 1. Executive Summary

The raw dataset contains **{raw_rows:,}** transaction records across **8 columns**. 
After comprehensive quality assessment, the following critical issues were identified 
and resolved through the cleaning pipeline:

| Issue Category          | Records Affected | % of Total |
|------------------------|-------------------|------------|
| Duplicate Records       | {dup_count:,}     | {dup_pct:.2f}%  |
| Missing Customer ID     | {cust_null:,}     | {cust_pct:.2f}%  |
| Missing Description     | {desc_null:,}     | {desc_pct:.2f}%  |
| Negative Quantity       | {neg_qty:,}       | {neg_qty_pct:.2f}%  |
| Non-positive Price      | {bad_price:,}     | {bad_price_pct:.2f}%  |

After cleaning, **{clean_rows:,}** records remain ({retain_pct:.1f}% retention rate).

---

## 2. Missing Values Analysis

| Column        | Missing Count | Missing % | Impact                                           |
|---------------|---------------|-----------|--------------------------------------------------|
| `Customer ID` | {cust_null:,} | {cust_pct:.2f}% | Cannot perform customer-level analysis          |
| `Description` | {desc_null:,} | {desc_pct:.2f}% | Minor impact; product identifiable via StockCode |
| Other columns | 0             | 0.00%     | No impact                                        |

**Decision:** Rows with missing `Customer ID` were removed since customer-level 
analysis is a core requirement. Missing `Description` rows were retained as products 
can still be identified by `StockCode`.

---

## 3. Duplicate Records

- **Total Duplicates Found:** {dup_count:,} ({dup_pct:.2f}%)
- **Action:** All exact duplicate rows were removed to prevent inflated metrics.

---

## 4. Invalid Values

### 4.1 Negative Quantity
- **Count:** {neg_qty:,} records
- **Interpretation:** Negative quantities represent cancelled or returned orders
  (invoices prefixed with 'C')
- **Action:** Removed — these are not valid sales transactions

### 4.2 Non-Positive Price
- **Count:** {bad_price:,} records  
- **Interpretation:** Price ≤ 0 is logically invalid for sales transactions
- **Action:** Removed — invalid pricing data

---

## 5. Data Transformations Applied

### 5.1 Type Conversions
- `InvoiceDate`: string → `datetime64` (enables time-series analysis)
- `Customer ID`: float → `int` (removes unnecessary decimal notation)

### 5.2 Text Standardization
- `Description`: trimmed whitespace + converted to UPPERCASE
- `Country`: trimmed whitespace + converted to Title Case

### 5.3 Feature Engineering
| New Column    | Formula / Logic                | Purpose                    |
|---------------|-------------------------------|----------------------------|
| `TotalAmount` | `Quantity × Price`            | Revenue per line item      |
| `Year`        | Extracted from `InvoiceDate`  | Year-over-year analysis    |
| `Month`       | Extracted from `InvoiceDate`  | Seasonal trends            |
| `DayOfWeek`   | Extracted from `InvoiceDate`  | Weekly shopping patterns   |
| `Hour`        | Extracted from `InvoiceDate`  | Hourly traffic analysis    |

---

## 6. Cleaning Pipeline Summary

| Step | Action                                | Rows Removed | Rows Remaining |
|------|---------------------------------------|-------------|----------------|
"""

    # Calculate values
    raw_rows = len(df_raw)
    clean_rows = len(df_clean)
    dup_count = int(df_raw.duplicated().sum())
    dup_pct = (dup_count / raw_rows) * 100
    cust_null = int(df_raw["Customer ID"].isnull().sum())
    cust_pct = (cust_null / raw_rows) * 100
    desc_null = int(df_raw["Description"].isnull().sum())
    desc_pct = (desc_null / raw_rows) * 100
    neg_qty = int((df_raw["Quantity"] < 0).sum())
    neg_qty_pct = (neg_qty / raw_rows) * 100
    bad_price = int((df_raw["Price"] <= 0).sum())
    bad_price_pct = (bad_price / raw_rows) * 100
    retain_pct = (clean_rows / raw_rows) * 100

    report = report.format(
        gen_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        raw_rows=raw_rows,
        clean_rows=clean_rows,
        dup_count=dup_count,
        dup_pct=dup_pct,
        cust_null=cust_null,
        cust_pct=cust_pct,
        desc_null=desc_null,
        desc_pct=desc_pct,
        neg_qty=neg_qty,
        neg_qty_pct=neg_qty_pct,
        bad_price=bad_price,
        bad_price_pct=bad_price_pct,
        retain_pct=retain_pct,
    )

    # Add cleaning steps
    for i, log_entry in enumerate(cleaning_log, 1):
        report += f"| {i}    | {log_entry} | — | — |\n"

    report += f"""
**Final Result:** {raw_rows:,} → {clean_rows:,} records ({retain_pct:.1f}% retained)

---

## 7. Final Dataset Profile

```
Columns: {len(df_clean.columns)}
Rows:    {clean_rows:,}
Nulls:   {df_clean.isnull().sum().sum()}
Duplicates: {df_clean.duplicated().sum()}
```

---

*This report was auto-generated by the data cleaning pipeline.*
"""

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  ✔ Quality Report saved to: {REPORT_PATH}")


# =============================================================================
#  MAIN PIPELINE
# =============================================================================
def main():
    """Execute the complete data wrangling pipeline."""

    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " DATA IMMERSION & WRANGLING PIPELINE ".center(68) + "║")
    print("║" + " Online Retail Dataset ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    # ── Load Raw Data ──
    print(f"\n  Loading raw data from: {RAW_DATA_PATH}")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"  ✖ ERROR: File not found at {RAW_DATA_PATH}")
        sys.exit(1)

    df_raw = pd.read_csv(RAW_DATA_PATH)
    print(f"  ✔ Loaded {len(df_raw):,} records with {len(df_raw.columns)} columns")

    # Keep a copy of raw data for reporting
    df = df_raw.copy()

    # ── Step 1: Data Familiarization ──
    df = step1_data_familiarization(df)

    # ── Step 2: Data Quality Assessment ──
    df, issues = step2_data_quality_assessment(df)

    # ── Step 3: Data Cleaning & Transformation ──
    df_clean, cleaning_log = step3_data_cleaning(df)

    # ── Save Cleaned Dataset ──
    print_header("SAVING OUTPUTS")
    df_clean.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"  ✔ Cleaned dataset saved to: {CLEANED_DATA_PATH}")
    print(f"    → {len(df_clean):,} records × {len(df_clean.columns)} columns")
    file_size = os.path.getsize(CLEANED_DATA_PATH) / (1024 * 1024)
    print(f"    → File size: {file_size:.1f} MB")

    # ── Generate Data Dictionary ──
    generate_data_dictionary(df_raw, df_clean)

    # ── Generate Quality Report ──
    generate_quality_report(df_raw, df_clean, issues, cleaning_log)

    # ── Final Summary ──
    print_header("✅ PIPELINE COMPLETE")
    print(f"  📁 Cleaned Data:    {CLEANED_DATA_PATH}")
    print(f"  📖 Data Dictionary: {DATA_DICT_PATH}")
    print(f"  📊 Quality Report:  {REPORT_PATH}")
    print(f"\n  Records: {len(df_raw):,} (raw) → {len(df_clean):,} (clean)")
    print(f"  Columns: {len(df_raw.columns)} (raw) → {len(df_clean.columns)} (clean)")
    print()


if __name__ == "__main__":
    main()
