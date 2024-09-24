

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


# SCRAPEOPS_API_KEY = 'd3085d77-e3cb-4c71-ac13-352863d4a84c'
# SCRAPEOPS_PROXY_ENABLED = True

# DOWNLOADER_MIDDLEWARES = {
#     'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
# }


# playwright settings
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False

}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 100000

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

FEEDS = {
    'dumps/data/%(name)s/%(name)s/%(time)s.json': {'format': 'json'}
}

# ITEM_PIPELINES = {
#     'scrape_any_crawler.pipe.e_comm_psql_pipe.PostgresPipeline': 300,
# }
