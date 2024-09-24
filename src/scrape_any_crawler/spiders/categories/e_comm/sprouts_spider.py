import scrapy
from scrapy_playwright.page import PageMethod
from scrapy import Selector
from scrape_any_crawler.items.e_comm_items import EcommerceItem
from scrape_any_crawler.spider_utils.extracts import extract_uuid
from scrape_any_crawler.spider_utils.convertors import price_cleaner
from scrape_any_crawler.spider_utils.generate_logs import set_unique_log_file

@set_unique_log_file
class SproutsSpider(scrapy.Spider):
    name = 'sprouts_spider'
    start_urls = [
        'https://shop.sprouts.com/shop/categories/124'
    ]
    allowed_domains = ['sprouts.com']
    DEFAULT_URL = "https://shop.sprouts.com/shop/categories/124"

    def __init__(self, url=None, *args, **kwargs):
        super(SproutsSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = [self.DEFAULT_URL]
    selectors = {
        "button": 'button[data-test="item-tile-name-button"]',
        "product_name": '//h2[@class="css-112fi4v"]/button/div[@class="css-15uwigl"]/text()',
        'images': '//div[@class="css-1l4w6pd"]/img/@src',
        'weight': '//button[@data-test="item-tile-weight-button"]/div[@class="css-1kh7mkb"]/text()',
        'price': '//div[@class="css-0"]/span[@class="css-coqxwd"]/text()',
        'reviews': '//div[@class="css-1sx5g0s"]/span[@data-test="reviewCountLabel"]/text()',
        'category': '//span[@class="tag-crumb"]/text()',
        'close_modal': 'button#shopping-selector-parent-process-modal-close-click',
        'list_container': 'ol.cell-container.cell-container--css-grid',
        'section': '//span[@data-test="breadcrumb-label" and @class="active"]/text()'
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
        product_js_code = """
       (async function () {
    // Function to close the modal if it exists
    async function closeModal() {
        const closeButton = document.querySelector('button[aria-label="Modal close"][data-test="modal-close-button"].css-l0nvc1');
        if (closeButton) {
            closeButton.click();
            console.log("Modal closed successfully");
        } else {
            console.log("No modal to close");
        }
    }

    // Function to scroll through items
    async function scrollThroughItems() {
        const listContainerSelector = 'ol.cell-container';
        const container = document.querySelector(listContainerSelector);

        // Get the number of items
        const childCount = container.children.length;
        console.log(`Child count: ${childCount}`);

        let currentScrollIndex = 0;
        const segmentSize = 4; // Number of children to scroll through at a time
        const scrollInterval = 4000; // 4s Time to wait between scrolls in milliseconds

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

    function getProductRating() {
        // Select the span element with the rating information
        const ratingElement = document.querySelector('span[data-test="product-rating-label"]');

        // Check if the element exists
        if (!ratingElement) {
            return null; // Return null if the rating element is not found
        }

        // Extract the text content, for example: "4.75 (231)"
        const ratingText = ratingElement.textContent.trim();

        // Extract the numeric rating from the text (before the space)
        const rating = ratingText.split(' ')[0];

        // Return the rating as a float
        return parseFloat(rating);
    }

    function getProductTags() {
        // Get all the list items from the tags container
        const tagElements = document.querySelectorAll('ul[data-test="pdp-product-tags"] li');

        // Create an array to hold the tags
        const tags = [];

        // Loop through the tags and extract the inner text
        tagElements.forEach(tagElement => {
            const tagText = tagElement.querySelector('div.css-85m0bu') ? tagElement.querySelector('div.css-85m0bu').textContent.trim() : null;

            // If the tagText is valid, add it to the array
            if (tagText) {
                tags.push(tagText);
            }
        });

        // Return the array of tags or null if none are found
        return tags.length > 0 ? tags : null;
    }

    function extractBreadcrumbLinks() {
        // Select the breadcrumbs list using the data-test attribute
        const breadcrumbList = document.querySelector('ul[role="region"][aria-label="breadcrumbs"][data-test="breadcrumbs"]');

        // Check if the breadcrumb list exists
        if (!breadcrumbList) {
            console.log("Breadcrumb list not found");
            return [];
        }

        // Select all <a> elements inside the breadcrumb list
        const anchorElements = breadcrumbList.querySelectorAll('li a.css-qx8mhw');

        // Extract the URL and text from each <a> element
        const links = [];
        anchorElements.forEach(anchor => {
            const url = anchor.href;
            const text = anchor.textContent.trim();
            links.push({ url, text });
        });

        return links;
    }

    // Function to scrape data
    async function scrapeData() {
        const items = document.querySelectorAll('li.product-wrapper.cell-wrapper.mobile-span-1');
        const result = [];
        for (let item of items) {
            try {
                // Click on the item to open the modal
                const button = item.querySelector('button.css-1gczm2n');
                if (button) {
                    button.click();

                    // Wait for the modal to appear
                    await new Promise(resolve => setTimeout(resolve, 2000)); // Adjust time as needed

                    // Scrape data from the modal
                    const modalContent = document.querySelector('.modal-content');
                    const descriptionElement = document.querySelector('div[data-test="line-clamp-content"]');
                    const description = descriptionElement ? descriptionElement.innerText : 'No description';

                    const breadcrumbs = extractBreadcrumbLinks();
                    const rating = getProductRating();
                    const brands = getProductTags();  // Fetch brands/tags here

                    console.log("Description", description);
                    console.log("Rating", rating);
                    console.log("Breadcrumbs", breadcrumbs);
                    console.log("Brands", brands);

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
                        description: description,
                        rating: rating,
                        product_info: breadcrumbs,
                        brands: brands // Include brands in the result
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

        """
        product_data = await page.evaluate(product_js_code)
        print("Product data", product_data)
        # Retrieve and parse the HTML content
        html = await page.content()
        s = Selector(text=html)

        # Extract product details
        product_names = s.xpath(self.selectors["product_name"]).getall()
        images = s.xpath(self.selectors['images']).getall()
        prices = s.xpath(self.selectors['price']).getall()
        weights = s.xpath(self.selectors['weight']).getall()
        reviews = s.xpath(self.selectors['reviews']).getall()

        item = EcommerceItem()
        # Yield each product's details
        for name, image, price, weight, review, product in zip(product_names, images, prices, weights, reviews, product_data):
            category_info = product.get('product_info', None)
            text_url = category_info[4] if category_info else None
            product_url = text_url.get('url', None) if text_url else None
            product_category = text_url.get('text', None) if text_url else None
            category = []
            category.append({
                'name': product_category if product_category else None,
                'section': s.xpath(self.selectors['section']).get(),
                'path': product_url if product_url else None
            })
        # item
            images_obj = []
            cleaned_price = price_cleaner(price)
            images_obj.append({
                "store": "sprouts",
                "type": "fit-in/200x200/filters:quality(80)",
                "url": image
            })
            clean_price = price_cleaner(price)
            item['product_id'] = extract_uuid(image)
            item['name'] = name if name else None
            item['images'] = images_obj if images_obj else None
            item['price'] = clean_price.get('amount') if clean_price else None
            item['specifications'] = {
                'weight': weight
            }
            item['store'] = "sprouts"
            item['currency'] = clean_price.get(
                'currency') if clean_price else None
            # brands convert brand list to string
            item['brand'] = " ".join(product.get(
                'brands', [])) if product.get('brands', []) else None

            item['rating'] = product.get('rating', None)
            item['description'] = product.get('description', None)
            item['product_url'] = product_url if product_url else None
            item['category'] = category
            item['date_scraped'] = response.headers.get('Date', None).decode()
            yield item
            await page.close()
