from dotenv import load_dotenv
import os

load_dotenv()

# Reddit
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
SECRET_KEY = os.getenv("REDDIT_SECRET_KEY")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Source Database
SOURCE_DB_USERNAME = os.getenv("SOURCE_DB_USERNAME")
SOURCE_DB_PASSWORD = os.getenv("SOURCE_DB_PASSWORD")
SOURCE_DB_HOST = os.getenv("SOURCE_DB_HOST")
SOURCE_DB_PORT = os.getenv("SOURCE_DB_PORT")
SOURCE_DB_NAME = os.getenv("SOURCE_DB_NAME")

# Warehouse Database
WAREHOUSE_DB_USERNAME = os.getenv("WAREHOUSE_DB_USERNAME")
WAREHOUSE_DB_PASSWORD = os.getenv("WAREHOUSE_DB_PASSWORD")
WAREHOUSE_DB_HOST = os.getenv("WAREHOUSE_DB_HOST")
WAREHOUSE_DB_PORT = os.getenv("WAREHOUSE_DB_PORT")
WAREHOUSE_DB_NAME = os.getenv("WAREHOUSE_DB_NAME")

# Fetch Data
SUBREDDIT = os.getenv("SUBREDDIT")
LIMIT = int(os.getenv("LIMIT"))  # type: ignore
