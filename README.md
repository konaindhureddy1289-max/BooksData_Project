Books Data Pipeline (/data_pipeline)
An end-to-end raw-to-relational data pipeline that scrapes book data
from a public scraping-practice website, cleans it into typed columns,
converts GBP prices to INR using a fixed project baseline, loads the
results into a normalized SQLite database, and analyses the data with
SQL and pandas.

Data source: books.toscrape.com, a
public website built for scraping practice. No login or API key is
required.
1. Pipeline Overview
books.toscrape.com
      |
      v
scrape.py          requests + BeautifulSoup        -> books_raw.csv
      |
      v
clean_data.py      pandas cleaning + conversion    -> clean_books.csv
      |
      v
build_database.py  SQLite (2 tables, PK/FK)         -> books.db
      |                                                query_results.txt
      v
7 SQL queries + pd.read_sql + pd.merge comparison
2. Install and Run
Requirements: Python 3.12 or 3.13 and an internet connection for the
scraping step.
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run from inside the data_pipeline folder
python scrape.py
python clean_data.py
python build_database.py
requirements.txt:
requests
beautifulsoup4
pandas
lxml
sqlite3 is included with Python. Each script runs end to end, and the
scripts pass data to one another through CSV files.
  Script                  Reads                   Writes
  scrape.py             Website                 books_raw.csv

  clean_data.py         books_raw.csv         clean_books.csv

  build_database.py     clean_books.csv       books.db,
                                              query_results.txt
3. Task 1: Scraping
- Libraries: requests and BeautifulSoup.
- Scope: 71 books across 4 categories: Travel (11),
  Mystery (20), Historical Fiction (20) and Sequential Art
  (20). This exceeds the stated minimum of 60 books across at
  least 3 categories.
- Fields captured: title, price (GBP as listed), star_rating
  (text such as "Three"), availability (text as listed) and
  category.
- Encoding: The response encoding is set to UTF-8 so currency
  symbols and apostrophes are decoded correctly.
4. Task 2: Cleaning and Parsing Decisions
  Raw field         Cleaned field     Type              Decision
  price (text     price_gbp       float           Remove characters other than
  with currency                                         digits and the decimal point, then
  symbol)                                               use
                                                        pd.to_numeric(errors="coerce")

  star_rating     rating          int (1--5)      Map each word to its number;
  ("One" to                                           unknown values become missing
  "Five")                                             

  availability    in_stock        bool            True when text contains
  (text)                                                "in stock" (case-insensitive)
  title,          Same names        Text              Strip leading and trailing
  category                                            whitespace
Handling messy rows: Rows with an unparseable price or rating are
dropped rather than imputed. These fields are used in later analysis, so
median imputation would introduce synthetic values. Invalid values are
first converted to missing values, allowing the pipeline to handle them
without crashing.

Duplicates: Rows with the same title in the same category are
removed.

Cleaning outcome: 71 rows scraped, 0 dropped as unparseable, 0
duplicates removed, and 71 clean rows. The script also asserts that
price_gbp is a float, rating is an integer between 1 and 5, and
in_stock is a boolean.
5. Task 3: Currency Conversion
price_inr is calculated as price_gbp × 105.50, rounded to two
decimal places.
Fixed project baseline: 1 GBP = 105.50 INR. This is a
project-defined constant, not a live exchange rate. It has no date
reference and does not require an API call.

6. Task 4: Normalized SQLite Schema
Two tables are connected by a primary-key/foreign-key relationship, so
each category name is stored once.
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
The books.db database is committed in this folder. build_database.py
regenerates it from scratch by dropping and recreating both tables.
7. Task 5: SQL Queries
All seven query strings and their printed results are saved in
query_results.txt. Together, the queries demonstrate SELECT,
WHERE, ORDER BY, LIMIT, DISTINCT, IN, BETWEEN, JOIN,
GROUP BY, and aggregate functions.
  Query                   Clauses demonstrated    Question answered
  Q1                      SELECT, WHERE       Which five-star,
                                                  in-stock books cost
                                                  under £30?

  Q2                      ORDER BY, LIMIT     What are the five most
                                                  expensive books?

  Q3                      DISTINCT              Which star ratings
                                                  appear in the data?

  Q4                      BETWEEN, ORDER BY,  Which are the cheapest
                          LIMIT                 books priced from £20
                                                  to £30?

  Q5                      IN, ORDER BY,       Which books are rated
                          LIMIT                 four or five stars?

  Q6                      JOIN, GROUP BY,     What are the book
                          aggregates              count, average price
                                                  and average rating per
                                                  category?

  Q7                      JOIN                  What is each book's
                                                  category name? Used for
                                              the pandas comparison.
The Q6 query:
SELECT c.category_name,
       COUNT(*)                   AS book_count,
       ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp,
       ROUND(AVG(b.rating), 2)    AS avg_rating
FROM books b
JOIN categories c ON b.category_id = c.category_id
GROUP BY c.category_name
ORDER BY avg_price_gbp DESC;
Q6 output: category summary
The supplied project description does not include the four actual Q6
result rows, so category averages cannot be stated reliably from the
description alone. Run python build_database.py and copy the four rows
printed in query_results.txt into this table.

  Category                                         Book count   Average price (GBP)   Average rating
  Copy the first row from query_results.txt             ---                   ---              ---
  Copy the second row from query_results.txt            ---                   ---              ---
  Copy the third row from query_results.txt             ---                   ---              ---
  Copy the fourth row from query_results.txt            ---                   ---              ---
8. Task 6: pd.read_sql vs pd.merge
- All seven query results are read into pandas DataFrames using
  pd.read_sql(...).
- The Q7 SQL JOIN is reproduced by reading books and categories
  into separate DataFrames and combining them with
  pd.merge(books_df, categories_df, on="category_id").
- The project reports 71 rows from the SQL JOIN and 71 rows from
  pd.merge, with identical outputs (True) after sorting.
9. Key Findings
The supplied project description confirms the sample size, category
counts, cleaning outcome and SQL/pandas consistency. It does not
include the Q6 category averages or Q1 result count, so those findings
are intentionally not fabricated.

After running build_database.py, use query_results.txt to report: -
The category with the highest average price and its average price. - The
category with the highest average rating and its average rating. - The
number of five-star, in-stock books priced under £30 returned by Q1.

These findings describe this scraped sample only and should not be
generalised to the wider book market.
10. Folder Structure
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
11. Limitations
- The sample contains 71 books across four selected categories and
  is limited to the first listing page of each category used by the
  scraper.
- The INR column uses a fixed baseline rate of 105.50 INR per GBP,
  so it is not a live financial conversion.
- Rows with unparseable prices or ratings are dropped. This is
  suitable for this small exercise but would require closer monitoring
  for noisier real-world data.
- Website content can change, so scraping results may differ on a
  later run.
