import os
import json

def get_latest_file(directory):
    """Get the latest file in a directory based on modification time."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def load_json_from_file(file_path):
    """Load JSON data from a file with UTF-8 encoding."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {file_path}: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"Error decoding file {file_path} with UTF-8 encoding: {e}")
        return None

def process_dumps(dumps_dir):
    """Process the latest dump file and load it into JSON."""
    # Get the spider directory path
    spider_dirs = [d for d in os.listdir(dumps_dir) if os.path.isdir(os.path.join(dumps_dir, d))]
    if not spider_dirs:
        raise FileNotFoundError("No spider directories found in the dumps directory.")

    latest_files = {}
    for spider_dir in spider_dirs:
        spider_path = os.path.join(dumps_dir, spider_dir)
        latest_file = get_latest_file(spider_path)
        if latest_file:
            latest_files[spider_dir] = latest_file

    if not latest_files:
        raise FileNotFoundError("No files found in spider directories.")

    # Load JSON from the latest files
    json_data = {}
    for spider_dir, file_path in latest_files.items():
        print(f"Loading data from {file_path} for spider {spider_dir}")
        json_content = load_json_from_file(file_path)
        if json_content is not None:
            json_data[spider_dir] = json_content

    return json_data

if __name__ == "__main__":
    dumps_directory = 'src/dumps/data/walmart_spider'
    try:
        data = process_dumps(dumps_directory)
        print(data)
    except Exception as e:
        print(f"An error occurred: {e}")
