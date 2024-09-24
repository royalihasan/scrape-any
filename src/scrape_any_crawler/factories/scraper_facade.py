import os
import sys
import time
from read_logs import read_spider_logs
from extract_config import get_spider_by_domain
from run_scrapper import SpiderRunner


base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if base_dir not in sys.path:
    sys.path.append(base_dir)
from utils.read_dumps import process_dumps
from utils.extract_domain import extract_full_domain
class ScraperFacade:
    def __init__(self):
        # A dictionary to track the last read position for each spider
        self.spider_log_positions = {}

    def url_to_domain(self, url):
        """
        Extracts domain from a given URL.
        """
        return extract_full_domain(url)

    def get_spider_by_domain(self, domain):
        """
        Retrieves the spider name by domain.
        """
        return get_spider_by_domain(domain)

    def start(self, **kwargs):
        """
        Starts a spider for a given URL and processes the dumped data.
        """
        url = kwargs.get('url')
        print(f"Received URL: {url}")
        domain = self.url_to_domain(url)
        print(f"Extracted domain: {domain}")
        spider = self.get_spider_by_domain(domain)
        print(f"Found spider: {spider}")

        if spider:
            runner = SpiderRunner()
            isSuccess = runner.run_spider(spider_name=spider, url=url)
            if isSuccess:
                dumps_directory = 'src/dumps/data/' + spider
                data = process_dumps(dumps_directory)
                return data
            else:
                print(f"Failed to run spider {spider}.")
                return None
        else:
            print(f"No spider found for domain: {domain}")
        return spider

    def stream_spider_logs(self, spider_name):
        """
        Generator function to stream logs dynamically, reading only new lines.
        Stops if no new logs are found for 10 seconds.
        """
        log_generator = read_spider_logs(spider_name)
        if not log_generator:
            yield f"No logs found for {spider_name}\n"
            return

        # Get the last read position or start from the beginning
        position = self.spider_log_positions.get(spider_name, 0)
        log_lines = list(log_generator)
        start_time = time.time()  # Track the start time for timeout

        try:
            while True:
                if position < len(log_lines):
                    for line in log_lines[position:]:
                        yield line + "\n"
                        position += 1  # Update the position after each yield
                    # Reset the start time as new logs were found
                    start_time = time.time()
                else:
                    time.sleep(1)  # Sleep for a short period before checking for new logs

                    # Read the latest logs dynamically by recalling the generator
                    log_generator = read_spider_logs(spider_name)
                    if log_generator:
                        log_lines = list(log_generator)
                    else:
                        yield f"No new logs found for {spider_name}\n"

                    # Check if 10 seconds have passed without new logs
                    if time.time() - start_time > 10:
                        yield "Stopped due to inactivity. No new logs found for 10 seconds.\n"
                        return
        except Exception as e:
            yield f"Error streaming logs: {e}\n"

    def get_logs(self, spider_url):
        """
        Retrieves the logs for a given spider by its URL.
        """
        domain = self.url_to_domain(spider_url)
        spider = self.get_spider_by_domain(domain)
        if spider:
            return self.stream_spider_logs(spider)
        else:
            return iter([f"No spider found for domain: {domain}\n"])

if __name__ == "__main__":
    facade = ScraperFacade()

    # Test the `start` method
    print("=== Testing `start` method ===")
    url = 'https://www.walmart.com'
    result = facade.start(url=url)
    if result:
        print("Data processed successfully:", result)
    else:
        print("Failed to process data or no data.")

    # Test the `get_logs` method and log streaming with a 10-second timeout
    print("\n=== Testing `get_logs` method ===")
    logs_generator = facade.get_logs('https://www.walmart.com/browse/electronics/3944?page=1')

    start_time = time.time()
    for log_line in logs_generator:
        print(log_line)
        if time.time() - start_time > 15:  # Ensure it runs for a little longer than the timeout
            break
