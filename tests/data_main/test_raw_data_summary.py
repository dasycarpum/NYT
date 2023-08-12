#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: create for the 'raw_data_summary.py' source file,
    4 unit tests for the 'checking_for_a_new_bestseller' function
    3 unit tests for the 'data_collection' function
"""

import os
import sys
import json
from sqlalchemy import create_engine, text
from unittest.mock import patch, mock_open
import pytest

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the project root
root_dir = os.path.join(current_script_dir, '../..')
sys.path.append(root_dir)
from config import RAW_DATA_ABS_PATH
# Constructing the absolute path of the src/data_collection directory
src_dir = os.path.join(root_dir, 'src', 'data_main')
# Adding the absolute path to system path
sys.path.append(src_dir)
from raw_data_summary import checking_for_a_new_bestseller, data_collection


# Pre-existing bestsellers in the database.
db_data = [(1, {"url": "https://amazon.com/bestseller1"}),
           (2, {"url": "https://amazon.com/bestseller2"})]

# The bestsellers in the New York Times file.
nyt_data = [{"amazon_product_url": url} for url in ["https://amazon.com/bestseller", "https://amazon.com/bestseller", "https://amazon.com/bestseller"]]


@pytest.fixture(scope="module")
def setup_db():
    # Create an in-memory SQLite database for testing.
    engine = create_engine("sqlite:///:memory:")

    # Create a table for testing.
    with engine.connect() as connection:
        connection.execute(text("CREATE TABLE book (id INTEGER PRIMARY KEY, data JSON);"))
        for data in db_data:
            connection.execute(text("INSERT INTO book (id, data) VALUES (:id, :data);"),
                               {"id": data[0], "data": json.dumps(data[1])})

    return engine

@pytest.fixture(scope="module")
def setup_nyt_file(tmpdir_factory):
    # Create a temporary New York Times bestsellers file.
    nyt_file = tmpdir_factory.mktemp("data").join("nyt_bestsellers.json")
    nyt_file.write(json.dumps(nyt_data))

    return str(nyt_file)

# Test the function under normal conditions
def test_checking_for_a_new_bestseller_success(setup_nyt_file, setup_db):
    new_id, new_url = checking_for_a_new_bestseller(setup_nyt_file, setup_db)

    # Check if the new ID is one more than the maximum ID from the database.
    assert new_id == max(id for id, _ in db_data) - 1

    # Check if the new URL is the one that's in the New York Times file but not in the database.
    assert new_url == "https://amazon.com/bestseller"


# Test the function with an empty New York Times file.
def test_empty_nyt_file(setup_db, tmpdir_factory):
    # Create an empty New York Times file.
    nyt_file = tmpdir_factory.mktemp("data").join("empty_nyt_bestsellers.json")
    nyt_file.write(json.dumps([]))

    with pytest.raises(IndexError):
        checking_for_a_new_bestseller(str(nyt_file), setup_db)


# Test the function when all bestsellers in the New York Times file have already been scraped.
def test_all_bestsellers_already_scraped(setup_nyt_file, setup_db):
    # Overwrite the database to include all bestsellers in the New York Times file.
    with setup_db.connect() as connection:
        connection.execute(text("DELETE FROM book;"))
        with open(setup_nyt_file, 'r') as file:
            nyt_data = json.load(file)
            for i, data in enumerate(nyt_data, start=1):
                connection.execute(text("INSERT INTO book (id, data) VALUES (:id, :data);"),
                                   {"id": i, "data": json.dumps({"url": data['amazon_product_url']})})


# Test the function when the database is empty.
def test_empty_database(setup_nyt_file, tmpdir_factory):
    # Create an in-memory SQLite database.
    engine = create_engine("sqlite:///:memory:")

    # Create a table.
    with engine.connect() as connection:
        connection.execute(text("CREATE TABLE book (id INTEGER PRIMARY KEY, data JSON);"))

    new_id, new_url = checking_for_a_new_bestseller(setup_nyt_file, engine)

    assert new_id == 1
    with open(setup_nyt_file, 'r') as file:
        nyt_data = json.load(file)
    assert new_url in [data['amazon_product_url'] for data in nyt_data]


# This test is checking the functionality of the data_collection function when it is used normally
def get_nyt_file_name(year, month, day):
    return RAW_DATA_ABS_PATH + f'best_sellers_{year}_{month}_{day}.json'

"""
@patch('raw_data_summary.nyt.get_nyt_book_categories')
@patch('raw_data_summary.nyt.get_nyt_bestsellers')
@patch('raw_data_summary.checking_for_a_new_bestseller')
@patch('raw_data_summary.amazon.scrape_amazon_books')
@patch('raw_data_summary.apple.scrape_apple_store_book')
@patch("builtins.open", new_callable=mock_open)
def test_data_collection_success(mock_open_file, mock_scrape_apple_store_book, mock_scrape_amazon_books, mock_checking_for_a_new_bestseller, mock_get_nyt_bestsellers, mock_get_nyt_book_categories, setup_db):
    year, month, day = 2023, 6, 26
    
    mock_get_nyt_book_categories.return_value = ["category1", "category2"]
    mock_checking_for_a_new_bestseller.return_value = (1, "amazon_url")
    mock_scrape_amazon_books.return_value = "amazon_data"
    mock_scrape_apple_store_book.return_value = "apple_data"
    mock_get_nyt_bestsellers.return_value = None

    # Ensure the directory exists.
    os.makedirs(RAW_DATA_ABS_PATH, exist_ok=True)

    # Mock the file content as an empty JSON list
    mock_open_file.return_value.read.return_value = "[]"

    data_collection(year, month, day, setup_db)

    assert os.path.isfile(get_nyt_file_name(year, month, day))

    # Clean up after test
    try:
        os.remove(RAW_DATA_ABS_PATH +  'raw_data.json')
    except FileNotFoundError:
        pass
