import os
from sqlalchemy import create_engine
from config import (
    SOURCE_DB_USERNAME,
    SOURCE_DB_PASSWORD,
    SOURCE_DB_HOST,
    SOURCE_DB_PORT,
    SOURCE_DB_NAME,
    WAREHOUSE_DB_USERNAME,
    WAREHOUSE_DB_PASSWORD,
    WAREHOUSE_DB_HOST,
    WAREHOUSE_DB_PORT,
    WAREHOUSE_DB_NAME,
)


def create_directories():
    """
    Creates a set of directories if they do not already exist.

    This function checks for the existence of the directories specified in the
    `directories` list. If a directory does not exist, it creates the directory
    and prints a message indicating that the directory was created. If the directory
    already exists, it prints a message indicating that the directory already exists.

    Directories created:
    - data/raw
    - data/transform
    - data/load
    """
    directories = ["data/raw", "data/transform", "data/load"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory created: {directory}")
        else:
            print(f"Directory already exists: {directory}")


def source_db_engine():
    """
    Creates and returns a SQLAlchemy engine for connecting to the source database.

    The engine is configured using environment variables for the database
    credentials and connection details, including username, password, host, port,
    and database name.

    Returns:
        sqlalchemy.engine.Engine: A SQLAlchemy engine instance for the source database.
    """
    engine = create_engine(
        f"postgresql://{SOURCE_DB_USERNAME}:{SOURCE_DB_PASSWORD}@{SOURCE_DB_HOST}:{SOURCE_DB_PORT}/{SOURCE_DB_NAME}"
    )

    return engine


def dw_engine():
    """
    Creates and returns a SQLAlchemy engine for connecting to the data warehouse.

    The engine is configured using environment variables for the warehouse
    database credentials and connection details.

    Returns:
        sqlalchemy.engine.base.Engine: A SQLAlchemy engine instance for the
        warehouse database.
    """
    warehouse_engine = create_engine(
        f"postgresql://{WAREHOUSE_DB_USERNAME}:{WAREHOUSE_DB_PASSWORD}@{WAREHOUSE_DB_HOST}:{WAREHOUSE_DB_PORT}/{WAREHOUSE_DB_NAME}"
    )

    return warehouse_engine
