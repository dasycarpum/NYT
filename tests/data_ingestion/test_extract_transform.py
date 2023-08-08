#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-24

@author: Roland

@abstract: create for the 'extract_transform.py' source file,
    5 unit tests for the 'convert_to_date' function,
    2 unit tests for the 'create_a_book_table_item' function,
    3 unit tests for the 'create_a_rank_table_item' function,
    2 unit tests for the 'create_of_review_table_items' function.

"""

import os
import sys
import pytest

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'data_ingestion')
# Adding the absolute path to system path
sys.path.append(src_dir)
from extract_transform import convert_to_date, create_a_book_table_item, create_a_rank_table_item, create_of_review_table_items



# This test verifies the normal operation of the convert_to_date function with valid input.
def test_convert_to_date_success():
    assert convert_to_date('The event will happen on July 24, 2023') == '2023-07-24'
    assert convert_to_date('The test is on December 1, 2023') == '2023-12-01'

# This test checks how the convert_to_date function handles date strings that are not in the expected '%B %d, %Y' format.
def test_wrong_date_format():
    with pytest.raises(ValueError):
        convert_to_date('The event will happen on 24 July, 2023')

# This test verifies how the convert_to_date function handles text that doesn't include the substring 'on' before the date string.
def test_missing_on_substring():
    with pytest.raises(AttributeError):
        convert_to_date('The event will happen July 24, 2023')

# This test checks how the function deals with inputs that are not strings, such as None or an integer.   
def test_non_string_input():
    with pytest.raises(TypeError):
        convert_to_date(None)
    with pytest.raises(TypeError):
        convert_to_date(1234)

# This test verifies the function's behavior when the input text is empty.      
def test_empty_input():
    with pytest.raises(AttributeError):
        convert_to_date('')


# Test the function under normal conditions and expects it to return the correct book dictionary. 
def test_create_a_book_table_item_success():
    new_id = 1
    nyt_data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'isbns': [{'isbn10': '1234567890', 'isbn13': '1234567890123'}],
        'book_uri': 'test_uri',
        'contributor': 'Test Contributor',
        'description': 'Test Description',
        'publisher': 'Test Publisher',
        'price': 'Test Price',
        'dagger': 'Test Dagger',
        'asterisk': 'Test Asterisk',
    }
    amazon_data = [{
        'url': 'test_url',
        'price': 'Test Amazon Price',
        'rating': 'Test Rating',
        'number_of_stars': 5,
        'number_of_pages': 350,
        'language': 'English',
        'publication_date': '2023-01-01',
        'reviews_count': 1000,
    }]
    apple_data = ['Test Genre']

    expected_book = {
        'id': new_id,
        'url': 'test_url',
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn10': ['1234567890'],
        'isbn13': ['1234567890123'],
        'book_uri': ['test_uri'],
        'contributor': 'Test Contributor',
        'description': ['Test Description'],
        'publisher': 'Test Publisher',
        'price': ['Test Price', 'Test Amazon Price'],
        'dagger': 'Test Dagger',
        'asterisk': ['Test Asterisk'],
        'genre': apple_data,
        'rating': 'Test Rating',
        'number_of_stars': 5,
        'number_of_pages': 350,
        'language': 'English',
        'publication_date': '2023-01-01',
        'reviews_count': 1000,
    }

    book = create_a_book_table_item(new_id, nyt_data, amazon_data, apple_data)

    assert book == expected_book


#  Test the function's behavior when a required key is missing from the input data and expects it to raise a KeyError. 
def test_create_a_book_table_item_missing_key():
    new_id = 1
    nyt_data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'isbns': [{'isbn10': '1234567890', 'isbn13': '1234567890123'}],
        # missing 'book_uri'
    }
    amazon_data = [{
        'url': 'test_url',
        'price': 'Test Amazon Price',
        'rating': 'Test Rating',
        'number_of_stars': 5,
        'number_of_pages': 350,
        'language': 'English',
        'publication_date': '2023-01-01',
        'reviews_count': 1000,
    }]
    apple_data = ['Test Genre']

    with pytest.raises(KeyError):
        create_a_book_table_item(new_id, nyt_data, amazon_data, apple_data)


# The test is a simple test with correct data to ensure that the function works as expected.
def test_create_a_rank_table_item_success():
    new_id = 1
    nyt_data = {
        'bestsellers_date': '2023-07-17',
        'category': 'Fiction',
        'rank': 1,
        'rank_last_week': 2,
        'weeks_on_list': 12
    }

    result = create_a_rank_table_item(new_id, nyt_data)
    expected = [1, '2023-07-17', 'Fiction', 1, 2, 12]

    assert result == expected, f'Expected {expected}, but got {result}'


# The test is to test that the function throws a KeyError if there's a missing key in nyt_data.
def test_create_a_rank_table_item_with_missing_key():
    new_id = 1
    nyt_data = {
        'bestsellers_date': '2023-07-17',
        'rank': 1,
        'rank_last_week': 2,
        'weeks_on_list': 12
    }

    with pytest.raises(KeyError):
        create_a_rank_table_item(new_id, nyt_data)


# The test is to test that the function throws a TypeError when the wrong type of data is provided.
def test_create_a_rank_table_item_with_wrong_data_type():
    new_id = 1
    nyt_data = {
        'bestsellers_date': '2023-07-17',
        'category': 'Fiction',
        'rank': '1',
        'rank_last_week': 2,
        'weeks_on_list': 12
    }

    with pytest.raises(TypeError):
        create_a_rank_table_item(new_id, nyt_data)

# The test is a simple test with correct data to ensure that the function works as expected.
def test_create_of_review_table_items_success():
    amazon_data = [
        {
            'reviews': [
                {'stars': 5, 'title': 'Great book', 'text': 'I loved it!', 'date': 'The test is on December 1, 2023'},
                {'stars': 3, 'title': 'Good book', 'text': 'It was ok.', 'date': 'The test is on December 2, 2023'}
            ]
        }
    ]

    expected_output = [
        [1, 1, 5, 'Great book', 'I loved it!', '2023-12-01'],
        [1, 2, 3, 'Good book', 'It was ok.', '2023-12-02']
    ]

    assert create_of_review_table_items(1, amazon_data) == expected_output


# And here's how to test the function in the absence of data
def test_create_of_review_table_items_no_data():
    amazon_data = []

    expected_output = []

    assert create_of_review_table_items(1, amazon_data) == expected_output
