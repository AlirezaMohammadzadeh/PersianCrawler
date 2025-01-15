import scrapy
import re
from logger import logger
from datetime import datetime


class IsnaSpider(scrapy.Spider):
    
    name = "Isna"
    start_urls = []
    custom_settings = {'AUTOTHROTTLE_ENABLED':True}

    main_url = "https://www.isna.ir"
    
    def __init__(self, url=None, *args, **kwargs):
        super(IsnaSpider, self).__init__(*args, **kwargs)
        self.items = []  # Initialize an empty list to store items
        if url:
            self.start_urls.append(url)

    def parse(self, response ):
        try:
            # we have a problem in isna which is unsolved. If you go to page 50, for example, it might show you some news from previous days! 
            # so acutally you should filter that out. 
            for news in response.css("div.items a::attr(href)").getall():
                if len(news.strip()) > 0:
                    yield scrapy.Request(
                        self.main_url+news,
                        callback=self.parse_news,
                    )
        except Exception:
            logger.error("Parsing Error: ", exc_info=True)

    def parse_news(self, response):
        try: 
            # Extract the date from the response (assuming it's available in the response)
            date = response.css('article#item li.date::text').get()  # Adjust the selector as needed

            item = {
                'date': date,
                'title': response.css('article#item h1::text').get(),
                'shortlink': response.css('input#short-url::attr(value)').get(),
                'time':  response.css('article#item li:nth-child(1) > span.text-meta::text').get(),
                'service': response.css('article#item li:nth-child(2) > span.text-meta::text').get(),
                'news_id': response.css('article#item li:nth-child(3) > span.text-meta::text').get(),
                'reporter': response.css('article#item li:nth-child(1) > strong::text').get(), 
                'managers': response.css('article#item li:nth-child(2) > strong::text').get(),
                'body': ' '.join(response.css('article#item div.item-body *::text').getall()),
            }
            
            # Clean up the item fields
            for key in item:
                if item[key]:
                    item[key] = re.sub(' +', ' ', item[key]).strip()
            
            self.items.append(item)
            # Log the item to confirm it's being created
            logger.info(f"Collected item: {item}")
            yield item  # Yield the item for Scrapy to process

        except Exception:
            logger.error("Error", exc_info=True)

    def close(self, reason):
        logger.info("Spider closed. Printing collected items:")
        logger.info(f"Total items collected: {len(self.items)}")
        logger.info(self.items)
        # Print the collected items directly
        for item in self.items:
            print(f"Date: {item['date']}, Title: {item['title']}, Short Link: {item['shortlink']}, Time: {item['time']}")
