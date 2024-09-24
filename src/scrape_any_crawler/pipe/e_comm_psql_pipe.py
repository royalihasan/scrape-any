import psycopg2
import logging


class PostgresPipeline:

    def open_spider(self, spider):
        # Connecting to PostgreSQL database
        try:
            self.connection = psycopg2.connect(
                dbname='e_commerce',  # Change to your database name
                user='scrapy',
                password='scrapy',
                host='localhost',  # Change to your host if it's different
                port='5432'
            )
            self.cursor = self.connection.cursor()
            logging.info("Connected to the PostgreSQL database.")
        except Exception as e:
            logging.error(f"Error connecting to the PostgreSQL database: {e}")

    def close_spider(self, spider):
        # Commit the transactions and close the connection
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        try:
            # Fill in missing fields
            required_fields = ['product_id', 'name', 'brand', 'product_url', 'price',
                               'sku', 'availability', 'rating', 'description', 'model', 'date_scraped', 'store', 'currency']

            for field in required_fields:
                items = f'{field} field type {
                    type(item[field] if field in item else None)}'
                print(items)
                if field not in item or item[field] is None:
                    item[field] = None

            # Upsert data into Product Table
            self.upsert_product(item)

            # Upsert data into Category Table
            if 'category' in item and item['category']:
                self.upsert_category(item['category'], item['product_id'])

            # Upsert data into Image Table
            if 'images' in item and item['images']:
                self.upsert_images(item['images'], item['product_id'])

            # Update or Insert into Price History Table
            if 'price' in item and item['price'] is not None:
                self.update_price_history(item['product_id'], item['price'])

            # Commit after successful upserts
            self.connection.commit()
        except Exception as e:
            logging.error(f"Error processing item: {e}")
            self.connection.rollback()  # Rollback the transaction if an error occurs

        return item

    def upsert_product(self, item):
        # Upsert product data into the Product Table
        query = """
            INSERT INTO product (product_id, product_name, brand, product_url, price, sku, availability, rating, description, model,store,currency, date_scraped)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s)
            ON CONFLICT (product_id) 
            DO UPDATE SET
                product_name = EXCLUDED.product_name,
                brand = EXCLUDED.brand,
                product_url = EXCLUDED.product_url,
                price = EXCLUDED.price,
                sku = EXCLUDED.sku,
                availability = EXCLUDED.availability,
                rating = EXCLUDED.rating,
                description = EXCLUDED.description,
                model = EXCLUDED.model,
                store = EXCLUDED.store,
                currency = EXCLUDED.currency,
                date_scraped = EXCLUDED.date_scraped;
        """
        data = (
            item['product_id'],
            item['name'],
            item['brand'],
            item['product_url'],
            item['price'],
            item['sku'],
            item['availability'],
            item['rating'],
            item['description'],
            item['model'],
            item['store'],
            item['currency'],
            item['date_scraped']

        )

        try:
            self.cursor.execute(query, data)
        except Exception as e:
            logging.error(f"Error upserting product: {e}")
            raise  # Raising the exception will trigger rollback in process_item()

    def upsert_category(self, categories, product_id):
        # Upsert category data into the Category Table
        for category in categories:
            query = """
                INSERT INTO category (name, section, path, product_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name, section, product_id) 
                DO UPDATE SET
                    path = EXCLUDED.path;
            """
            data = (
                category['name'],
                category.get('section', None),
                category.get('path', None),
                product_id
            )

            try:
                self.cursor.execute(query, data)
            except Exception as e:
                logging.error(f"Error upserting category: {e}")
                raise  # Raising the exception will trigger rollback in process_item()

    def upsert_images(self, images, product_id):
        # Upsert image data into the Image Table
        for image in images:
            query = """
                INSERT INTO images (store, type, url, product_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (url, product_id) 
                DO UPDATE SET
                    store = EXCLUDED.store,
                    type = EXCLUDED.type;
            """
            data = (
                image.get('store', None),
                image.get('type', None),
                image.get('url', None),
                product_id
            )

            try:
                self.cursor.execute(query, data)
            except Exception as e:
                logging.error(f"Error upserting image: {e}")
                raise  # Raising the exception will trigger rollback in process_item()

    def update_price_history(self, product_id, new_price):
        # Check if there's an existing price record
        query = """
            SELECT price_history_id, current_price FROM price_history 
            WHERE product_id = %s
            ORDER BY last_updated DESC
            LIMIT 1;
        """
        self.cursor.execute(query, (product_id,))
        result = self.cursor.fetchone()

        if result:
            price_history_id, current_price = result
            # Check if the new price is different from the current price
            if new_price != current_price:
                # Update the price history: set current price as previous price and update the new price
                update_query = """
                    UPDATE price_history 
                    SET previous_price = current_price, current_price = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE price_history_id = %s;
                """
                self.cursor.execute(
                    update_query, (new_price, price_history_id))
                logging.info(f"Price updated for product_id {product_id}: Old Price = {
                             current_price}, New Price = {new_price}")
            else:
                logging.info(f"No price change for product_id {
                             product_id}. Current Price remains {current_price}.")
        else:
            # Insert new price details if no existing record found
            insert_query = """
                INSERT INTO price_history (product_id, current_price, previous_price) 
                VALUES (%s, %s, NULL);  -- NULL because there is no previous price yet
            """
            self.cursor.execute(insert_query, (product_id, new_price))
            logging.info(f"Inserted new price record for product_id {
                         product_id} with Price = {new_price}")
