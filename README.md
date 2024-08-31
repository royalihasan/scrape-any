# Scrape-Any

**Scrape-Any** is a powerful web scraping tool designed to extract data from any website, utilizing advanced Large Language Models (LLMs) for intelligent content processing. Whether you're dealing with static HTML or dynamic JavaScript-rendered content, **Scrape-Any** provides a robust solution for all your web scraping needs.

## Key Features

- **Versatile Scraping:** Capable of scraping various types of websites including blogs, e-commerce sites, and social media platforms.
- **LLM-Powered Extraction:** Uses state-of-the-art Large Language Models to understand and extract structured data from complex web pages.
- **Dynamic Content Handling:** Integrates Playwright to handle and scrape content rendered by JavaScript.
- **Customizable Configuration:** Define and manage scraping tasks using a flexible YAML configuration file.
- **Scalable Architecture:** Built with scalability in mind, supporting multiple concurrent scraping tasks through a distributed system.

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or later
- Pip (Python package manager)
- Git (for cloning the repository)

### Steps to Install

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/royalihasan/scrape-any.git
    cd scrape-any
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Install Playwright:**
    ```bash
    playwright install
    ```

## Configuration

### Configuration File

The `config.yaml` file is used to define scraping tasks and parameters. Each entry specifies a spider, its target website, and how to process the scraped data. Example configuration:

```yaml
spiders:
  e_comm:
    - name: amazon_spider
      type: SpecificSpider
      domain: amazon.com
      module: e_comm.amazon_spider

    - name: walmart_spider
      type: SpecificSpider
      module: e_comm.walmart_spider
      domain: walmart.com
```