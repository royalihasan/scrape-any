import scrapy

import json
from scrape_any_crawler.items.e_comm_items import EcommerceItem
import re
from scrape_any_crawler.spider_utils.convertors import price_cleaner
from scrape_any_crawler.spider_utils.generate_logs import set_unique_log_file


def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove special characters, keeping only alphanumeric characters and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.strip()

@set_unique_log_file
class WalmartSpider(scrapy.Spider):
    name = "walmart_spider"
    BASE_URL = 'https://www.walmart.com'
    start_urls = [
        "https://www.walmart.com/browse/electronics/3944?page=1&affinityOverride=default"]

    DEFAULT_URL = "https://www.walmart.com/browse/electronics/3944?page=1&affinityOverride=default"
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrape_any_crawler.pipe.e_comm_psql_pipe.PostgresPipeline': 300,
        },
        # 'SCRAPEOPS_API_KEY': '7e0c88d8-0221-4b51-a67f-faec12d61a19',
        # 'SCRAPEOPS_PROXY_ENABLED': True,
        # 'CONCURRENT_REQUESTS': 1,

        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
        # }
    }

    def __init__(self, url=None, *args, **kwargs):
        super(WalmartSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = [self.DEFAULT_URL]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        script_tag = response.xpath(
            '//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag:
            json_blob = json.loads(script_tag)
            count = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["count"]
            for item in range(count):
                item_data = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"][item]
                if "canonicalUrl" in item_data:
                    sub_links = item_data["canonicalUrl"]
                    print("sub_links", sub_links)
                    full_url = response.urljoin(sub_links)
                    yield scrapy.Request(full_url, callback=self.parse_product)
                else:
                    print(f"Item {item} does not have a canonicalUrl")

        current_page = int(response.url.split('page=')[1].split('&')[0])
        next_page_url = response.url.replace(
            f'page={current_page}', f'page={current_page + 1}')

        if current_page < 0:
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_product(self, response):
        self.logger.info(f"Processing product page: {response.url}")

        # Initialize json_blob to avoid reference errors
        json_blob = None

        # Parse json blob
        script_tag = response.xpath(
            '//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag:
            try:
                json_blob = json.loads(script_tag)
                print("Json blob", json_blob)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON: {e}")
                return  # Exit if JSON cannot be parsed

        # Proceed only if json_blob is successfully loaded
        if json_blob:
            try:
                # Extract product details props.pageProps.initialData.data.product
                product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
                product_idml = json_blob["props"]["pageProps"]["initialData"]["data"]["idml"]
                # extract from css
                price = response.css('span[itemprop="price"]::text').get()
                price = price.replace('Now ', '') if price else 'N/A'
                rating_raw = response.css('span.rating-number::text').get()
                rating = rating_raw.strip('()') if rating_raw else None
                reviews = response.css(
                    'a[data-testid="item-review-section-link"]::text').get()
                reviews = reviews.replace(
                    'reviews', '').strip() if reviews else None

                # reconstruct

                images = []
                for img in product_data.get('imageInfo').get('allImages'):
                    images.append({
                        "store": "Walmart",
                        "type": "thumbnail",
                        "url": img.get('url')
                    })

                categories = []
                for path in product_data['category']['path']:
                    section = path['url'].split('/')[1]
                    categories.append(
                        {'name': path['name'],
                         'section': section,
                         'path': path['url']}
                    )

                # clean price
                clean_price = price_cleaner(price)

                item = EcommerceItem()
                item['product_id'] = product_data.get('id')
                item['name'] = clean_text(product_data.get('name'))
                item['brand'] = product_data.get('brand')
                item['store'] = 'Walmart'
                item['category'] = categories
                item['product_url'] = response.url
                item['price'] = clean_price.get('amount')
                item['currency'] = clean_price.get('currency')
                item['sku'] = product_data.get('upc')
                item['availability'] = product_data.get('availabilityStatus')
                item['rating'] = rating
                item['reviews'] = reviews
                item['description'] = clean_text(
                    product_idml.get('longDescription'))
                item['specifications'] = product_idml.get('specifications')
                item['images'] = images
                item['shipping_info'] = product_data.get('location')
                item['seller_info'] = {"seller_id": product_data.get('sellerId'), "seller_name": product_data.get(
                    'sellerName'), 'seller_display_name': product_data.get('sellerDisplayName'), 'seller_type': product_data.get('sellerType')}
                item['model'] = product_data.get('model')
                item['date_scraped'] = response.headers.get(
                    'Date', None).decode()
                yield item
            except KeyError as e:
                self.logger.error(f"Key error accessing product data: {e}")
            except Exception as e:
                self.logger.error(f"Error parsing product page: {e}")
