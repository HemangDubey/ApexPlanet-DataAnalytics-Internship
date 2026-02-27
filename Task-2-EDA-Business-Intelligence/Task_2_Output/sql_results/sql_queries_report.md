# SQL Business Questions Report

> Generated on `2026-02-27 16:47:39`

---

## Q1: What are the top 5 products by total revenue?

**SQL Query:**
```sql
SELECT description AS product,
                           ROUND(SUM(quantity * price), 2) AS total_revenue,
                           SUM(quantity) AS total_qty_sold,
                           COUNT(DISTINCT invoice) AS num_orders
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY description
                    ORDER BY total_revenue DESC
                    LIMIT 5;
```

**Result:**

| product                            |   total_revenue |   total_qty_sold |   num_orders |
|:-----------------------------------|----------------:|-----------------:|-------------:|
| Manual                             |          339615 |             9635 |          789 |
| REGENCY CAKESTAND 3 TIER           |          330590 |            26478 |         3918 |
| DOTCOM POSTAGE                     |          309854 |             1415 |         1415 |
| WHITE HANGING HEART T-LIGHT HOLDER |          260990 |            94658 |         5455 |
| PAPER CRAFT , LITTLE BIRDIE        |          168470 |            80995 |            1 |

---

## Q2: What is the monthly revenue trend?

**SQL Query:**
```sql
SELECT SUBSTR(invoice_date, 1, 7) AS month,
                           ROUND(SUM(quantity * price), 2) AS monthly_revenue,
                           COUNT(DISTINCT invoice) AS num_invoices,
                           COUNT(DISTINCT customer_id) AS unique_customers
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY month
                    ORDER BY month;
```

**Result:**

| month   |   monthly_revenue |   num_invoices |   unique_customers |
|:--------|------------------:|---------------:|-------------------:|
| 2009-12 |  822484           |           1682 |                955 |
| 2010-01 |  651155           |           1105 |                721 |
| 2010-02 |  551878           |           1202 |                773 |
| 2010-03 |  830915           |           1681 |               1058 |
| 2010-04 |  678875           |           1462 |                943 |
| 2010-05 |  657706           |           1500 |                967 |
| 2010-06 |  749537           |           1645 |               1041 |
| 2010-07 |  648810           |           1529 |                929 |
| 2010-08 |  695252           |           1425 |                911 |
| 2010-09 |  921697           |           1839 |               1145 |
| 2010-10 |       1.1619e+06  |           2301 |               1497 |
| 2010-11 |       1.46429e+06 |           2747 |               1607 |
| 2010-12 |  821453           |           1559 |                886 |
| 2011-01 |  689812           |           1086 |                742 |
| 2011-02 |  522546           |           1100 |                759 |
| 2011-03 |  716215           |           1454 |                975 |
| 2011-04 |  536968           |           1246 |                857 |
| 2011-05 |  769297           |           1681 |               1057 |
| 2011-06 |  760547           |           1533 |                992 |
| 2011-07 |  718076           |           1475 |                950 |
| 2011-08 |  757841           |           1361 |                936 |
| 2011-09 |       1.05644e+06 |           1837 |               1267 |
| 2011-10 |       1.15126e+06 |           2040 |               1364 |
| 2011-11 |       1.50387e+06 |           2769 |               1665 |
| 2011-12 |  637808           |            819 |                616 |

---

## Q3: Which countries contribute the most revenue (Top 10)?

**SQL Query:**
```sql
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
```

**Result:**

| country        |    total_revenue |   unique_customers |   num_orders |   revenue_pct |
|:---------------|-----------------:|-------------------:|-------------:|--------------:|
| United Kingdom |      1.74106e+07 |               5350 |        36536 |         85.03 |
| EIRE           | 658767           |                  6 |          626 |          3.22 |
| Netherlands    | 554038           |                 22 |          228 |          2.71 |
| Germany        | 425020           |                107 |          789 |          2.08 |
| France         | 350456           |                 96 |          622 |          1.71 |
| Australia      | 169283           |                 15 |           95 |          0.83 |
| Spain          | 108332           |                 41 |          154 |          0.53 |
| Switzerland    | 100686           |                 23 |           93 |          0.49 |
| Sweden         |  91869.8         |                 20 |          105 |          0.45 |
| Denmark        |  68580.7         |                 12 |           43 |          0.33 |

---

