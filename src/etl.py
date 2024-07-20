import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import event

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log function for SQLAlchemy
def log_sql(statement, *multiparams, **params):
    logger.info(statement)

# Retrieve connection parameters from environment variables
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

# Construct the database URL
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
logger.info(f"Database URL: {db_url}")

# Connect to PostgreSQL using SQLAlchemy
engine = create_engine(db_url)

# Attach logging event listener to the engine
event.listen(engine, "before_cursor_execute", log_sql)

# Fetch new rows from the source table that do not exist in the destination table
query = """
    SELECT src.*
    FROM tmp.users src
    LEFT JOIN tmp.users_cleansed dest ON src.id = dest.id
    WHERE dest.id IS NULL
"""
logger.info("Executing SQL query to fetch new rows...")
df = pd.read_sql_query(query, engine)

if not df.empty:
    logger.info("Found new rows. Performing transformation and insertion...")
    # Transformation: Append 'cleaned' to email
    df['email'] = df['email'].str.lower() + 'cleaned'

    # Insert data into users_cleansed table
    df.to_sql('users_cleansed', engine, schema='tmp', if_exists='append', index=False)
    logger.info("Data insertion successful.")
else:
    logger.info("No new rows found.")

# Dispose the engine
engine.dispose()
logger.info("Database connection closed.")
