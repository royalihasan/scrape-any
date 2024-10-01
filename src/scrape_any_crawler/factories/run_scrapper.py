import subprocess
import os


class SpiderRunner:
    def run_spider(self, spider_name, **kwargs):
        url = kwargs.get('url')
        spider_directory = os.path.join(os.getcwd(), 'src/')

        """Runs a Scrapy spider using subprocess without storing logs."""
        try:
            # Start the subprocess to run the spider
            process = subprocess.Popen(
                ['scrapy', 'crawl', spider_name, '-a', f'url={url}'],
                cwd=spider_directory
            )

            # Wait for the process to complete
            process.wait()
            # Check if the process ended successfully
            return process.returncode == 0

        except Exception as e:
            print(f"Failed to run spider {spider_name}: {str(e)}")
            return False


# Test
if __name__ == '__main__':
    spider_runner = SpiderRunner()
    spider_runner.run_spider(
        'walmart_spider', url='https://www.walmart.com/browse/food/bread/976759_976779_8399244?povid=976759_GlobalNav_976779_GroceryBakeryBread_Bread_Rweb_Jul_26')
