# app.py
from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    # Fetch data from another website (replace 'example.com' with the actual URL)
    url = 'https://www.hillspet.nl/about-us/nutritional-philosophy/ingredients'
    response = requests.get(url)

    if response.status_code == 200:
        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the heading using a simplified selector
        heading = soup.select_one('#content .categories-list')

        # Get the text content of the heading
        heading_text = heading if heading else "Heading not found"

        # Extract the text content of the <p> element using a simplified selector
        paragraph_text = soup.select_one('#content > div > div > div > div:nth-child(1) > div > div > div > section > div > section:nth-child(1) > div > div.ingredients-columns-container.col-md-8.cl-xs-12 > div.col-sm-6.first > div:nth-child(1) > div > div > div > p')

        # Get the text content of the paragraph
        paragraph_text = paragraph_text if paragraph_text else "Paragraph not found"

    print(heading_text, paragraph_text)
    return render_template('home.html', heading_text=heading_text, paragraph_text = paragraph_text)

if __name__ == '__main__':
    app.run(debug=True)