from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'en-US,en;q=0.9'
}

PRODUCTS = {
    "iPhone 14 (128GB)": {
        "amazon":  "https://www.amazon.in/s?k=iphone+14+128gb",
        "flipkart":"https://www.flipkart.com/search?q=iphone+14+128gb"
    },
    "Samsung Galaxy S23": {
        "amazon":  "https://www.amazon.in/s?k=samsung+galaxy+s23",
        "flipkart":"https://www.flipkart.com/search?q=samsung+galaxy+s23"
    },
    "Redmi Note 13 Pro": {
        "amazon":  "https://www.amazon.in/s?k=redmi+note+13+pro",
        "flipkart":"https://www.flipkart.com/search?q=redmi+note+13+pro"
    }
}

def scrape_amazon(url):
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        product = soup.find('div', {'data-component-type': 's-search-result'})
        title = product.h2.text.strip() if product and product.h2 else "No title"
        price_tag = product.find('span', class_='a-price-whole')
        rating_tag = product.find('span', class_='a-icon-alt')

        price = f"₹{price_tag.text.strip()}" if price_tag else "N/A"
        rating = rating_tag.text.strip() if rating_tag else "No rating"

        return {"title": title, "price": price, "rating": rating}
    except Exception as e:
        print(f"Amazon error: {e}")
        return {"title": "Not found", "price": "N/A", "rating": "N/A"}

def scrape_flipkart(url):
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        products = soup.find_all('div', {'class': '_1AtVbE'})
        for product in products:
            title_tag = product.find('div', class_='_4rR01T') or product.find('a', class_='s1Q9rs')
            price_tag = product.find('div', class_='_30jeq3')
            rating_tag = product.find('div', class_='_3LWZlK')

            if title_tag and price_tag:
                title = title_tag.text.strip()
                price = price_tag.text.strip()
                rating = rating_tag.text.strip() if rating_tag else "No rating"
                return {"title": title, "price": price, "rating": rating}

        return {"title": "Not found", "price": "N/A", "rating": "N/A"}
    except Exception as e:
        print(f"Flipkart error: {e}")
        return {"title": "Not found", "price": "N/A", "rating": "N/A"}

@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS.keys())

@app.route('/compare', methods=['POST'])
def compare():
    product = request.form.get('product')
    urls = PRODUCTS.get(product, {})
    amazon_data = scrape_amazon(urls.get('amazon', ''))
    flipkart_data = scrape_flipkart(urls.get('flipkart', ''))
    return render_template('compare.html',
                           product=product,
                           amazon=amazon_data,
                           flipkart=flipkart_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

