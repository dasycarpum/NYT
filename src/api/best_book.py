#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-08

@author: Roland

@abstract: by setting the book genre and year of publication, the API will return the titles and authors of the top 5 bestsellers, based on the number of weeks remaining in the ranking.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
# from config import DB_ENGINE

DB_NAME = 'nyt'
DB_USER = 'postgres'
DB_PASS = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_ENGINE='postgresql://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME


try:
    # Attempt to create the database engine
    engine = create_engine(DB_ENGINE)
except Exception as e:
    raise RuntimeError(f"Failed to create database engine: {e}")


query = """
    WITH UniqueBooks AS (
        SELECT DISTINCT ON (b.data->>'author', b.data->>'title')
            b.data->>'title' AS title,
            b.data->>'author' AS author,
            r.weeks_on_list
        FROM
            book AS b
        JOIN
            rank AS r ON b.id = r.id_book
        WHERE
            b.data->>'publication_date' LIKE '2020-%'
            AND b.data->>'genre' = 'Mysteries & Thrillers'
        ORDER BY
            b.data->>'author',
            b.data->>'title',
            r.weeks_on_list DESC
    )
    SELECT json_agg(row_to_json(UniqueBooks.*))
    FROM (SELECT * FROM UniqueBooks ORDER BY weeks_on_list DESC LIMIT 5) AS UniqueBooks;
    """

try:
    with engine.connect() as connection:
        result = connection.execute(text(query))
        best_book_json = result.fetchone()[0]  # This should be a JSON array

        # Check if the DataFrame is empty
        if not best_book_json:
            raise ValueError("Fetched dataset is empty.")
        print(best_book_json)

except SQLAlchemyError as e:
    # Specific handling for SQLAlchemy errors
    raise RuntimeError(f"SQLAlchemy error occurred: {e}")
except Exception as e:
    # General error handling
    raise RuntimeError(f"Failed to fetch dataset: {e}")




