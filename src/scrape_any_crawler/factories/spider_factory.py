from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from spider_registry import SpiderRegistry
from base_exporter import JSONExporter
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks


class SpiderFactory:
    @staticmethod
    def run_spider(domain, url_list, stop_after_crawl=False):
        try:
            # Try to get the spider from the registry
            spider_cls = SpiderRegistry.get_spider(domain)
        except ValueError:
            # Load and register the spider if it's not already registered
            spider_cls = SpiderRegistry.load_and_register_spider(domain)
            spider_cls(test_url=url_list)

        if spider_cls:
            # Hardcoded settings for the Scrapy process
            settings = {
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'ROBOTSTXT_OBEY': True,
                'LOG_LEVEL': 'INFO',
                'COOKIES_ENABLED': False,
                'SCRAPEOPS_API_KEY': 'd3085d77-e3cb-4c71-ac13-352863d4a84c',
                'SCRAPEOPS_PROXY_ENABLED': True,
                'DOWNLOADER_MIDDLEWARES': {
                    'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
                }
            }

            # Set exporter
            JSONExporter.configure_export(settings=settings)

            # Create a CrawlerRunner instance with the hardcoded settings
            runner = CrawlerRunner(get_project_settings())

            # Schedule the spider class to run
            d = runner.crawl(spider_cls)
            # d.addBoth(lambda _: reactor.stop())
            reactor.run()  # the script will block here until the crawling is finished


if __name__ == "__main__":
    # Example usage
    domain = "walmart.com"  # The domain you want to scrape
    SpiderFactory.run_spider(domain, ['a'])
