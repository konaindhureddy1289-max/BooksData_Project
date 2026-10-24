import pandas as pd
import sqlite3
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

#Queries

query1 = """
SELECT Title,Rating
FROM Books
WHERE Rating =5;
"""
df1 = pd.read_sql_query(query1, conn)
print("Query 1")
print(df1)

query2 = """
SELECT Title,Price_inr
FROM Books
ORDER BY Price_inr DESC;
"""
cursor.execute(query2)
print("Query 2")
print(cursor.fetchall())

query3 = """
SELECT Title,Price_inr
FROM Books
ORDER BY Price_inr DESC
LIMIT 5;
"""
cursor.execute(query3)
print("Query 3")
print(cursor.fetchall())

query4 = """
SELECT DISTINCT Category_name
FROM Categories;
"""
cursor.execute(query4)
print("Query 4")
print(cursor.fetchall())

query5 = """
SELECT Title,Price_inr
FROM Books
WHERE Price_inr BETWEEN 2000 AND 5000;
"""
cursor.execute(query5)
print("Query 5")
print(cursor.fetchall())

query6 = """
SELECT
b.Title,
c.Category_name,
b.Rating,
b.Price_inr
FROM Books b
INNER JOIN Categories c
ON b.Category_id = c.Category_id
ORDER BY b.Rating DESC
"""
df_query6 = pd.read_sql_query(query6, conn)
print("Query 6")
print(df_query6)
sql_join_df = pd.read_sql_query(query6, conn)

books_df = pd.read_sql_query("SELECT * FROM Books", conn)

categories_df = pd.read_sql_query("SELECT * FROM Categories", conn)


merged_df = pd.merge(
    books_df,
    categories_df,
    on="Category_id",
    how="inner"
)

merged_df = merged_df[
    [
        "Title",
        "Category_name",
        "Rating",
        "Price_inr"
    ]
]
sql_join_df = sql_join_df.sort_values(
    by=["Rating", "Title"],
    ascending=[False, True]
).reset_index(drop=True)

merged_df = merged_df.sort_values(
    by=["Rating", "Title"],
    ascending=[False, True]
).reset_index(drop=True)

print(sql_join_df.equals(merged_df))
conn.close()