## Q4: Who are the top 10 customers by total spend?

**SQL Query:**
```sql
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
```

**Result:**

|   customer_id |      total_spend |   num_orders |   avg_order_value |
|--------------:|-----------------:|-------------:|------------------:|
|         15255 |      3.10554e+06 |         3118 |             13.58 |
|         18102 | 580987           |          145 |            558.64 |
|         14646 | 528603           |          151 |            137.34 |
|         14156 | 313438           |          156 |             77.62 |
|         14911 | 291421           |          398 |             26.31 |
|         17450 | 244784           |           51 |            582.82 |
|         13694 | 195641           |          143 |            128.8  |
|         17511 | 172133           |           60 |             92.15 |
|         16446 | 168472           |            2 |          56157.5  |
|         16684 | 147143           |           55 |            204.93 |

---

## Q5: What is the average order value by country?

**SQL Query:**
```sql
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
```

**Result:**

| country     |   total_orders |   total_revenue |   avg_order_value |
|:------------|---------------:|----------------:|------------------:|
| Netherlands |            228 |        554038   |           2429.99 |
| Singapore   |             11 |         25317.1 |           2301.55 |
| Australia   |             95 |        169283   |           1781.93 |
| Denmark     |             43 |         68580.7 |           1594.9  |
| Hong Kong   |             15 |         23685.5 |           1579.03 |
| Japan       |             33 |         43023.9 |           1303.75 |
| Norway      |             45 |         56322.5 |           1251.61 |
| Israel      |             10 |         11328.8 |           1132.88 |
| Switzerland |             93 |        100686   |           1082.64 |
| Greece      |             18 |         19096.2 |           1060.9  |

---

## Q6: What are the peak shopping hours?

**SQL Query:**
```sql
SELECT CAST(SUBSTR(invoice_date, 12, 2) AS INTEGER) AS hour_of_day,
                           COUNT(*) AS num_transactions,
                           ROUND(SUM(quantity * price), 2) AS total_revenue,
                           ROUND(AVG(quantity * price), 2) AS avg_transaction_value
                    FROM transactions
                    WHERE quantity > 0 AND price > 0
                    GROUP BY hour_of_day
                    ORDER BY hour_of_day;
```

**Result:**

|   hour_of_day |   num_transactions |    total_revenue |   avg_transaction_value |
|--------------:|-------------------:|-----------------:|------------------------:|
|             6 |                  1 |      4.25        |                    4.25 |
|             7 |               1054 |  75765.6         |                   71.88 |
|             8 |              15527 | 528559           |                   34.04 |
|             9 |              65840 |      1.76963e+06 |                   26.88 |
|            10 |              88264 |      2.58113e+06 |                   29.24 |
|            11 |             114211 |      2.53533e+06 |                   22.2  |
|            12 |             150992 |      2.85038e+06 |                   18.88 |
|            13 |             142660 |      2.54847e+06 |                   17.86 |
|            14 |             132874 |      2.32168e+06 |                   17.47 |
|            15 |             128024 |      2.39494e+06 |                   18.71 |
|            16 |              88655 |      1.57014e+06 |                   17.71 |
|            17 |              54203 | 861460           |                   15.89 |
|            18 |              15529 | 273405           |                   17.61 |
|            19 |               8182 | 126830           |                   15.5  |
|            20 |               1898 |  38904.2         |                   20.5  |

---

## Q7: What is the cancellation rate and revenue lost?

**SQL Query:**
```sql
SELECT
                        COUNT(CASE WHEN quantity < 0 THEN 1 END) AS cancelled_items,
                        COUNT(*) AS total_items,
                        ROUND(COUNT(CASE WHEN quantity < 0 THEN 1 END) * 100.0 / COUNT(*), 2) AS cancel_rate_pct,
                        ROUND(ABS(SUM(CASE WHEN quantity < 0 THEN quantity * price ELSE 0 END)), 2) AS revenue_lost,
                        ROUND(SUM(CASE WHEN quantity > 0 THEN quantity * price ELSE 0 END), 2) AS revenue_earned
                    FROM transactions;
```

**Result:**

|   cancelled_items |   total_items |   cancel_rate_pct |   revenue_lost |   revenue_earned |
|------------------:|--------------:|------------------:|---------------:|-----------------:|
|             22496 |   1.03304e+06 |              2.18 |    1.46242e+06 |       2.0318e+07 |

---
