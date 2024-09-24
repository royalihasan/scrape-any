import sys
import os
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from utils.config_loader import ConfigLoader

def get_spider_by_domain(domain):
    config = ConfigLoader().load()
    """Fetch the spider configuration based on the domain."""
    for category, spiders in config['spiders'].items():
        for spider in spiders:
            if spider['domain'] == domain:
                return spider.get('name')
    return None


if __name__ == '__main__':
    spider = get_spider_by_domain('shop.sprouts.com')
    print(spider)
