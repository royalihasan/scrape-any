import scrapy
from scrapy import Selector


class CostcoSpider(scrapy.Spider):
    name = 'costco_spider'
    allowed_domains = ['costco.com']
    start_urls = [
        'https://www.costco.com/pc-laptops.html']

    # selectors
    selectors = {
        'product_name': '//h1[@itemprop="name"]/text()',
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 8,
        'CONCURRENT_REQUESTS': 1,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": True
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 10000000,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.product_links,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                }
            )

    def product_links(self, response):
        pass
