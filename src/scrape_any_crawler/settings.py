

BOT_NAME = "scrape_any_crawler"

SPIDER_MODULES = ["scrape_any_crawler.spiders"]
NEWSPIDER_MODULE = "scrape_any_crawler.spiders"


# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


# User agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"


# SCRAPEOPS_API_KEY = '2b1b732f-ce34-4a84-87a1-8d3955aaa013'
# SCRAPEOPS_PROXY_ENABLED = True

# DOWNLOADER_MIDDLEWARES = {
#     'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
# }
