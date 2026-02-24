# 🧹 Task 1 — Data Immersion & Wrangling

**Apex Planet Data Analytics Internship**  
**Timeline:** 10 Days | **Dataset:** Online Retail Transaction Data

---

## 📌 Objective

Rapidly acquire, clean, and prepare the **Online Retail Dataset** for analysis — mastering the critical first step of any data analytics project: **Data Wrangling**.

---

## 📂 Project Structure

```
Data_Immersion_Wrangling/
├── data/
│   ├── raw_data.csv              # Original dataset (1,067,371 records)
│   └── cleaned_data.csv          # Cleaned dataset (779,425 records)
├── docs/
│   ├── data_dictionary.md        # Comprehensive data dictionary
│   └── data_quality_report.md    # Data quality assessment report
├── notebooks/
│   └── data_cleaning.ipynb       # Jupyter notebook (reference)
├── scripts/
│   └── data_cleaning.py          # Python cleaning pipeline script
└── README.md                     # This file
```

---

## 🔍 Dataset Overview

| Attribute         | Value                             |
|-------------------|-----------------------------------|
| **Dataset Name**  | Online Retail Transaction Data    |
| **Source**        | UCI Machine Learning Repository   |
| **Records (Raw)**| 1,067,371                         |
| **Records (Clean)**| 779,425 (73.0% retained)        |
| **Columns (Raw)**| 8                                 |
| **Columns (Clean)**| 13 (5 engineered features)      |
| **Time Period**   | Dec 2009 – Dec 2011               |
| **Geography**     | 41 countries                      |

---

## 🛠️ Steps Completed

### Step 1: Data Access & Familiarization
- Loaded the raw CSV dataset (94.8 MB, 1,067,371 rows)
- Explored dataset shape, data types, and statistical summaries
- Identified 8 columns: `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price`, `Customer ID`, `Country`
- Created a comprehensive **[Data Dictionary](docs/data_dictionary.md)**

### Step 2: Data Quality Assessment
- **Missing Values**: `Customer ID` (243,007 / 22.77%) and `Description` (4,382 / 0.41%)
- **Duplicates**: 34,335 exact duplicate records (3.22%)
- **Negative Quantity**: 22,950 records (cancelled/returned transactions)
- **Non-positive Price**: 6,207 records (invalid pricing)
- **Inconsistent Text**: Mixed casing in Description column
- **Cancelled Invoices**: Invoices prefixed with 'C'
- Full findings in the **[Data Quality Report](docs/data_quality_report.md)**

### Step 3: Data Cleaning & Transformation

| Cleaning Action                              | Impact                  |
|----------------------------------------------|-------------------------|
| Removed duplicate records                    | -34,335 rows            |
| Removed non-positive quantity (cancellations)| -22,496 rows            |
| Removed non-positive price (invalid)         | -2,626 rows             |
| Removed missing Customer ID                  | -228,489 rows           |
| **Total removed**                            | **287,946 rows (27%)**  |

**Transformations Applied:**
- `InvoiceDate` → converted from string to `datetime64`
- `Customer ID` → converted from `float` to `int`
- `Description` → standardized to UPPERCASE, trimmed whitespace
- `Country` → standardized to Title Case, trimmed whitespace

**Feature Engineering:**
| New Column    | Formula                        | Purpose                   |
|---------------|-------------------------------|---------------------------|
| `TotalAmount` | `Quantity × Price`            | Revenue per line item     |
| `Year`        | Extracted from `InvoiceDate`  | Year-over-year analysis   |
| `Month`       | Extracted from `InvoiceDate`  | Seasonal trend analysis   |
| `DayOfWeek`   | Extracted from `InvoiceDate`  | Weekly shopping patterns  |
| `Hour`        | Extracted from `InvoiceDate`  | Hourly traffic analysis   |

---

## 🚀 How to Run

### Prerequisites
- Python 3.8+
- pandas (`pip install pandas`)

### Execute the Pipeline
```bash
cd Data_Immersion_Wrangling
python scripts/data_cleaning.py
```

This will:
1. Load and profile the raw dataset
2. Perform data quality assessment
3. Clean and transform the data
4. Save `cleaned_data.csv` to `data/`
5. Generate `data_dictionary.md` and `data_quality_report.md` in `docs/`

---

## 📊 Deliverables

| Deliverable           | File                              | Description                                    |
|-----------------------|-----------------------------------|------------------------------------------------|
| 📖 Data Dictionary    | `docs/data_dictionary.md`        | Column definitions, types, business relevance  |
| 📊 Quality Report     | `docs/data_quality_report.md`    | Complete profiling & issues analysis           |
| 🧹 Cleaning Script    | `scripts/data_cleaning.py`       | Automated cleaning & transformation pipeline   |
| 📁 Cleaned Dataset    | `data/cleaned_data.csv`          | Analysis-ready dataset (779,425 records)       |

---

## 📈 Final Dataset Summary

```
Records:    779,425 (from 1,067,371 raw)
Columns:    13 (8 original + 5 engineered)
Nulls:      0
Duplicates: 0
```

| Column        | Min     | Max          | Mean    | Median  |
|---------------|---------|--------------|---------|---------|
| Quantity      | 1       | 80,995       | 13.49   | 6.0     |
| Price (£)     | 0.001   | 10,953.50    | 3.22    | 1.95    |
| TotalAmount(£)| 0.00    | 168,469.60   | 22.29   | 12.48   |

---

*Completed: February 2026 | Apex Planet Data Analytics Internship*
