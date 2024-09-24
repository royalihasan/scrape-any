from typing import Any, Iterable
import scrapy
from scrapy.http import Response


class BjsSpider(scrapy.Spider):
    name = "bjs_spider"
    start_urls = [
        "https://www.bjs.com/category/grocery/dairy/wellsley-farms-dairy/3000000000000248005",

    ]
    custom_settings = {
        'SCRAPEOPS_PROXY_SETTINGS': {'country': 'us'},
        'DOWNLOAD_DELAY': 3,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 3,
        'CONCURRENT_REQUESTS': 1,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
    }
    selectors = {
        "product_links": 'div.title-new-plp a.product-link::attr(href)',
        "url": "response.url",
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'playwright': True})

    def parse(self, response):
        # title
        title = response.css("title::text").get()
        product_links = response.css(self.selectors["product_links"]).extract()
        for link in product_links:
            print("Link" + link)
        print("Response_url" + response.url)
        yield {
            "title": title,
            "url": response.url,
        }
