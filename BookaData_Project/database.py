import pandas as pd
import sqlite3
df = pd.read_csv("clean_books.csv")
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

#create Categories table
cursor.execute("""
               CREATE TABLE IF NOT EXISTS Categories(
               Category_id INTEGER PRIMARY KEY AUTOINCREMENT,
               Category_name TEXT UNIQUE NOT NULL
               )
               """)

#create Books table
cursor.execute("""
               CREATE TABLE IF NOT EXISTS Books(
               Books_id INTEGER PRIMARY KEY AUTOINCREMENT,
               Title TEXT NOT NULL,
               Price_gbp REAL NOT NULL,
               Price_inr REAL NOT NULL,
               Rating INTEGER,
               Availability BOOLEAN,
               Category_id INTEGER,
               FOREIGN KEY(Category_id)
                REFERENCES Categories(Category_id)
               )""")

conn.commit()

#veify tables exist or not
cursor.execute("""
               SELECT NAME
               FROM sqlite_master
               WHERE type='table';
               """)
print(cursor.fetchall())


#Insert into tables

Categories = df["category"].unique()
for category in Categories:
    cursor.execute("""
                   INSERT OR IGNORE INTO Categories(category_name)
                   VALUES(?)
                   """ ,(category,))

conn.commit()
cursor.execute("SELECT * FROM Categories")
print(cursor.fetchall())
for _, row in df.iterrows():

    cursor.execute("""
        SELECT Category_id
        FROM Categories
        WHERE Category_name = ?
    """, (row["category"],))

    result = cursor.fetchone()

    if result is None:
        print("Category not found:", row["category"])
        continue

    category_id = result[0]

    cursor.execute("""
        INSERT INTO Books(
            Title,
            Price_gbp,
            Price_inr,
            Rating,
            Availability,
            Category_id
        )
        VALUES(?,?,?,?,?,?)
    """, (
        row["title"],
        row["price"],
        row["price_inr"],
        row["rating"],
        row["availability"],
        category_id
    ))
    conn.commit()

cursor.execute("SELECT COUNT(*) FROM Books")
print("Number of books:", cursor.fetchone()[0])

cursor.execute("""
SELECT *
FROM Books
LIMIT 5;
""")

print(cursor.fetchall())


cursor.execute("SELECT COUNT(*) FROM Categories")
print(cursor.fetchone())

cursor.execute("SELECT COUNT(*) FROM Books")
print(cursor.fetchone())

cursor.execute("SELECT * FROM Books LIMIT 5")
print(cursor.fetchall())
conn.close()