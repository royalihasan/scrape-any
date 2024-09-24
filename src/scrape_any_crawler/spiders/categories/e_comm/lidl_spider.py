import scrapy
from scrapy.spiders import Spider
from scrapy_playwright.page import PageMethod
from scrape_any_crawler.items.e_comm_items import EcommerceItem
from scrapy import Selector
from scrape_any_crawler.spider_utils.convertors import price_cleaner


class AlDiSpiderSinglePage(Spider):
    name = 'lidl_spider'
    start_urls = [
        'https://www.lidl.com/products?category=OCI2000081&sort=productAtoZ'
    ]
    BASE_URL = 'https://www.lidl.com'
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 8,
        # 'CONCURRENT_REQUESTS': 10,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'COOKIES_DEBUG': True,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": False
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 10000000,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 2  # Number of tabs per domain
        'ITEM_PIPELINES': {
            'scrape_any_crawler.pipe.e_comm_psql_pipe.PostgresPipeline': 300,
        }
    }

    selectors = {
        "name": '//h3[@itemprop="name"]/text()',
        'category': '//div[@class="aisle-module-container"]//span[@data-testid="description-text"]/text()',
        "price": '//span[@class="product-price-new__price"]/text()',
        "image": '//ul[@class="product-preview-list"]//img/@src',
        "sku": '//div[@class="aisle-info-container"]//h4[@data-testid="aisle-number"]/text()',
        "description": '//div[@class="description"]//text()',
        "weight": '//div[@class="base-price-container"]//h5[@itemprop="price"]/text()',
        'availability': '//div[@class="stock-status-container__stock-status instock"]/text()',
        'brand': '//div[@class="aisle-module-container"]//p[@class="regular-type stock-status-store"]/text()',
        'discount_price': "//span[contains(@class, 'product-price-new__price') and contains(@class, 'product-price-new__price--discount')]/text()",
        'single_image': "//img[@itemprop='image' and @data-testid='carouselImageLarge0']/@src",
        'product_url': '//a[@class="clickable link product-card__detail clickable--size-inline"]/@href',
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.extract_product_links, meta={'playwright': True, 'playwright_include_page': True})

    async def extract_product_links(self, response):
        page = response.meta['playwright_page']
        # Handle cookie acceptance
        await page.click('#onetrust-accept-btn-handler')
        await page.wait_for_timeout(2000)  # Wait for 2 seconds

        # JavaScript code to extract links
        js_code = '''
        const waitForContent = () => new Promise(resolve => {
            const interval = setInterval(() => {
                if (document.querySelectorAll('a.clickable.link.product-card__detail.clickable--size-inline').length) {
                    clearInterval(interval);
                    resolve();
                }
            }, 100);
        });

        const extractLinks = async () => {
            await waitForContent();
            const elements = document.querySelectorAll('a.clickable.link.product-card__detail.clickable--size-inline');
            return Array.from(elements).map(el => el.getAttribute('href'));
        };

        extractLinks();
        '''

        product_links = await page.evaluate(js_code)

        print("Extracted product_links:", product_links)
        await page.close()
        for url in product_links:
            yield scrapy.Request(url=self.BASE_URL + url, callback=self.parse, meta={'playwright': True, 'playwright_include_page': True})

    async def parse(self, response):
        page = response.meta['playwright_page']

        # JavaScript extraction code
        js_code = '''
        const selectors = {
            "name": '//h3[@itemprop="name"]/text()',
            'category': '//div[@class="aisle-module-container"]//span[@data-testid="description-text"]/text()',
            "price": '//span[@class="product-price-new__price"]/text()',
            "image": '//ul[@class="product-preview-list"]//img/@src',
            "sku": '//div[@class="aisle-info-container"]//h4[@data-testid="aisle-number"]/text()',
            "description": '//div[@class="description"]//text()',
            "weight": '//div[@class="base-price-container"]//h5[@itemprop="price"]/text()',
            'availability': '//div[@class="stock-status-container__stock-status instock"]/text()',
            'brand': '//div[@class="aisle-module-container"]//p[@class="regular-type stock-status-store"]/text()',
            'discount_price': "//span[contains(@class, 'product-price-new__price') and contains(@class, 'product-price-new__price--discount')]/text()",
            'single_image': "//img[@itemprop='image' and @data-testid='carouselImageLarge0']/@src"
        };

        function extractTextContent(xpath) {
            const evaluator = new XPathEvaluator();
            const result = evaluator.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            let texts = [];
            for (let i = 0; i < result.snapshotLength; i++) {
                texts.push(result.snapshotItem(i).textContent.trim());
            }
            return texts;
        }

        function extractData() {
            const data = {};
            for (let key in selectors) {
                data[key] = extractTextContent(selectors[key]);
            }
            return data;
        }

        extractData();
        '''
        # Retrieve and parse the HTML content
        html = await page.content()
        s = Selector(text=html)
        data = await page.evaluate(js_code)

        name = data["name"][0] if data["name"] else None
        brand = data["brand"][0] if data["brand"] else None
        category = data["category"][1] if data["category"] else None
        # construct category
        categories = []
        images = []
        categories.append({
            'name': brand,
            'section': category,
            'path': response.url
        })
        images.append({
            "store": "Lidl",
            "type": "thumbnail",
            "url": data["single_image"][0] if data["single_image"] else None
        })
        for img in data["image"] or []:
            images.append({
                "store": "Lidl",
                "type": "sub-image",
                "url": img
            })
        # Extract product ID from URL
        product_id = response.url.split(
            '/')[-1].split('?')[0]  # Extract ID from URL
        item = EcommerceItem()
        item["product_id"] = product_id
        # name into string

        item["name"] = name if name else None

        item["brand"] = brand if brand else None
        item["product_url"] = response.url
        item["category"] = categories if categories else None
        item["images"] = images if images else None
        item['store'] = 'Lidl'
        price = data["price"][0] if data["price"] else None
        price_ = price_cleaner(price)
        item["price"] = price_.get('amount') if price_ else None
        item['currency'] = price_.get('currency') if price_ else None
        item["description"] = " ".join(
            data["description"]) if data["description"] else None
        item["specifications"] = [{'weight': data["weight"]}]
        availability = data["availability"][0] if data["availability"] else None
        item["availability"] = availability
        item['date_scraped'] = response.headers.get('Date', None).decode()

        yield item
        await page.close()


