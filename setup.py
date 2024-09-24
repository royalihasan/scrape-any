import psycopg2

def test_postgres_connection():
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            dbname='e_commerce',  # Change to your database name
            user='scrapy',
            password='scrapy',
            host='localhost',  # Change to your host if it's different
            port='5432'         # Default PostgreSQL port
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print(f"Connected to PostgreSQL database version: {db_version}")
        
    except Exception as error:
        print(f"Error connecting to PostgreSQL: {error}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    test_postgres_connection()
