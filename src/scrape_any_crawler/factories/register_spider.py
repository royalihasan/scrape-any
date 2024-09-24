import sys
import os
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if base_dir not in sys.path:
    sys.path.append(base_dir)
from spider_registry import SpiderRegistryDynamic


def register_spider(domain):
    def decorator(spider_cls):
        SpiderRegistryDynamic.register(domain, spider_cls)
        return spider_cls
    return decorator
