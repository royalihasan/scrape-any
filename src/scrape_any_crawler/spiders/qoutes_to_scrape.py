from typing import Iterable
import scrapy
from bs4 import BeautifulSoup, Comment
import re
import htmlmin


class HtmlCleanupSpider(scrapy.Spider):
    name = "html_cleanup"
    start_urls = ["https://walmart.com"]  # Add your target URLs here
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
        'COOKIES_DEBUG': True,
        'COOKIES_ENABLED': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": False,
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 5000000
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'playwright': True})

    def parse(self, response):
        # Get the HTML content
        html_content = response.body

        # Log the HTML content
        print(html_content)

        

    def clean_html(self, html_content):
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove unwanted tags (scripts, styles, etc.)
        for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside', 'form', 'input']):
            tag.decompose()

        # Remove comments
        for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Process all div tags
        for tag in soup.find_all('div'):
            # If the div contains only text (no nested tags), keep it
            if all(isinstance(child, str) for child in tag.contents):
                continue
            # Otherwise, unwrap the tag (remove it but keep its contents)
            tag.unwrap()

        # Remove attributes from all tags except <a> and <img>
        for tag in soup.find_all(True):
            if tag.name in ['a', 'img']:
                # Keep only specific attributes for <a> and <img> tags
                tag.attrs = {key: val for key, val in tag.attrs.items() if key in [
                    'href', 'src', 'alt']}
            else:
                # Remove all attributes for other tags
                tag.attrs = {}

        # Minify the HTML
        minified_html = htmlmin.minify(
            str(soup), remove_empty_space=True, remove_comments=True)

        return minified_html

    def extract_text(self, cleaned_html):
        # Convert the cleaned HTML to plain text
        soup = BeautifulSoup(cleaned_html, "html.parser")
        plain_text = soup.get_text(separator='\n', strip=True)

        # Further process or chunk the text if needed
        chunks = self.chunk_content(plain_text)
        return chunks

    def chunk_content(self, text, chunk_size=500):
        # Break the content into smaller chunks
        words = text.split()
        for i in range(0, len(words), chunk_size):
            yield ' '.join(words[i:i + chunk_size])
