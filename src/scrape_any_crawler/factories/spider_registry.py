import sys
import os
import importlib

# Ensure the base directory (where 'scrape_any_crawler' and 'utils' are located) is in the Python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if base_dir not in sys.path:
    sys.path.append(base_dir)
from utils.config_loader import ConfigLoader

# Add 'scrape_any_crawler' to the Python path
scrape_any_crawler_path = os.path.join(base_dir, 'scrape_any_crawler')
if scrape_any_crawler_path not in sys.path:
    sys.path.append(scrape_any_crawler_path)


class SpiderRegistry:
    _registry = {}

    @classmethod
    def register(cls, domain, spider_cls):
        cls._registry[domain] = spider_cls

    @classmethod
    def get_spider(cls, domain):
        spider_cls = cls._registry.get(domain)
        if spider_cls is None:
            raise ValueError(f"Spider for domain '{domain}' not found")
        return spider_cls

    @classmethod
    def load_and_register_spider(cls, domain):
        config_loader = ConfigLoader()
        config = config_loader.load()
        print(config)

        for category, spiders in config['spiders'].items():
            for spider in spiders:
                if domain == spider.get('domain'):
                    module_path = spider['module']
                    class_name = spider['class']
                    print(f"Loading spider class: {module_path}.{class_name}")

                    # Import the spider class directly using its full path
                    try:
                        # Ensure that the module path is correctly formatted
                        if not module_path.startswith('scrape_any_crawler.'):
                            module_path = 'scrape_any_crawler.' + module_path
                        module = importlib.import_module(module_path)
                        spider_cls = getattr(module, class_name)
                        cls.register(domain, spider_cls)
                        return spider_cls
                    except ModuleNotFoundError as e:
                        print(f"ModuleNotFoundError: {e}")
                    except AttributeError as e:
                        print(f"AttributeError: {e}")

        raise ValueError(f"No spider found for domain '{domain}'")


if __name__ == '__main__':
    domain = "walmart.com"
    try:
        spider_cls = SpiderRegistry.get_spider(domain)
    except ValueError:
        spider_cls = SpiderRegistry.load_and_register_spider(domain)

    spider_instance = spider_cls()
    # print(spider_instance.product_data)
