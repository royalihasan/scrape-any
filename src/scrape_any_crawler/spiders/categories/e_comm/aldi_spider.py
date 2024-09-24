from typing import Any
import scrapy
from scrapy.spiders import  Spider
from scrape_any_crawler.items.e_comm_items import EcommerceItem
from scrape_any_crawler.spider_utils.extracts import extract_product_codes_from_list, find_first_id, extract_id_from_url
import re


def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove special characters, keeping only alphanumeric characters and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.strip()


class AlDiSpider(Spider):
    name = 'aldi_spider'
    start_urls = [
        'https://www.aldi.us/products/snacks']
    DEFAULT_URL = "https://www.aldi.us/products/snacks"

    def __init__(self, url=None, *args, **kwargs):
        super(AlDiSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = [self.DEFAULT_URL]

    # selectors object
    selectors = {
        "product": {
            "name": '//h1[contains(@class, "detail-box--price-box--title")]/text() | //h1[contains(@class, "detail-box--price-box--title")]/br/following-sibling::text()',
            'category': '//ul[contains(@class, "breadcrumb-nav")]//li[last()-1]/a/span[@itemprop="name"]/text()',
            "price": ".product-price::text",
            "image": '//div[contains(@class, "media-gallery")]//img/@src',
            "sku": '//ul/li[contains(text(), "Product Code")]/text()',
            "description_list": '#detail-tabcontent-1 ul li::text',
            "specifications": '//*[@id="c579739"]/div/div[2]/div[2]/div/span[5]/text()',
            'category_list': 'ul.breadcrumb-nav li.breadcrumb-nav--element *::text',
            'single_image': '//div[contains(@class, "ratio-container")]//img/@src'

        }
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrape_any_crawler.pipe.e_comm_psql_pipe.PostgresPipeline': 300,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.extract_sub_category_links)
            yield scrapy.Request(url, callback=self.extract_main_category)

    def extract_main_category(self, response: Any):
        links = response.xpath(
            '//div[@class="linked-teaser"]/a/@href').getall()
        filtered_links = [
            link for link in links if "recipe" not in link and "fileadmin" not in link]
        for link in filtered_links:
            yield response.follow(link, callback=self.parse)

    def extract_sub_category_links(self, response: Any):
        links = response.xpath(
            '//div[@class="csc-default "]//p//a/@href').getall()
        print("sub category links", links)
        for link in links:
            yield scrapy.Request(link, callback=self.extract_sub_category_product_links)

    def extract_sub_category_product_links(self, response: Any):
        links = response.xpath(
            '//a[@class="box--wrapper ym-gl ym-g25 "]/@href').getall()
        filtered_links = [
            link for link in links if "recipe" not in link and "fileadmin" not in link]
        for link in filtered_links:
            yield response.follow(link, callback=self.parse)
        print("product links", filtered_links)

    def parse(self, response):
        item = EcommerceItem()

        # category object reconstruction
        category_list = response.css(
            self.selectors["product"]["category_list"]).getall()
        print("category list", category_list)
        category_list_item = []
        images_obj_list = []

        category = {
            'name': category_list[3],
            'section': category_list[2],
            'path': response.url
        }
        category_list_item.append(category)

        for img in response.xpath(self.selectors["product"]["image"]).getall():
            images_obj_list.append({
                "store": "Aldi",
                "type": "carousel",
                "url": img
            })
            # also add single image
        images_obj_list.append({
            "store": "Aldi",
            "type": "main_thumbnail",
            "url": response.xpath(self.selectors["product"]["single_image"]).get()
        })
        description_list = response.css(
            self.selectors["product"]["description_list"]).getall()
        print("description list", description_list)

        images_list = response.xpath(
            self.selectors["product"]["image"]).getall()
        print("Test Single Image", response.xpath(
            self.selectors["product"]["single_image"]).get())
        # puts the data into the item object
        item["product_id"] = find_first_id(images_list) if find_first_id(
            images_list) else extract_id_from_url(response.xpath(self.selectors["product"]["single_image"]).get())
        combined_name = " ".join(response.xpath(
            self.selectors["product"]["name"]).getall())
        item["name"] = clean_text(combined_name)
        item["brand"] = "Aldi"
        item["product_url"] = response.url
        item["category"] = category_list_item
        item["images"] = images_obj_list
        item["sku"] = extract_product_codes_from_list(description_list)
        combined_description = " ".join(description_list)
        item["description"] = clean_text(combined_description)
        item["specifications"] = [{'weight': response.xpath(
            self.selectors["product"]["specifications"]).get()}]
        item['date_scraped'] = response.headers.get('Date', None).decode()
        yield item
