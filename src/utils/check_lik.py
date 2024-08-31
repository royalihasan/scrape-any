import requests

def is_link_working(url):
    """Checks if a given URL is working (not broken)."""
    try:
        # Use requests.get instead of requests.head
        response = requests.get(url, allow_redirects=True, timeout=10)
        print(response.status_code)
        # Consider the link working if status code is in the range 200-399
        if 200 <= response.status_code < 400:
            return True
        else:
            return False
    except requests.RequestException as e:
        # Catch exceptions that may occur (e.g., connection errors, timeouts)
        print(f"Error checking {url}: {e}")
        return False

if __name__ == "__main__":
    # Example usage:
    urls = [
        'https://www.amazon.com',
        'https://www.nonexistentwebsite12345.com',
        'https://www.google.com',
        'http://example.com/nonexistentpage'
    ]

    for url in urls:
        status = "Working" if is_link_working(url) else "Broken"
        print(f"URL: {url} -> Status: {status}")
