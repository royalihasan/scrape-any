import os
from datetime import datetime
from logging.config import dictConfig

def set_unique_log_file(spider_cls):
    """
    Decorator that sets up a unique log file for each spider instance.
    """
    original_init = spider_cls.__init__

    def new_init(self, *args, **kwargs):
        # Get the spider name from the instance
        spider_name = self.name

        # Create a directory for logs if it doesn't exist
        log_dir = f"log_dumps/{spider_name}"
        os.makedirs(log_dir, exist_ok=True)

        # Create a unique log file name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'{log_dir}/{spider_name}_log_{timestamp}.log'

        # Update the spider's custom_settings dynamically
        self.custom_settings = {
            **getattr(self, 'custom_settings', {}),
            'LOG_FILE': None,  # Disable default Scrapy file logging so we can use our own handler
            'LOG_LEVEL': 'INFO',  # Adjust the log level if necessary
        }

        # Configure logging to both file and console
        dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                },
            },
            'handlers': {
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': log_file,
                    'formatter': 'default',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                },
            },
            'root': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
            },
        })

        # Call the original __init__ method
        original_init(self, *args, **kwargs)

    # Override the spider's __init__ method with the new one
    spider_cls.__init__ = new_init

    return spider_cls
