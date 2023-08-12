#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-24

@author: Roland

@abstract: create for the 'load.py' source file,
    2 unit tests for the 'load_book_into_database' function,
    2 unit tests for the 'load_rank_into_database' function,
    2 unit tests for the 'load_review_into_database' function.
"""

import os
import sys
import json
from io import StringIO
import pytest
from unittest.mock import patch, mock_open
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd


# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'data_ingestion')
# Adding the absolute path to system path
sys.path.append(src_dir)
from load import load_book_into_database, load_rank_into_database, load_review_into_database


# The test tests the case where the book ID is not already in the database. It asserts that the INSERT statement was executed with the expected values.
def test_load_book_into_database_new():
    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as connection:
        connection.execute(text('CREATE TABLE test_table (id INT PRIMARY KEY, data TEXT)'))

    with patch('builtins.open', new_callable=mock_open, read_data='{"id": 4, "title": "New Book", "author": "John Doe"}'):
        load_book_into_database('file_path', engine, 'test_table')

    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM test_table')).fetchall()

    assert len(result) == 1
    assert result[0][0] == 4
    assert json.loads(result[0][1]) == {"title": "New Book", "author": "John Doe"}


# The test tests the case where the book ID is already in the database. It asserts that the INSERT statement was not executed.
def test_load_book_into_database_existing():
    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as connection:
        connection.execute(text('CREATE TABLE test_table (id INT PRIMARY KEY, data TEXT)'))
        connection.execute(text("INSERT INTO test_table (id, data) VALUES (:id, :data)"), {"id": 4, "data": json.dumps({"title": "New Book", "author": "John Doe"})})

    with patch('builtins.open', new_callable=mock_open, read_data='{"id": 4, "title": "New Book", "author": "John Doe"}'):
        load_book_into_database('file_path', engine, 'test_table')

    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM test_table')).fetchall()


    assert len(result) == 1  # There should still be only one record, as the insert should not have occurred
    assert result[0][0] == 4
    assert json.loads(result[0][1]) == {"title": "New Book", "author": "John Doe"}


# The test checks the function's ability to correctly insert new data into an empty database.
def test_load_rank_into_database_new():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as connection:
        connection.execute(text('CREATE TABLE test_table (id_book INT, date DATE, category TEXT, combined_key TEXT)'))

    csv_data = 'id_book,date,category\n1,2023-07-24,Fiction'
    
    # Mock the pd.read_csv function to return a DataFrame from our string
    with patch('pandas.read_csv', return_value=pd.read_csv(StringIO(csv_data))):
        load_rank_into_database('file_path', engine, 'test_table')

    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM test_table')).fetchall()

    assert len(result) == 1
    assert result[0][0] == 1
    assert pd.to_datetime(result[0][1]) == pd.to_datetime('2023-07-24')
    assert result[0][2] == 'Fiction'


# The test validates that the function correctly avoids inserting duplicate data into the database.
def test_load_rank_into_database_existing():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as connection:
        connection.execute(text('CREATE TABLE test_table (id_book INT, date DATE, category TEXT, combined_key TEXT)'))
        connection.execute(text('INSERT INTO test_table (id_book, date, category, combined_key) VALUES (1, "2023-07-24", "Fiction", "12023-07-24Fiction")'))

    csv_data = 'id_book,date,category\n1,2023-07-24,Fiction'

    # Mock the pd.read_csv function to return a DataFrame from our string
    with patch('pandas.read_csv', return_value=pd.read_csv(StringIO(csv_data))):
        load_rank_into_database('file_path', engine, 'test_table')

    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM test_table')).fetchall()

    assert len(result) == 1  # There should still be only one record, as the insert should not have occurred
    assert result[0][0] == 1
    assert pd.to_datetime(result[0][1]) == pd.to_datetime('2023-07-24')
    assert result[0][2] == 'Fiction'


# The test checks the function's ability to correctly insert new data into an empty database.
def test_load_review_into_database_new():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as connection:
        connection.execute(text('CREATE TABLE test_table (id_book INT, id_review INT, date DATE, combined_key TEXT)'))

    csv_data = 'id_book,id_review,date\n1,1,2023-07-24'
    
    # Mock the pd.read_csv function to return a DataFrame from our string
    with patch('pandas.read_csv', return_value=pd.read_csv(StringIO(csv_data))):
        load_review_into_database('file_path', engine, 'test_table')

    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM test_table')).fetchall()

    assert len(result) == 1
    assert result[0][0] == 1
    assert result[0][1] == 1
    assert pd.to_datetime(result[0][2]) == pd.to_datetime('2023-07-24')


# The test validates that the function correctly avoids inserting duplicate data into the database.
def test_load_review_into_database_existing():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as connection:
        connection.execute(text('CREATE TABLE test_table (id_book INT, id_review INT, date DATE, combined_key TEXT)'))
        connection.execute(text('INSERT INTO test_table (id_book, id_review, date, combined_key) VALUES (1, 1, "2023-07-24", "100001")'))

    csv_data = 'id_book,id_review,date\n1,1,2023-07-24'

    # Mock the pd.read_csv function to return a DataFrame from our string
    with patch('pandas.read_csv', return_value=pd.read_csv(StringIO(csv_data))):
        load_review_into_database('file_path', engine, 'test_table')

    with engine.connect() as connection:
        result = connection.execute(text('SELECT * FROM test_table')).fetchall()

    assert len(result) == 1  # There should still be only one record, as the insert should not have occurred
    assert result[0][0] == 1
    assert result[0][1] == 1
    assert pd.to_datetime(result[0][2]) == pd.to_datetime('2023-07-24')
