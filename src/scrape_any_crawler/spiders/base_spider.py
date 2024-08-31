from typing import Iterable
import scrapy
from bs4 import BeautifulSoup, Tag
from typing import List, Dict
import json
from meta_ai_api import MetaAI
import time


class BaseSpider(scrapy.Spider):
    name = 'base_spider'
    allowed_domains = ['daraz.pk']
    start_urls = [
        'https://www.daraz.pk/#hp-just-for-you']

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
            yield scrapy.Request(url=url, callback=self.parse_html, meta={'playwright': True})

    def parse_html(self, response):
        print("Doc"+response.body)
        soup = BeautifulSoup(response.text, 'lxml')

        # Remove unwanted tags
        self.remove_unwanted_tags(soup)

        flat_html_content = BeautifulSoup(self.flatten_html(soup), 'lxml')
        self.logger.info("Flat HTML content processed.")
        cleaned_html = self.format_content(flat_html_content)
        chunked_content = self.chunk_content(cleaned_html)
        chunk_count = len(chunked_content)
        print("Cleaned Html"+cleaned_html)

        # Process chunks with MetaAI
        json_data = self.process_with_metaai(chunked_content)

        item = {
            'url': response.url,
            'cleaned_html': json_data,
        }

        yield item

    def remove_unwanted_tags(self, soup):
        """Remove unwanted tags from BeautifulSoup object."""
        for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'aside', 'form', 'input']):
            tag.decompose()

    def format_content(self, soup):
        """
        Extract text from tags and format them according to the requirements.
        """
        content = []
        open_tags = []  # Stack to keep track of opened tags

        def has_content(tag):
            """Check if the tag or its children contain meaningful content."""
            if tag.name in ['script', 'style', 'head']:
                return False
            if tag.name == 'div':
                if tag.get_text(strip=True):
                    return True
                for child in tag.contents:
                    if isinstance(child, Tag) and has_content(child):
                        return True
                    elif isinstance(child, str) and child.strip():
                        return True
            return False

        def handle_tag(tag):
            if tag.name == 'div':
                if has_content(tag):
                    if open_tags and open_tags[-1] == 'div':
                        content.append("[/div]")
                    content.append("[div]")
                    open_tags.append('div')
                else:
                    return  # Skip empty <div> tags
            elif tag.name == 'p':
                content.append(f"p: {tag.get_text(strip=True)}")
            elif tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content.append(f"h{tag.name[1]}: {tag.get_text(strip=True)}")
            elif tag.name == 'ul':
                content.append("[ul]")
                content.extend(f"li: {li.get_text(strip=True)}" for li in tag.find_all(
                    'li', recursive=False))
                content.append("[/ul]")
            elif tag.name == 'ol':
                content.append("[ol]")
                content.extend(f"li: {li.get_text(strip=True)}" for li in tag.find_all(
                    'li', recursive=False))
                content.append("[/ol]")
            elif tag.name == 'span':
                content.append(f"span: {tag.get_text(strip=True)}")
            elif tag.name == 'a':
                href = tag.get('href', 'no href')
                content.append(f"a: {tag.get_text(strip=True)} (href: {href})")
            elif tag.name == 'img':
                src = tag.get('src', 'no src')
                alt = tag.get('alt', 'no alt')
                content.append(f"img: (src: {src}, alt: {alt})")
            else:
                pass

            if tag.name not in ['div', 'ul', 'ol']:
                if open_tags and open_tags[-1] == 'div':
                    content.append("[/div]")
                    open_tags.pop()

        for tag in soup.find_all(True):
            handle_tag(tag)

        # Close any remaining open tags
        while open_tags:
            content.append("[/div]")
            open_tags.pop()

        return '\n'.join(content)

    def flatten_html(self, soup):
        """
        Recursively flatten HTML from BeautifulSoup object.
        """
        def flatten(tag):
            if isinstance(tag, Tag):
                tag_html = f'<{tag.name}'
                if tag.name in ['a', 'img']:
                    for attr, value in tag.attrs.items():
                        tag_html += f' {attr}="{value}"'
                tag_html += '>'

                for child in tag.contents:
                    if isinstance(child, Tag):
                        tag_html += flatten(child)
                    elif isinstance(child, str):
                        tag_html += child

                if tag.name not in ['img']:
                    tag_html += f'</{tag.name}>'

                return tag_html
            return ''

        return flatten(soup)

    def chunk_content(self, content: str) -> List[str]:
        """
        Split the content into chunks of up to 1000 tokens, ensuring each chunk ends with a closing tag.
        """
        token_limit = 1000  # Define the token limit for chunks
        chunks = []
        current_chunk = []

        # Tokenize and chunk content
        tokens = content.split()
        token_count = 0

        for token in tokens:
            # Number of tokens in the current token
            token_length = len(token.split())
            if token_count + token_length > token_limit:
                # Ensure we end the chunk with a closing tag if necessary
                if current_chunk and current_chunk[-1] != "[/div]":
                    current_chunk.append("[/div]")
                chunks.append(' '.join(current_chunk))
                current_chunk = [token]
                token_count = token_length
            else:
                current_chunk.append(token)
                token_count += token_length

        # Add the last chunk
        if current_chunk:
            if current_chunk[-1] != "[/div]":
                current_chunk.append("[/div]")
            chunks.append(' '.join(current_chunk))

        return chunks

    def process_with_metaai(self, chunks: List[str], delay: int = 1) -> List[Dict]:
        """
        Send a list of chunks to the MetaAI model and get the response for each chunk.

        Args:
            chunks (List[str]): List of text chunks to be processed.
            delay (int): Time in seconds to wait between processing each chunk.

        Returns:
            List[Dict]: List of responses from the MetaAI model for each chunk.
        """
        ai = MetaAI()
        all_responses = []

        for chunk in chunks:
            message = (
                "You are a specialist in transforming raw text into structured product data. "
                "I'll give you text from a webpage that describes various products. "
                "Your task is to convert this text into a JSON format with the following fields: "
                "`name`, `price`, `description`, `image_url`, and `category`. "
                "If any field is missing or the information is unclear, use `null` for that field and indicate that the value is missing.\n\n"
                "Please make sure the JSON output is correctly formatted and includes only the specified fields. "
                "The output should be in a format suitable for e-commerce websites. Avoid adding any additional information or personal references.\n\n"
                f"Here is the text:\n{chunk}\n\n"
            )

            try:
                response = ai.prompt(message=str(message), attempts=2)
                self.logger.info("Response from MetaAI: %s", response)
                json_data = self.convert_response_to_json(response)
                for data in json_data:
                    all_responses.append(data)
                self.logger.info("Processed chunk: %s", chunk)
            except Exception as e:
                self.logger.error("Error processing chunk: %s", e)

            # Wait for the specified delay before processing the next chunk
            time.sleep(delay)
        return all_responses

    def convert_response_to_json(self, response):
        """
        Convert the MetaAI response to proper JSON format.

        Args:
        response (Dict): The response dictionary from MetaAI containing the JSON schema as a string.

        Returns:
        List[Dict]: The JSON data parsed into a Python list of dictionaries.
        """
        try:
            # Extract the JSON string from the 'message' key
            json_string = response.get('message', '')

        # Find the start of the actual JSON array in the string
            json_start = json_string.find("[")

            if json_start != -1:
                # Extract the JSON part from the string
                json_data = json_string[json_start:json_string.rfind(
                    "]")+1]

            # Replace escape characters and fix formatting issues
                json_data = json_data.replace('\n', '')
                json_data = json_data.replace('\\', '')

            # Parse the JSON string into a Python list of dictionaries
                parsed_json = json.loads(json_data)
                return parsed_json
            else:
                raise ValueError(
                    "JSON array not found in the response message.")

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        return []
