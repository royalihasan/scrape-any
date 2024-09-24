import os
from datetime import datetime

def read_spider_logs(spider_name, base_dir='src/log_dumps', log_extension='.log'):
    """
    Stream the latest log file for a given spider from the log directory line by line.
    
    :param spider_name: The name of the spider whose logs you want to read.
    :param base_dir: The base directory where the logs are located.
    :param log_extension: The extension of the log file (default is '.log').
    :return: A generator yielding lines from the latest log file.
    """
    spider_dir = os.path.join(base_dir, spider_name)
    log_files = []

    # Check if the spider's log directory exists
    if not os.path.exists(spider_dir):
        print(f"Spider log directory '{spider_dir}' does not exist.")
        return None

    print(f"Searching for log files in: {spider_dir}")

    # Search for log files in the spider's log directory
    for root, dirs, files in os.walk(spider_dir):
        for file in files:
            # Match the specific format 'spidername_log_YYYYMMDD_HHMMSS.log'
            if file.endswith(log_extension) and file.startswith(f"{spider_name}_log_"):
                log_files.append(os.path.join(root, file))

    # If no log files found, return None
    if not log_files:
        print(f"No log files found for spider '{spider_name}' in {spider_dir}")
        return None

    def extract_timestamp(log_file):
        try:
            # Extract the timestamp part from the filename (after 'spidername_log_')
            timestamp_str = log_file.split('_log_')[-1].replace(log_extension, '')
            return datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except ValueError:
            # Handle files without valid timestamps or incorrect format
            print(f"Skipping file with invalid timestamp format: {log_file}")
            return None

    # Filter out files with invalid timestamps and sort the remaining by timestamp
    log_files_with_timestamp = [(file, extract_timestamp(file)) for file in log_files]
    log_files_with_timestamp = [item for item in log_files_with_timestamp if item[1] is not None]

    if not log_files_with_timestamp:
        print(f"No valid log files with timestamp found for spider '{spider_name}'")
        return None

    # Sort by the extracted timestamp
    log_files_with_timestamp.sort(key=lambda x: x[1])

    latest_log_file = log_files_with_timestamp[-1][0]
    print(f"Reading latest log file: {latest_log_file}")

    # Read and yield lines from the latest log file
    try:
        with open(latest_log_file, 'r') as f:
            for line in f.readlines():
                yield line.strip()  # Yield each line, stripped of leading/trailing whitespace
    except Exception as e:
        print(f"Error reading {latest_log_file}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    latest_log = read_spider_logs('walmart_spider')
    if latest_log:
        for line in latest_log:
            print(line)
