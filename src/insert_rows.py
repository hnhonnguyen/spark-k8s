import argparse
import os
import logging
import pandas as pd
from sqlalchemy import create_engine
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to generate a random string
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

# Function to insert random rows into the database
def insert_random_rows(engine, n):
    usernames = [generate_random_string(8) for _ in range(n)]
    emails = [f"{username}@example.com" for username in usernames]
    passwords = [generate_random_string(10) for _ in range(n)]

    data = {'username': usernames, 'email': emails, 'password': passwords}
    df = pd.DataFrame(data)

    df.to_sql('users', engine, schema='tmp', if_exists='append', index=False)

def main(db_name, db_user, db_password, db_host, db_port):
    # Create SQLAlchemy engine
    db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(db_url)

    # Insert random rows into the database
    try:
        # Connect to the database
        with engine.connect() as conn:
            logger.info("Connected to the database.")

            # Insert random rows into tmp.users
            num_rows = random.randint(1, 10)  # Generate a random number of rows to insert (1 to 10)
            insert_random_rows(conn, num_rows)
            logger.info(f"{num_rows} random rows inserted successfully.")

    except Exception as e:
        logger.error("Error: Unable to connect to the database.")
        logger.error(e)

    finally:
        engine.dispose()
        logger.info("Database connection closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Insert random rows into a PostgreSQL database.')
    parser.add_argument('--db_name', help='Database name')
    parser.add_argument('--db_user', help='Database username')
    parser.add_argument('--db_password', help='Database password')
    parser.add_argument('--db_host', help='Database host')
    parser.add_argument('--db_port', help='Database port')

    args = parser.parse_args()

    # If command-line arguments are not provided, fall back to environment variables
    db_name = args.db_name or os.environ.get('DB_NAME')
    db_user = args.db_user or os.environ.get('DB_USER')
    db_password = args.db_password or os.environ.get('DB_PASSWORD')
    db_host = args.db_host or os.environ.get('DB_HOST')
    db_port = args.db_port or os.environ.get('DB_PORT')

    if not all([db_name, db_user, db_password, db_host, db_port]):
        print("Error: Please provide all required arguments or set environment variables.")
        exit(1)

    main(db_name, db_user, db_password, db_host, db_port)
