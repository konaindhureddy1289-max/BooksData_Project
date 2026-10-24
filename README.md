# Data Pipeline (`/data_pipeline`)

A raw-to-relational data pipeline: scrape live product data from a public scraping-practice site, clean it into proper types, convert prices with a fixed baseline rate, load it into a normalized SQLite database, and query it with both SQL and pandas.

**Data source:** [books.toscrape.com](https://books.toscrape.com), a public website built for scraping practice (no login or API key required).

---

## 1. Pipeline Overview

```
books.toscrape.com
      |
      v
scrape.py          requests + BeautifulSoup        ->  books_raw.csv
      |
      v
clean_data.py      pandas cleaning + conversion    ->  clean_books.csv
      |
      v
build_database.py  SQLite (2 tables, PK/FK)        ->  books.db
      |                                                query_results.txt
      v
7 SQL queries  +  pd.read_sql  +  pd.merge comparison
```

## 2. Install and Run

**Requirements:** Python 3.12 or 3.13 and an internet connection for the scraping step.

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline in order, from inside the data_pipeline folder
python scrape.py
python clean_data.py
python build_database.py
```

`requirements.txt`:

```
requests
beautifulsoup4
pandas
lxml
```

`sqlite3` ships with Python. Each script runs end to end with no manual copy-pasting, and the three steps hand data to each other through CSV files.

| Script | Reads | Writes |
|---|---|---|
| `scrape.py` | the website | `books_raw.csv` |
| `clean_data.py` | `books_raw.csv` | `clean_books.csv` |
| `build_database.py` | `clean_books.csv` | `books.db`, `query_results.txt` |

## 3. Task 1: Scraping

- **Libraries:** `requests` and `BeautifulSoup`.
- **Scope:** [71] books across [4] categories: Travel ([11]), Mystery ([20]), Historical Fiction ([20]) and Sequential Art ([20]). This meets the minimum of 60 books across at least 3 categories.
- **Fields captured per book:** `title`, `price` (as listed, in GBP), `star_rating` (as text, for example "Three"), `availability` (as listed text) and `category`.
- **Encoding:** the response encoding is set to UTF-8 so the pound sign and apostrophes are read correctly instead of appearing as `Â£` or `â`.

## 4. Task 2: Cleaning and Parsing Decisions

| Raw field | Cleaned field | Type | Decision |
|---|---|---|---|
| `price` (text with currency symbol) | `price_gbp` | `float` | Remove every character except digits and the decimal point, then convert with `pd.to_numeric(errors="coerce")`, so a bad value becomes NaN instead of crashing the pipeline |
| `star_rating` ("One" to "Five") | `rating` | `int` (1 to 5) | Map each word to its number; an unknown word becomes NaN |
| `availability` (text) | `in_stock` | `bool` | `True` when the text contains "in stock" (case-insensitive) |
| `title`, `category` | same | text | Strip leading and trailing whitespace |

**Handling messy rows: drop, do not impute.** If a row's price or rating cannot be parsed, the row is dropped. Both fields are the quantities analysed later, so filling a gap with a median would create invented values that distort the averages reported below. The pipeline also does not crash: unparseable values are converted to NaN first and removed in one step.

**Duplicates:** rows with the same title in the same category are removed.

**Cleaning outcome:** [71] rows scraped, [0] dropped as unparseable, [0] duplicates removed, [71] clean rows. The script also asserts that `price_gbp` is a float, `rating` is an integer between 1 and 5, and `in_stock` is a boolean.

## 5. Task 3: Currency Conversion

`price_inr` is computed as `price_gbp × 105.50`, rounded to 2 decimals.

> **Fixed baseline rate used: 1 GBP = 105.50 INR.** This is a project-defined constant. It is not a live exchange rate, has no date reference, and requires no API call or network access.

## 6. Task 4: Normalized SQLite Schema

Two tables joined by a primary key and foreign key, so each category name is stored once.

```sql
CREATE TABLE categories (
    category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE books (
    book_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    price_gbp   REAL    NOT NULL,
    price_inr   REAL    NOT NULL,
    rating      INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    in_stock    INTEGER NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories (category_id)
);
```

The database file `books.db` is committed in this folder, and `build_database.py` regenerates it from scratch (it drops and recreates both tables on each run).

## 7. Task 5: SQL Queries

Every query string and its printed output is saved in **`query_results.txt`**. Together they cover `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `IN`, `BETWEEN` and `JOIN`.

| # | Clauses demonstrated | Question answered |
|---|---|---|
| Q1 | `SELECT`, `WHERE` | Which five-star, in-stock books cost under £30? |
| Q2 | `ORDER BY`, `LIMIT` | What are the 5 most expensive books? |
| Q3 | `DISTINCT` | Which star ratings appear in the data? |
| Q4 | `BETWEEN`, `ORDER BY`, `LIMIT` | Which are the cheapest books priced from £20 to £30? |
| Q5 | `IN`, `ORDER BY`, `LIMIT` | Which books are rated 4 or 5 stars? |
| Q6 | `JOIN`, `GROUP BY`, aggregates | What are the book count, average price and average rating per category? |
| Q7 | `JOIN` | Every book with its category name (used for the pandas comparison) |

The JOIN query behind Q6:

```sql
SELECT c.category_name,
       COUNT(*)                   AS book_count,
       ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp,
       ROUND(AVG(b.rating), 2)    AS avg_rating
FROM books b
JOIN categories c ON b.category_id = c.category_id
GROUP BY c.category_name
ORDER BY avg_price_gbp DESC;
```

Q6 output:

| category_name | book_count | avg_price_gbp | avg_rating |
|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] |
| [ ] | [ ] | [ ] | [ ] |
| [ ] | [ ] | [ ] | [ ] |
| [ ] | [ ] | [ ] | [ ] |

## 8. Task 6: `pd.read_sql` vs `pd.merge`

- All seven query results are read back into pandas DataFrames with `pd.read_sql(...)`.
- The Q7 JOIN is reproduced a second way: the `books` and `categories` tables are read into DataFrames and combined with `pd.merge(books_df, categories_df, on="category_id")`, with no SQL join.
- Both outputs are printed side by side in `query_results.txt`, and the script checks them for equality after sorting.

Result: SQL JOIN returned [71] rows, `pd.merge` returned [71] rows, and **outputs identical: [True]**.

## 9. Key Findings

- [Finding 1 from Q6: which category has the highest average price, with the number.]
- [Finding 2: which category has the highest average rating.]
- [Finding 3 from Q1: how many five-star, in-stock books cost under £30.]

These describe this sample of the catalogue only and should not be generalised to the wider book market.

## 10. Folder Structure

```
data_pipeline/
├── scrape.py
├── clean_data.py
├── build_database.py
├── books_raw.csv
├── clean_books.csv
├── books.db
├── query_results.txt
├── requirements.txt
└── README.md
```

## 11. Limitations

- The sample is small ([71] books) and covers only [the first listing page of each of 4 categories].
- The INR column uses a fixed baseline rate for the exercise, so it is not a real financial conversion.
- Rows with unparseable prices or ratings are dropped, which is appropriate for a small, clean source but would need review for a noisier real-world source.
