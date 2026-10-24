from bs4 import BeautifulSoup
import requests
url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")
categories = soup.select(".side_categories ul li a")[1:5]

all_book = []
for category in categories:
  name = category.get_text(strip=True)
  link = "https://books.toscrape.com/" +category["href"]

  response = requests.get(link)
  soup = BeautifulSoup(response.text,"html.parser")
  books = soup.find_all("article",class_="product_pod")

  for book in books:
    title = book.h3.a["title"]
    price = book.find("p",class_="price_color").text
    rating = book.find("p",class_="star-rating")["class"][1]
    availability = book.find("p",class_="instock availability").text.strip()
    print(f"Title: {title} | Price: {price} | Rating: {rating} | Availability: {availability}","category:",name)
    book_data = {
        'title': title,
        'price': price,
        'rating': rating,
        'availability': availability,
        'category': name
    }
    all_book.append(book_data)
     
