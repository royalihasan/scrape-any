
import scrapy


class EcommerceItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    product_url = scrapy.Field()
    price = scrapy.Field()
    sku = scrapy.Field()
    availability = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()
    description = scrapy.Field()
    specifications = scrapy.Field()
    images = scrapy.Field()
    shipping_info = scrapy.Field()
    seller_info = scrapy.Field()
    tags = scrapy.Field()
    model = scrapy.Field()
    date_scraped = scrapy.Field()
    currency = scrapy.Field()
    store= scrapy.Field()
