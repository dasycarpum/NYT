#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-29

@author: Roland

@abstract: load the 3 relational tables (book, rank and review) into the PosGreSQL database from individual csv or json files

"""

import json
import pandas as pd
from sqlalchemy import text


def load_book_into_database(file, engine, table):
    """
    Uploads data 'book' from a JSON file into a PostgreSQL database, while preventing duplicates.

    This function reads a JSON file and uploads its data into a specified PostgreSQL database. It checks for duplicates based on the 'id' key in the JSON data before appending the new data to the specified table in the database.

    Args:
        file (str): The path to the JSON file to be read.
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.
        table (str): The name of the table within the database where the data will be stored.

    Returns:
        None

    """
    # Read existing ids from the table
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT id FROM {table}"))
        existing_ids = [row[0] for row in result]
        
    # Read data from JSON file
    with open(file, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
        
    # Check if id in the JSON data exists in the table
    if data_json['id'] not in existing_ids:
        # If it doesn't exist, insert the whole JSON object into the 'data' column
        id_value = data_json.pop('id')  # Remove 'id' from JSON and keep its value
        with engine.connect() as connection:
            connection.execute(text(f"INSERT INTO {table} (id, data) VALUES (:id, :data)"), {'id': id_value, 'data': json.dumps(data_json)})
            connection.commit()


def load_rank_into_database(file, engine, table):
    """
    Uploads data 'rank' from a CSV file into a PostgreSQL database, while preventing duplicates.

    This function reads a CSV file and uploads its data into a specified PostgreSQL database. It checks for duplicates based on the combination of 'id_book', 'date', and 'category' before appending the new data to the specified table in the database.

    Args:
        file (str): The path to the CSV file to be read.
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.
        table (str): The name of the table within the database where the data will be stored.

    Returns:
        None

    """
     # Read data from CSV file
    data = pd.read_csv(file) 
    
    # Read existing data from the table
    existing_data = pd.read_sql(table, engine)
    
    # Convert date column to datetime object in both dataframes for proper comparison
    data['date'] = pd.to_datetime(data['date'])
    existing_data['date'] = pd.to_datetime(existing_data['date'])

    # Combine the three columns to create a single identifier for each row
    data['combined_key'] = data['id_book'].astype(str) + data['date'].astype(str) + data['category']
    existing_data['combined_key'] = existing_data['id_book'].astype(str) + existing_data['date'].astype(str) + existing_data['category']

    # Only keep rows from the new data where combined_key does not exist in the existing data
    data = data[~data.combined_key.isin(existing_data.combined_key)]

    # Drop the combined_key column as it's no longer needed
    data.drop(columns=['combined_key'], inplace=True)
    
    # If there is any new data, append it to the table
    if len(data) > 0:
        data.to_sql(table, engine, if_exists='append', index=False)


def load_review_into_database(file, engine, table):
    """
    Uploads data 'review' from a CSV file into a PostgreSQL database, while preventing duplicates.

    This function reads a CSV file and uploads its data into a specified PostgreSQL database. It checks for duplicates based on the combination of 'id_book' and 'id_review'  before appending the new data to the specified table in the database.

    Args:
        file (str): The path to the CSV file to be read.
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.
        table (str): The name of the table within the database where the data will be stored.

    Returns:
        None

    """
     # Read data from CSV file
    data = pd.read_csv(file)
    print("data 1 :", data.shape)
    # Read existing data from the table
    existing_data = pd.read_sql(table, engine)

    # Convert date column to datetime object in both dataframes for proper comparison
    data['date'] = pd.to_datetime(data['date'])
    existing_data['date'] = pd.to_datetime(existing_data['date'])

    # Combine the two columns to create a single identifier for each row
    # Pad 'id_review' with leading zeros to ensure consistent length
    data['combined_key'] = data['id_book'].astype(str) + data['id_review'].astype(str).str.zfill(5)  # assuming max 99999 reviews
    existing_data['combined_key'] = existing_data['id_book'].astype(str) + existing_data['id_review'].astype(str).str.zfill(5)

    # Only keep rows from the new data where combined_key does not exist in the existing data
    data = data[~data.combined_key.isin(existing_data.combined_key)]

    # Drop the combined_key column as it's no longer needed
    data.drop(columns=['combined_key'], inplace=True)
    print("data 2 :", data.shape)
    # If there is any new data, append it to the table
    if len(data) > 0:
        data.to_sql(table, engine, if_exists='append', index=False)