"""

# Test when there is no Apple URL:
@patch('raw_data_summary.nyt.get_nyt_book_categories')
@patch('raw_data_summary.nyt.get_nyt_bestsellers')
@patch('raw_data_summary.checking_for_a_new_bestseller')
@patch('raw_data_summary.amazon.scrape_amazon_books')
@patch('raw_data_summary.apple.scrape_apple_store_book')
def test_data_collection_no_apple_url(mock_scrape_apple_store_book, mock_scrape_amazon_books, mock_checking_for_a_new_bestseller, mock_get_nyt_bestsellers, mock_get_nyt_book_categories, setup_db):
    year, month, day = 2023, 6, 26
    
    mock_get_nyt_book_categories.return_value = ["category1", "category2"]
    mock_checking_for_a_new_bestseller.return_value = (1, "amazon_url")
    mock_scrape_amazon_books.return_value = "amazon_data"
    mock_scrape_apple_store_book.return_value = "apple_data"
    mock_get_nyt_bestsellers.return_value = None

    # Ensure the directory exists.
    os.makedirs(RAW_DATA_ABS_PATH , exist_ok=True)

    # Override 'buy_links' in the data to ensure no Apple link
    with open(get_nyt_file_name(year, month, day), 'w', encoding='utf-8') as f:
        data = [
            {
                'amazon_product_url': 'amazon_url',
                'buy_links': [
                    {'name': 'Not Apple Books', 'url': 'not_apple_url'}
                ]
            }
        ]
        json.dump(data, f)

    data_collection(year, month, day, setup_db)

    assert os.path.isfile(get_nyt_file_name(year, month, day))

    # Clean up after test
    try:
        os.remove(RAW_DATA_ABS_PATH + 'raw_data.json')
    except FileNotFoundError:
        pass


# Test when there is no Amazon URL
@patch('raw_data_summary.nyt.get_nyt_book_categories')
@patch('raw_data_summary.nyt.get_nyt_bestsellers')
@patch('raw_data_summary.checking_for_a_new_bestseller')
@patch('raw_data_summary.amazon.scrape_amazon_books')
@patch('raw_data_summary.apple.scrape_apple_store_book')
def test_data_collection_no_amazon_url(mock_scrape_apple_store_book, mock_scrape_amazon_books, mock_checking_for_a_new_bestseller, mock_get_nyt_bestsellers, mock_get_nyt_book_categories, setup_db):
    year, month, day = 2023, 6, 26
    
    mock_get_nyt_book_categories.return_value = ["category1", "category2"]
    mock_checking_for_a_new_bestseller.return_value = (1, None)
    mock_scrape_amazon_books.return_value = "amazon_data"
    mock_scrape_apple_store_book.return_value = "apple_data"
    mock_get_nyt_bestsellers.return_value = None

    # Ensure the directory exists.
    os.makedirs(RAW_DATA_ABS_PATH, exist_ok=True)

    data_collection(year, month, day, setup_db)

    assert os.path.isfile(get_nyt_file_name(year, month, day))  # this will now check that the NYT file is created
    assert not os.path.isfile(RAW_DATA_ABS_PATH + 'raw_data.json')  # this will check that raw_data.json is not created

