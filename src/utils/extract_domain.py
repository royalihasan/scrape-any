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


def extract_full_domain(url):
    """Extracts the full domain name from a given URL, including subdomains but without the scheme or path."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


if __name__ == "__main__":

    # Example usage:
    urls = [
        "https://www.wholefoodsmarket.com/",
        "https://www.aldi.us/",
        "https://www.lidl.com/",
        "https://www.wegmans.com/",
        "https://www.harristeeter.com/",
        "https://www.safeway.com/",
        "https://giantfood.com/",
        "https://www.costco.com/",
        "https://www.bjs.com/",
        "https://www.walmart.com",
        "https://www.sprouts.com",

    ]

    for url in urls:
        print(f"URL: {url} -> Domain Name: {extract_full_domain(url)}")
