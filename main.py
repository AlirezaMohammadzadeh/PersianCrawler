import scrapy
from scrapy.crawler import CrawlerProcess
from isna import IsnaSpider  # Adjust the import based on your project structure

def run_spider(url):
    process = CrawlerProcess({
        'LOG_LEVEL': 'ERROR',  # Set log level to avoid clutter
    })

    process.crawl(IsnaSpider, url=url)  # Pass the URL to the spider
    process.start()  # Start the crawling process
    

if __name__ == "__main__":
    url = 'isna.ir/xdFJsQ'
    run_spider(url)

