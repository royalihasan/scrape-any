
# Project: Scrape-Any

This project is a web scraper built using Scrapy for collecting product data from e-commerce websites. It integrates with a PostgreSQL database to store pricing and product details and features a UI for controlling and monitoring the scraping process.

---

## 1. Installation

### Python Version
- Ensure that you have **Python 3.x** installed.

### Setting up a Virtual Environment
To keep dependencies isolated, it is recommended to set up a Python virtual environment.

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

### Installing Dependencies
All required Python packages are listed in `requirements.txt`. To install them, use:

```bash
pip install -r requirements.txt
```

The main dependencies include:

- `Scrapy==2.11.2`: The web scraping framework.
- `PyYAML==6.0.2`: For handling YAML configuration.
- `psycopg2-binary==2.9.1`: PostgreSQL adapter for Python.
- `price-parser==0.3.4`: For parsing pricing information.
- `Flask==3.0.3`: For the backend server.
- `Flask-Cors==5.0.0`: For handling CORS in the backend.


---

## 2. Configuration

### Database Configuration (PostgreSQL)
The scraper stores collected data in a PostgreSQL database. Below is the sample configuration for connecting to the database:

Access the `src/scrape_any_crawler/pipe/e_comm_psql_pipe.py` file and update the database connection details:
```python
import psycopg2

self.connection = psycopg2.connect(
    dbname='e_commerce',  # Change to your database name
    user='scrapy',
    password='scrapy',
    host='localhost',  # Change if hosted externally
    port='5432'
)
```

Ensure that your PostgreSQL database is set up with the following credentials:
- **Database Name**: `e_commerce`
- **Username**: `scrapy`
- **Password**: `scrapy`
- **Host**: `localhost`
- **Port**: `5432`

### Docker Configuration for PostgreSQL
To simplify the database setup, you can run PostgreSQL in a Docker container. Below is the `docker-compose.yml` configuration:

```yaml
version: '3.9'

services:
  psql:
    image: postgres:latest
    container_name: psql
    restart: always
    environment:
      POSTGRES_USER: scrapy
      POSTGRES_PASSWORD: scrapy
      POSTGRES_DB: e_commerce
    ports:
      - "5432:5432"
    volumes:
      - ./data:/var/lib/postgresql/data
```

To set up PostgreSQL using Docker:
1. Ensure Docker is installed and running on your machine.
2. Run the following command to start the PostgreSQL service:
   ```bash
   docker-compose up -d
   ```

This will start a PostgreSQL instance with the necessary configurations. Make sure PostgreSQL is running before you start the scraper.

---

## 3. Running the Scraper

To run the scraper, navigate to the root directory and use the provided setup script:

```bash
python setup.py
```

When prompted, you will be given three options:
- Enter '1' to run the backend server.
- Enter '2' to run the UI.
- Enter '3' to run both the server and the UI simultaneously.

Choose the appropriate option based on your needs.

---

## 4. Accessing the UI

The project includes a user-friendly interface for controlling the scraper. Once the UI is running, you can access it by navigating to:

```
http://localhost:5173
```
### Sample Urls to Scrape
- `https://www.walmart.com/browse/electronics/3944`
- `https://shop.wegmans.com/shop/categories/216`
- `https://shop.sprouts.com/shop/categories/124`
- `ttps://www.aldi.us/products/snacks`

### Using the UI
1. Enter the URL of the website you want to scrape in the input box.
2. Click the "Start Scraping" button to begin the scraping process.
3. You will be able to monitor the progress through the logs.



---

## 5. Additional Notes

### Directory Structure
Here is a basic breakdown of the key directories:

- `src/scrape_any_crawler/spiders/`: Contains Scrapy spiders responsible for scraping different websites.
- `data/`: Volume for storing PostgreSQL data if running the database via Docker.
- `ui/`: Contains files related to the user interface for controlling the scraping process.

### Logs
Log files are generated during the scraping process. Each spider has its own log file located in a designated `log_dumps` directory. You can stream and view these logs directly from the UI.

### Database Management
Ensure that the PostgreSQL service is running before starting the scraper to avoid connection issues. If using Docker, remember to start the container before executing the scraper.