# {
#         "product_id": "1065748",
#         "name": [
#             "mozzarella string cheese"
#         ],
#         "brand": [
#             "store: Culpeper VA - Brandy Rd"
#         ],
#         "product_url": "https://www.lidl.com/products/1065748",
#         "category": [
#             "section:",
#             "Chiller"
#         ],
#         "images": [
#             {
#                 "single_image": [
#                     "https://production-endpoint.azureedge.net/images/68RJIC9L6PFJAC1GF0QJ0C0/6cc909e0-7a74-4169-b3c7-ed00dad64c97/279156_500x500_500x500.tif.jpg"
#                 ]
#             },
#             {
#                 "all_images": [
#                     "https://production-endpoint.azureedge.net/images/68RJIC9L6PFJAC1GF0QJ0C0/6cc909e0-7a74-4169-b3c7-ed00dad64c97/279156_500x500_500x500.tif.jpg",
#                     "https://production-endpoint.azureedge.net/images/6GR36CPG75FJAC1GF0QJ0C0/d89caaa3-1d34-4d3c-b846-3745542d42a0/463309_500x500_500x500.tif.jpg"
#                 ]
#             }
#         ],
#         "sku": [
#             "aisle:",
#             "1"
#         ],
#         "price": [
#             "$2.79",
#             "*"
#         ],
#         "description": [
#             "Creamy and stringy, this mozzarella cheese makes a great snack options for the busy work week. Take pasta night to the next level by cubing and stuffing this cheese into homemade meatballs.",
#             "from cows not treated with rBST*",
#             "refrigerated",
#             "12 oz.",
#             "*no significant difference has been shown between milk derived from rBST-treated and non-rBST-treated cows"
#         ],
#         "specifications": [
#             {
#                 "weight": [
#                     "23.3 ¢ per oz."
#                 ]
#             }
#         ],
#         "availability": [],
#         "date_scraped": "Thu, 12 Sep 2024 14:07:50 GMT"
#     }
