from flask import Flask, render_template, request
import sqlite3
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def store_paragraphs_in_database(paragraphs):
    # Connect to the SQLite database
    conn = sqlite3.connect('paragraphs.db')
    cursor = conn.cursor()

    # Create a table to store the paragraphs if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paragraph TEXT
        )
    ''')

    # Insert the paragraphs into the database
    for paragraph in paragraphs:
        cursor.execute('INSERT INTO paragraphs (paragraph) VALUES (?)', (paragraph,))
    conn.commit()  # Commit the transaction to update the database

    # Close the database connection
    cursor.close()
    conn.close()

@app.route('/')
def home():
    return render_template('index_one.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    num_links = int(request.form['num_links'])

    # Connect to the SQLite database
    conn = sqlite3.connect('links.db')
    cursor = conn.cursor()

    # Fetch the desired number of links from the database
    cursor.execute('SELECT link FROM links LIMIT ?', (num_links,))
    link_rows = cursor.fetchall()
    links = [row[0] for row in link_rows]

    # Close the database connection
    cursor.close()
    conn.close()

    scraped_paragraphs = []

    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            scraped_paragraphs.append(paragraph.text)

    # Store the scraped paragraphs in the database
    store_paragraphs_in_database(scraped_paragraphs)

    # Render the result page with the scraped paragraphs
    return render_template('result_one.html', paragraphs=scraped_paragraphs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
