from scrapy import Spider, Selector
import scrapy
from scrape_any_crawler.items.e_comm_items import EcommerceItem
import uuid
from scrape_any_crawler.spider_utils.extracts import extract_uuid
from scrape_any_crawler.spider_utils.convertors import price_cleaner
from scrape_any_crawler.spider_utils.generate_logs import set_unique_log_file


@set_unique_log_file
class WegmansSpider(scrapy.Spider):
    name = 'wegmans_spider'
    allowed_domains = ['wegmans.com']
    start_urls = ['https://shop.wegmans.com/shop/categories/216']
    DEFAULT_URL = "https://shop.wegmans.com/shop/categories/216"

    def __init__(self, url=None, *args, **kwargs):
        super(WegmansSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = [self.DEFAULT_URL]
    # selectors
    selectors = {
        'product_name': '//button[@data-test="item-tile-name-button"]/div[@class="css-131yigi"]/text()',
        'list_container': 'ul[data-test="shop-products-items"]',
        'close_modal': 'button#shopping-selector-parent-process-modal-close-click',
        'images': '//div[@class="css-1l4w6pd"]/img/@src',
        'price': '//div[@class="css-0"]/span[@class="css-zqx11d"]/text()',
        'weight': '//div[@class="css-1kh7mkb"]/text()',
        'rating': '//div[@class="css-1sx5g0s"]/span[@data-test="reviewCountLabel"]/text()',
        'category': '//ul[@data-test="breadcrumbs"]//li[last()]/span[@data-test="breadcrumb-label"]/text()',
        'section': """response.xpath('//ul[@data-test="breadcrumbs"]/li/a[contains(@href, "/shop/categories")]/@href').get()""",
        'description': '//div[@data-test="line-clamp-content"]//text()'


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
            "headless": False
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 10000000,

        'ITEM_PIPELINES': {
            'scrape_any_crawler.pipe.e_comm_psql_pipe.PostgresPipeline': 300,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                }
            )

    async def parse(self, response):
        # Get the Playwright page object from meta
        page = response.meta.get('playwright_page')

        # Try to close the modal by clicking the close button
        try:
            if await page.query_selector(self.selectors['close_modal']):
                await page.click(self.selectors['close_modal'])
                self.logger.info("Modal closed successfully")
            else:
                self.logger.info("No modal to close")
        except Exception as e:
            self.logger.warning(f"Failed to close modal: {e}")

        list_container_selector = self.selectors['list_container']
        container = await page.query_selector(list_container_selector)

        js_code = ''' 
        (async function() {
            // Function to close the modal if it exists
            async function closeModal() {
                const closeButton = document.querySelector('button[data-test="modal-close-button"]');
                if (closeButton) {
                    closeButton.click();
                    console.log("Modal closed successfully");
                } else {
                    console.log("No modal to close");
                }
            }

            // Function to scroll through items
            async function scrollThroughItems() {
                const listContainerSelector = 'ul[data-test="shop-products-items"]';
                const container = document.querySelector(listContainerSelector);

                // Get the number of items
                const childCount = container.children.length;
                console.log(`Child count: ${childCount}`);

                let currentScrollIndex = 0;
                const segmentSize = 4; // Number of children to scroll through at a time
                const scrollInterval = 2000; // Time to wait between scrolls in milliseconds

                while (currentScrollIndex < childCount) {
                    const endIndex = Math.min(currentScrollIndex + segmentSize, childCount) - 1;

                    // Scroll to the end of the current segment
                    const children = container.children;
                    const topOffset = children[endIndex].offsetTop;
                    window.scrollTo(0, topOffset);

                    console.log(`Scrolled to index: ${endIndex}`);
                    await new Promise(resolve => setTimeout(resolve, scrollInterval));

                    currentScrollIndex += segmentSize;
                }
            }

            // Function to scrape data
            async function scrapeData() {
                const items = document.querySelectorAll('li[data-test="product-grid-item"]');
                const result = [];
                for (let item of items) {
                    try {
                        // Click on the item to open the modal
                        const button = item.querySelector('button.css-1gczm2n');
                        if (button) {
                            button.click();
                            
                            // Wait for the modal to appear
                            await new Promise(resolve => setTimeout(resolve, 10000)); // Adjust time as needed

                            // Scrape data from the modal
                            const modalContent = document.querySelector('.modal-content');
                            const descriptionElement = document.querySelector('div[data-test="line-clamp-content"]');
                            const description = descriptionElement ? descriptionElement.innerText : 'No description';

                            if (modalContent) {
                                const modalText = modalContent.innerText;
                                console.log('Modal data:', modalText);
                            } else {
                                console.log('Modal content not found');
                            }

                            console.log('Description:', description);

                            // Close the modal
                            await closeModal();

                            result.push({
                                modalContent: modalContent ? modalContent.innerText : 'No modal content',
                                description: description
                            });
                        } else {
                            console.log('Button not found in item');
                        }
                        
                        // Wait for the next item to be visible
                        await new Promise(resolve => setTimeout(resolve, 500)); // Adjust time as needed
                        
                    } catch (e) {
                        console.error(`Error processing item: ${e}`);
                    }
                }
                return result;
            }

            // Run the functions
            await closeModal();
            await scrollThroughItems();
            return await scrapeData();
        })();
        '''
        scraped_data = await page.evaluate(js_code)
        print("Scraped data", scraped_data)
        html = await page.content()
        s = Selector(text=html)

        # product details
        item = EcommerceItem()
        names = s.xpath(self.selectors['product_name']).getall()
        images = s.xpath(self.selectors['images']).getall()
        prices = s.xpath(self.selectors['price']).getall()
        weights = s.xpath(self.selectors['weight']).getall()
        ratings = s.xpath(self.selectors['rating']).getall()
        # Extract the 3rd item text (CSS is 0-based index)
        category_section = s.css(
            'ul[role="region"] li:nth-of-type(4) a::text').get(default='').strip()
        category_url = s.css(
            'ul[role="region"] li:nth-of-type(4) a::attr(href)').get(default='')
        print("Category text", category_section)
        print("category url", category_url)
        # construct category
        category = []
        category.append({
            'name': s.xpath(self.selectors['category']).get(),
            'section': category_section,
            'path': category_url
        })

        for name, image, price, weight, rating, data in zip(names, images, prices, weights, ratings, scraped_data):
            images_obj = []
            cleaned_price = price_cleaner(price)
            images_obj.append({
                "store": "Wegmans",
                "type": "fit-in/200x200/filters:quality(80)",
                "url": image
            })
            product_id = extract_uuid(image)
            brand = name.split(',')[0].strip()
            item['product_id'] = product_id
            item['name'] = name
            item['images'] = images_obj
            item['price'] = cleaned_price.get('amount')
            item['currency'] = cleaned_price.get('currency')
            item['specifications'] = {
                'weight': weight
            }
            item['rating'] = rating if rating else None
            item['category'] = category
            item['store'] = "wegmans"
            item['product_url'] = response.url
            item['description'] = data.get('description', 'No description')
            item['brand'] = brand
            item['date_scraped'] = response.headers.get('Date', None).decode()

            yield item
            await page.close()
