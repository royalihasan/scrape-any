import psycopg2
import json

# Sample JSON string (you can load it from a file or API)
json_data = '''
{
  "product_id": "12345",
  "product_name": "Sample Product",
  "store_name": "Sample Store",
  "brand": "BrandX",
  "product_url": "http://example.com/product",
  "description": "This is a sample product.",
  "model": "X-123",
  "rating": 4.5,
  "sku": "ABC123",
  "availability": "In Stock",
  "date_scraped": "2024-09-08",
  "images": [
    {
      "store": "Store A",
      "type": "thumbnail",
      "url": "http://example.com/image1.jpg"
    },
    {
      "store": "Store B",
      "type": "full",
      "url": "http://example.com/image2.jpg"
    }
  ],
  "category": {
    "name": "food",
    "section": "Chiller",
    "path": "/food, Chiller"
  }
}
'''

# Convert the JSON string to a dictionary
product_data = json.loads(json_data)

print(product_data)


# Database connection details
conn = psycopg2.connect(
    dbname='e_commerce',  # Change to your database name
    user='scrapy',
    password='scrapy',
    host='localhost',  # Change to your host if it's different
    port='5432'         # Default PostgreSQL port
)

# Create a cursor object
cur = conn.cursor()

# Insert data into Product_Table
product_insert_query = '''
INSERT INTO product (product_id, product_name, store_name, brand, product_url, description, model, rating, sku, availability, date_scraped)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (product_id) DO NOTHING;  -- Prevents duplicates if product_id already exists
'''

# Product data from the dictionary
cur.execute(product_insert_query, (
    product_data['product_id'],
    product_data['product_name'],
    product_data['store_name'],
    product_data['brand'],
    product_data['product_url'],
    product_data['description'],
    product_data['model'],
    product_data['rating'],
    product_data['sku'],
    product_data['availability'],
    product_data['date_scraped']
))

# Insert data into Category_Table
category_insert_query = '''
INSERT INTO category (name, section, path, product_id)
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING;
'''

cur.execute(category_insert_query, (
    product_data['category']['name'],
    product_data['category']['section'],
    product_data['category']['path'],
    product_data['product_id']
))

# Insert data into Image_Table for each image
image_insert_query = '''
INSERT INTO images (store, type, url, product_id)
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING;
'''

for image in product_data['images']:
    cur.execute(image_insert_query, (
        image['store'],
        image['type'],
        image['url'],
        product_data['product_id']
    ))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("Data inserted successfully!")
