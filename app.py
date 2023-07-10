from flask import Flask, render_template, request, redirect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import sqlite3

app = Flask(__name__)

options = Options()
options.add_argument("--headless")
service = Service("C:/Users/Dell/Desktop/WebScrapping/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

def store_links_in_database(links):
    # Connect to the SQLite database
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()

    # Create a table to store the links if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT
        )
    ''')

    # Insert the links into the database
    for link_url in links:
        cursor.execute('INSERT INTO links (link) VALUES (?)', (link_url,))
    conn.commit()  # Commit the transaction to update the database

    # Close the database connection
    cursor.close()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    base_url = url.rstrip('/')

    driver.get(url)

    total_duration = 5
    scroll_interval = 1

    scroll_actions = total_duration // scroll_interval

    for i in range(scroll_actions):
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    links = soup.find_all('a')
    link_urls = []
    for link in links:
        if 'href' in link.attrs:
            absolute_url = urljoin(base_url, link['href'])
            if absolute_url.startswith(base_url):
                link_urls.append(absolute_url)

    # Store the links in the database
    store_links_in_database(link_urls)

    return render_template('result.html', links=link_urls)

@app.route('/post-link', methods=['POST'])
def post_link():
    link = request.form['link']
    store_links_in_database([link])
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
