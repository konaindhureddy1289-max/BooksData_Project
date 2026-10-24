from scrape import all_book
import pandas as pd
df=pd.DataFrame(all_book)
print(df.head())
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df["title"]=df["title"].str.strip()
df["category"]=df["category"].str.strip()
df["availability"]=df["availability"].str.strip()

df["price"]=df["price"].str.replace("Â£" ," " ,regex=False)
df["price"]=df["price"].astype(float)

rating_map = {
  "One" : 1,
  "Two" : 2,
  "Three" : 3,
  "Four" : 4,
  "Five" :5
  }
df["rating"]=df["rating"].map(rating_map)
df["availability"] = df["availability"].str.contains("In stock")


print(df.head())
print(df.info())
print(df.isnull().sum())


df["price_inr"]=(df["price"]*105.50).round(2)
print(df[["price", "price_inr"]].head())

df.to_csv("clean_books.csv", index=False)