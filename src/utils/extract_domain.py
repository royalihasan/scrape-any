from urllib.parse import urlparse


def extract_domain_name(url):
    """Extracts the domain name from a given URL, without subdomains or TLDs."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]

    # Split by '.' and return the second to last part
    parts = domain.split('.')
    if len(parts) > 2:
        # Handles cases like 'blog.example.co.uk' -> 'example'
        return parts[-2]
    else:
        # Handles cases like 'example.com' -> 'example'
        return parts[0]


if __name__ == "__main__":

    # Example usage:
    urls = [
        'https://www.amazon.com/product/B07PGL2N7J',
        'http://blog.example.co.uk/some-post/',
        'https://example.com',
        'ftp://ftp.example.com/file.txt',
        'https://www.google.co.uk/search?q=test'
    ]

for url in urls:
    print(f"URL: {url} -> Domain Name: {extract_domain_name(url)}")
