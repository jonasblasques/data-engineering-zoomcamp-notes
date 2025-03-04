# SQL Refresher

### Table of contents (under construction)


- [Window Funtions](#window-funtions)
    - [Row Number](#row-number)
- [Common Table Expression](#common-table-expression)



## Window Funtions    

A window function performs a calculation across a set of table rows that are related to the current row within a specific "window" or subset of data. This is comparable to the type of calculation that can be done with an aggregate function  (such as SUM(), AVG(), COUNT(), etc.).

But unlike regular aggregate functions, use of a window function does not cause rows to become grouped into a single output row — the rows retain their separate identities.

**Key Characteristics of Window Functions:**

Syntax:

```sql
FUNCTION() OVER (PARTITION BY column_name ORDER BY column_name)
```

A window function always has two components. This second part here defines your window:

```sql
OVER (PARTITION BY column_name ORDER BY column_name)
```

Your window here is how you want to be viewing your data when you're applying your function

- PARTITION BY: divides the result set into groups (optional).

- ORDER BY: defines the order of processing rows within the partition.


**Common Window Functions:**

Ranking Functions

- ROW_NUMBER(): Assigns a unique row number within a partition.
- RANK(): Similar to ROW_NUMBER(), but assigns the same rank to duplicate values, skipping numbers.
- DENSE_RANK(): Like RANK(), but without gaps in numbering.

Aggregate Functions as Window Functions

- SUM() OVER(): Computes a running total.
- AVG() OVER(): Computes a moving average.

Lag and Lead Functions

- LAG(): Retrieves the value from a previous row.
- LEAD(): Retrieves the value from the next row.




### Row Number

The ROW_NUMBER() window function in SQL assigns a unique sequential integer to rows within a partition of a result set. It is typically used to generate row numbers for each row in a query result, based on a specified ordering.

Syntax:

```sql
ROW_NUMBER() OVER (PARTITION BY column_name ORDER BY column_name)
```

Common Uses:

- Removing Duplicates: You can use ROW_NUMBER() to identify duplicate rows and keep only one by filtering out rows with a row number greater than 1.

- Ranking Data: Used when ranking rows based on specific criteria but requiring unique row numbers.

- Selecting the Latest Record: Helps in selecting the most recent entry per category when combined with PARTITION BY.

Example:

```sql

SELECT 
  total_amount,
  ROW_NUMBER() OVER (ORDER BY total_amount DESC) AS ranking

FROM `greentaxi_trips` 
LIMIT 10;

```

The query returns the top 10 highest total_amount values from the table, along with a row number indicating their ranking.


| Row | total_amount | ranking |
|----|--------|--------|
| 1  | 4012.3 | 1      |
| 2  | 2878.3 | 2      |
| 3  | 2438.8 | 3      |
| 4  | 2156.3 | 4      |
| 5  | 2109.8 | 5      |
| 6  | 2017.3 | 6      |
| 7  | 1971.05| 7      |
| 8  | 1958.8 | 8      |
| 9  | 1762.8 | 9      |
| 10 | 1600.8 | 10     |



## Common Table Expression

A CTE, short for Common Table Expression, is like a query within a query. With the WITH statement, you can create temporary tables to store results, making complex queries more readable and maintainable. These temporary tables exist only for the duration of the main query.

CTEs and subqueries are both powerful tools and can be used to achieve similar goals, but they have different use cases and advantages.

By declaring CTEs at the beginning of the query, you enhance code readability, enabling a clearer grasp of your analysis logic. Breaking down the query into smaller, more manageable components encourages effortless code maintenance and enhances comprehension.

Syntax:

```sql

WITH cte_name AS (
    SELECT column1, column2
    FROM some_table
    WHERE condition
)
SELECT * FROM cte_name;
```
