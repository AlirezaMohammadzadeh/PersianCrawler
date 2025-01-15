import requests
from bs4 import BeautifulSoup
import json
import psycopg2
from psycopg2 import sql

def insert_data_to_db(data):
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname='news',
        user='admin',
        password='admin',
        host='localhost',  # or your host
        port='5432'  # default port for PostgreSQL
    )
    cursor = conn.cursor()
    
    # Insert data into the isna_news table
    insert_query = sql.SQL("""
        INSERT INTO isna_news (title, short_link, time, tags, kicker, summary, news_code, category, body, image_link, date_modified, author_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """)
    
    cursor.execute(insert_query, data)
    conn.commit()
    cursor.close()
    conn.close()

def scrape_isna_article(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the desired information
        title = soup.select_one('article#item h1').get_text(strip=True)
        shortlink = soup.select_one('input#short-url')['value']
        time = soup.select_one('article#item li:nth-child(1) > span.text-meta').get_text(strip=True)
        
        # Extract the body of the news article
        body = ' '.join([p.get_text(strip=True) for p in soup.select('article#item div.item-body p')])
        
        # Extract tags
        tags = [tag.get_text(strip=True) for tag in soup.select('footer.tags ul li a')]
        
        # Extract the kicker
        kicker = soup.select_one('div.full-news-text h2.kicker').get_text(strip=True) if soup.select_one('div.full-news-text h2.kicker') else 'No kicker found'
        
        # Extract the summary
        summary = soup.select_one('p.summary[itemprop="description"]').get_text(strip=True) if soup.select_one('p.summary[itemprop="description"]') else 'No summary found'
        
        # Extract the category
        category = soup.select_one('span.text-meta[itemprop="articleSection"]').get_text(strip=True) if soup.select_one('span.text-meta[itemprop="articleSection"]') else 'No category found'
        
        # Extract the JSON-LD data
        json_ld_script = soup.select_one('script[type="application/ld+json"]')
        if json_ld_script:
            json_data = json.loads(json_ld_script.string)
            json_news_code = json_data.get('mainEntityOfPage', {}).get('@id', '').split('/')[-2]  # Extract the news code from the URL
            
            # Extract dateModified and author name
            date_modified = json_data.get('dateModified', 'No date modified found')
            author_name = json_data.get('author', {}).get('name', 'No author found')
        else:
            json_news_code = 'No JSON-LD data found'
            date_modified = 'No date modified found'
            author_name = 'No author found'
        
        # Extract the image link
        image_link = soup.select_one('figure.item-img img')['src'] if soup.select_one('figure.item-img img') else 'No image found'
        
        # Prepare data for insertion
        data = (
            title,
            shortlink,
            time,
            tags,
            kicker,
            summary,
            json_news_code,
            category,
            body,
            image_link,
            date_modified,
            author_name
        )
        
        # Insert data into the database
        insert_data_to_db(data)
        
        # Print the extracted information
        print(f"Title: {title}")
        print(f"Short Link: {shortlink}")
        print(f"Time: {time}")
        print(f"Tags: {', '.join(tags)}") 
        print(f"Kicker: {kicker}")  
        print(f"Summary: {summary}")  
        print(f"News Code (from JSON-LD): {json_news_code}")  
        print(f"Category: {category}")
        print(f"Body: {body}")  
        print(f"Image Link: {image_link}")  # Print the image link
        
        # Print date modified and author name
        print(f"Date Modified: {date_modified}")  # Print the date modified
        print(f"Author Name: {author_name}")  # Print the author's name
        
    else:
        print(f"Failed to retrieve the article. Status code: {response.status_code}")

if __name__ == "__main__":
    url = 'https://www.isna.ir/news/99020201601/%D8%AC%D8%A7%D9%8A%DB%8C-%D9%82%D8%A7%D9%84%D8%A7%DB%8C-%D8%A7%D8%B3%D8%A7%D8%B3%DB%8C-%D8%A8%D8%A7-%DB%B8%DB%B1-%D9%87%D8%B2%D8%A7%D8%B1-%DA%A9%D8%A7%D9%85%DB%8C%D9%88%D9%86'
    scrape_isna_article(url) 