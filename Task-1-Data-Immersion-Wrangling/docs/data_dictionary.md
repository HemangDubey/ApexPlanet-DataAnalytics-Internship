# 📖 Data Dictionary — Online Retail Dataset

## Dataset Overview

| Attribute         | Value                                      |
|-------------------|---------------------------------------------|
| **Dataset Name**  | Online Retail Transaction Data              |
| **Source**         | UCI Machine Learning Repository             |
| **Format**         | CSV                                         |
| **Raw Records**    | 1,067,371                                |
| **Clean Records**  | 779,425                              |
| **Time Period**    | 2009-12-01 to 2011-12-09                    |
| **Geography**      | 41 countries                     |

---

## Column Descriptions (Raw Dataset)

| # | Column Name   | Data Type | Non-Null Count | Null Count | Null %  | Description                                                  | Business Relevance                            |
|---|---------------|-----------|----------------|------------|---------|--------------------------------------------------------------|-----------------------------------------------|
| 1 | `Invoice`     | object    | 1,067,371   | 0          | 0.00%   | 6-digit invoice number. Prefix 'C' = cancelled transaction  | Uniquely identifies each transaction          |
| 2 | `StockCode`   | object    | 1,067,371   | 0          | 0.00%   | 5-digit product/item code                                    | Identifies products for inventory analysis    |
| 3 | `Description` | object    | 1,062,989    | 4,382 | 0.41%  | Product name/description                       | Product categorization and search             |
| 4 | `Quantity`    | int64     | 1,067,371   | 0          | 0.00%   | Quantity of each product per transaction                      | Sales volume analysis                         |
| 5 | `InvoiceDate` | object    | 1,067,371   | 0          | 0.00%   | Date and time of invoice generation (MM/DD/YYYY HH:MM)       | Time-series and seasonal analysis             |
| 6 | `Price`       | float64   | 1,067,371   | 0          | 0.00%   | Unit price in GBP (£)                                        | Revenue calculation and pricing analysis      |
| 7 | `Customer ID` | float64   | 824,364    | 243,007 | 22.77%  | 5-digit unique customer identifier               | Customer segmentation and retention analysis  |
| 8 | `Country`     | object    | 1,067,371   | 0          | 0.00%   | Country where the customer resides                           | Geographic market analysis                    |

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
1. **Missing Values**: `Description` (4,382 nulls) and `Customer ID` (243,007 nulls)
2. **Duplicate Records**: 34,335 exact duplicate rows
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
| `Quantity`    | 1  | 80,995    | 13.49 | 6.0 |
| `Price`       | £0.001 | £10,953.50 | £3.22 | £1.95 |
| `TotalAmount` | £0.00 | £168,469.60 | £22.29 | £12.48 |

---

*Generated on: 2026-02-24 22:48:38*
