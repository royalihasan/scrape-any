import scrapy
import json
from typing import List, Dict, Any, Generator, AsyncGenerator
import uuid
import scrapy.http
from scrapy import Selector
from scrape_any_crawler.items.e_comm_items import EcommerceItem


class HarrisTeeterSpider(scrapy.Spider):
    name = 'harris_teeter'
    allowed_domains = ['harristeeter.com']
    urls_list: List[str] = [
        'https://www.harristeeter.com/pl/chicken/05002?pzn=relevance'
    ]
    base_url: str = 'https://www.harristeeter.com'

    custom_settings: Dict[str, Any] = {
        'DOWNLOAD_DELAY': 3,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 8,
        'CONCURRENT_REQUESTS': 1,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
        # 'PROXY_ENABLED': True,
    }
    headers: Dict[str, str] = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
        'cache-control': 'no-cache',
        'device-memory': '8',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    selector = {
        'weight': "span.ProductDetails-sellBy::text",

        'rating': "span.kds-Text--m.mx-4.text-accent-more-prominent::text",

        'total_reviews': "span.kds-Text--m.ml-1.text-accent-more-prominent::attr(aria-label)",

        'stocks': "span.kds-Tag-text::text",

        'sold_and_shipped_by': 'button.kds-Text--m.WebBuyLinkButton.p-0.text-accent-more-prominent.truncate[data-testid="marketplace-sellers-name"]::text',

        'sub_category': "ol.list-none li.inline a::text"

    }

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        for url in self.urls_list:
            yield scrapy.Request(url=url, callback=self.parse_product_urls, meta={'playwright': True, 'playwright_include_page': True})

    async def parse_product_urls(self, response: scrapy.http.Response):
        page = response.meta['playwright_page']

        while True:
            # Click the "Load More" button to load additional products, if present
            load_more_button = await page.query_selector('button.kds-Button.interactive.palette-accent.kind-prominent.variant-border.my-12.px-32.LoadMore__load-more-button')
            if load_more_button:
                await load_more_button.click()
                await page.wait_for_selector('a.kds-Link.kds-Link--inherit.kds-Link--implied.ProductDescription-truncated.overflow-hidden.text-primary')
                await page.wait_for_timeout(2000)  # Adjust timeout as needed
            else:
                break

        html = await page.content()
        s = Selector(text=html)
        await page.close()

        # Extract product URLs from the page
        urls_elements = s.css(
            'a.kds-Link.kds-Link--inherit.kds-Link--implied.ProductDescription-truncated.overflow-hidden.text-primary')
        urls = urls_elements.css('::attr(href)').getall()
        self.logger.info(f'Found URLs: {urls}')
        if not urls:
            self.logger.error('No URLs found on the page.')
            return
        print('Total Links:', len(urls))
        # Send requests for each product URL
        for product_url in urls:
            yield scrapy.Request(url=self.base_url + product_url, headers=self.headers, callback=self.parse_product)

    def parse_product(self, response: scrapy.http.Response):
        self.logger.info(f'Parsing product page: {response.url}')
        script_data = response.css('#content > div > div > script::text').get()
        if script_data:
            try:
                product_data = json.loads(script_data)

                item = EcommerceItem()
                item['product_id'] = str(uuid.uuid4())
                item['name'] = product_data.get('name')
                item['brand'] = product_data.get('brand')
                item['product_url'] = response.url
                item['category'] = self.selector.get('sub_category').get()
                item['images'] = product_data.get('image')
                item['sku'] = product_data.get('sku')
                item['price'] = product_data.get(
                    'price') or 'Not available'
                item['description'] = product_data.get('description')
                item['specifications'] = [
                    {'weight': self.selector.get('weight').get()}]
                item['date_scraped'] = response.headers.get(
                    'Date', None).decode()
                item['shipping_info'] = self.selector.get(
                    'sold_and_shipped_by').get()
                item['rating'] = self.selector.get('rating').get()
                item['reviews'] = self.selector.get('total_reviews').get()
                item['availability'] = self.selector.get('stocks').get()
                yield item

            except json.JSONDecodeError:
                self.logger.error('Failed to decode JSON from script tag.')
