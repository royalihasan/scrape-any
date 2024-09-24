from typing import Iterable
import scrapy


class SafewaySpider(scrapy.Spider):
    name = 'safeway'
    allowed_domains = ['safeway.com']
    start_urls = ['https://www.safeway.com/shop.html']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):

        pass
