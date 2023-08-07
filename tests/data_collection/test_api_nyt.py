#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-22

@author: Roland

@abstract: create 4 unit tests for the 'get_nyt_book_categories' function in the 'api_nyt.py' source file, and 12 unit tests for the 'get_nyt_bestsellers' function (and its sub-functions) in the same source file.
"""

import os
import sys
import pytest
import unittest
from datetime import datetime
import requests
import requests_mock
from unittest.mock import MagicMock, patch, mock_open
from pynytimes import NYTAPI

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the project root
root_dir = os.path.join(current_script_dir, '../..')
sys.path.append(root_dir)
from config import NYT_api_key
# Constructing the absolute path of the src/data_collection directory
src_dir = os.path.join(root_dir, 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
from api_nyt import get_nyt_book_categories, get_nyt_bestsellers, fetch_bestsellers, process_books, save_as_json, sleep



# Check if the function returns the expected categories given a known API response.
def test_get_nyt_book_categories():
    # Mock API key and endpoint
    api_key = "mock-api-key"
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"

    # Mock the API response
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, json={"results": [
            {"list_name": "Hardcover Fiction", "updated": "WEEKLY", "oldest_published_date": "2013-01-01", "newest_published_date": str(datetime.now().date())},
            {"list_name": "Paperback Nonfiction", "updated": "MONTHLY", "oldest_published_date": "2013-01-01", "newest_published_date": str(datetime.now().date())},
            {"list_name": "Children’s Middle Grade", "updated": "WEEKLY", "oldest_published_date": "2013-01-01", "newest_published_date": "2017-12-31"}
        ]})
        
        # Call the function and get the result
        categories = get_nyt_book_categories(api_key, max_year=2022)

    # The expected result
    expected_categories = ['Hardcover Fiction']

    # Check that the returned categories match the expected result
    assert categories == expected_categories


# Check if the function raises a ValueError when an invalid API key is provided.
def test_get_nyt_book_categories_invalid_api_key():
    # Invalid API key
    api_key = "invalid-api-key"
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"

    # Mock the API response with an error message
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, json={"fault": {"faultstring": "Invalid ApiKey", "detail": {"errorcode": "oauth.v2.InvalidApiKey"}}})

        with pytest.raises(Exception, match="API request returned no data."):
            get_nyt_book_categories(api_key)


# Check if the function handles exceptions from the api_request correctly.
def test_get_nyt_book_categories_api_request_exception():
    # Valid API key
    api_key = NYT_api_key
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"

    # Mock the API response to raise a ReadTimeout exception
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, exc=requests.exceptions.ReadTimeout)

        try:
            # Call the function and get the result
            get_nyt_book_categories(api_key)
        except Exception as e:
            assert str(e) == "API request failed due to a timeout."
            return

    assert False, "Expected an Exception to be raised with message 'API request failed due to a timeout.' but it wasn't."


# Check if the function correctly handles the "max_year" parameter.
def test_get_nyt_book_categories_max_year(requests_mock):
    api_key = 'test-api-key'
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"

    # Define the mocked API response
    mock_response = {
        "results": [
            {"updated": "WEEKLY", "oldest_published_date": "2013-01-01", "newest_published_date": "2021-12-31", "list_name": "Paperback Nonfiction"},
            {"updated": "WEEKLY", "oldest_published_date": "2013-01-01", "newest_published_date": "2021-12-31", "list_name": "Children’s Middle Grade"},
            {"updated": "WEEKLY", "oldest_published_date": "2015-01-01", "newest_published_date": "2022-12-31", "list_name": "Hardcover Fiction"}
        ]
    }

    # Mock the API response
    requests_mock.get(endpoint + 'api-key=' + api_key, json=mock_response)
        
    # Call the function
    categories = get_nyt_book_categories(api_key, max_year=2021)

    # Define the expected result
    expected_categories = ['Paperback Nonfiction', 'Children’s Middle Grade']

    # Check the result
    assert set(categories) == set(expected_categories)


# This test is checking the functionality of the fetch_bestsellers function when it is used normally, i.e., when it doesn't encounter any exceptions. 
def test_fetch_bestsellers_success():
    # Create a mock NYTAPI object
    nyt = MagicMock(spec=NYTAPI)

    # Mock the best_sellers_list method to return some example data
    example_books = [{'title': 'Example Book', 'author': 'John Doe'}]
    nyt.best_sellers_list.return_value = example_books

    # Call the function and check that it returns the correct data
    result = fetch_bestsellers(nyt, 'Hardcover Fiction', datetime.strptime('2022-12-31', '%Y-%m-%d'))
    assert result == example_books


# This test is checking that the fetch_bestsellers function handles TypeError
def test_fetch_bestsellers_type_error():
    # Create a mock NYTAPI object
    nyt = MagicMock(spec=NYTAPI)

    # Mock the best_sellers_list method to raise a TypeError
    nyt.best_sellers_list.side_effect = TypeError

    # Call the function and check that it returns an empty list
    result = fetch_bestsellers(nyt, 'Hardcover Fiction', datetime.strptime('2022-12-31', '%Y-%m-%d'))
    assert result == []


# This test is similar to the previous, but it's checking that the fetch_bestsellers function handles other, non-TypeError exceptions correctly. 
def test_fetch_bestsellers_other_exception():
    # Create a mock NYTAPI object
    nyt = MagicMock(spec=NYTAPI)

    # Mock the best_sellers_list method to raise an arbitrary Exception
    nyt.best_sellers_list.side_effect = Exception

    # Call the function and check that it returns an empty list
    result = fetch_bestsellers(nyt, 'Hardcover Fiction', datetime.strptime('2022-12-31', '%Y-%m-%d'))
    assert result == []

# Check that the function correctly handles an empty list of books.
def test_process_books_empty_list():
    # Test case where books list is empty.
    books = []
    cat = "category1"
    monday = "2022-01-01"
    
    result = process_books(books, cat, monday)

    assert result == []

# Verify that the function correctly processes a list containing one book.
def test_process_books_single_book():
    # Test case where books list contains one book.
    books = [{"title": "Test Book", "author": "Test Author"}]
    cat = "category1"
    monday = "2022-01-01"
    
    expected_result = [{
        "title": "Test Book", 
        "author": "Test Author", 
        "category": "category1",
        "bestsellers_date": "2022-01-01"
    }]

    result = process_books(books, cat, monday)

    assert result == expected_result

# Check that the function correctly processes a list containing multiple books.
def test_process_books_multiple_books():
    # Test case where books list contains multiple books.
    books = [
        {"title": "Test Book 1", "author": "Test Author 1"},
        {"title": "Test Book 2", "author": "Test Author 2"},
    ]
    cat = "category1"
    monday = "2022-01-01"
    
    expected_result = [
        {
            "title": "Test Book 1", 
            "author": "Test Author 1", 
            "category": "category1",
            "bestsellers_date": "2022-01-01"
        },
        {
            "title": "Test Book 2", 
            "author": "Test Author 2", 
            "category": "category1",
            "bestsellers_date": "2022-01-01"
        }
    ]

    result = process_books(books, cat, monday)

    assert result == expected_result


class TestSaveAsJson(unittest.TestCase):
    # Test the normal operation of save_as_json, asserting that open and json.dump are called with the expected arguments.
    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_as_json(self, mock_file, mock_json_dump):
        data = {"key": "value"}
        year, month, day = 2023, 7, 17

        save_as_json(data, year, month, day)

        mock_file.assert_called_once_with('data/raw_data/best_sellers_2023_7_17.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with(data, mock_file())

    # Test that a FileNotFoundError is raised when the file path does not exist.
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_save_as_json_file_not_found(self, mock_file):
        data = {"key": "value"}
        year, month, day = 2023, 7, 22

        with self.assertRaises(FileNotFoundError):
            save_as_json(data, year, month, day)

    # Test that a TypeError is raised when the data is not serializable.
    @patch("json.dump", side_effect=TypeError)
    @patch("builtins.open", new_callable=mock_open)
    def test_save_as_json_not_serializable(self, mock_file, mock_json_dump):
        data = {"key": "value"}
        year, month, day = 2023, 7, 22

        with self.assertRaises(TypeError):
            save_as_json(data, year, month, day)
    
if __name__ == "__main__":
    unittest.main()


# This test involves providing valid arguments to the function and checking whether it executes without any errors.
def test_get_nyt_bestsellers_valid_args(mocker):
    # Arrange
    api_key = 'valid_key'
    categories = ['category1', 'category2']
    year = 2022
    month = 1
    day = 1

    mock_fetch = mocker.patch('api_nyt.fetch_bestsellers', return_value=[{'book1': 'details'}, {'book2': 'details'}])
    mock_process = mocker.patch('api_nyt.process_books', return_value=[{'book1': 'details', 'category': 'category1', 'bestsellers_date': '2022-01-01'}, {'book2': 'details', 'category': 'category1', 'bestsellers_date': '2022-01-01'}])
    mock_sleep = mocker.patch('api_nyt.sleep')
    mock_save = mocker.patch('api_nyt.save_as_json')

    # Act
    try:
        get_nyt_bestsellers(api_key, categories, year, month, day)
        # Assert
        assert True  # If it gets here, the function has executed without any errors.
    except Exception as e:
        pytest.fail(f"get_nyt_bestsellers() raised {type(e).__name__} unexpectedly!")

# Provide invalid arguments and ensure that the function handles them gracefully and doesn't crash.
def test_get_nyt_bestsellers_invalid_args(mocker):
    # Arrange
    api_key = 'valid_key'
    categories = ['category1', 'category2']
    year = "invalid_year"  # Provide invalid year

    mock_fetch = mocker.patch('api_nyt.fetch_bestsellers')
    mock_process = mocker.patch('api_nyt.process_books')
    mock_sleep = mocker.patch('api_nyt.sleep')
    mock_save = mocker.patch('api_nyt.save_as_json')

    # Act and Assert
    with pytest.raises(Exception):
        get_nyt_bestsellers(api_key, categories, year)



# We use mocking to control the return values of the smaller functions and ensure that the loops and conditionals in get_nyt_bestsellers() work as expected.
def test_get_nyt_bestsellers_loops_conditionals(mocker):
    # Arrange
    api_key = 'valid_key'
    categories = ['category1', 'category2']
    year = 2022

    mock_fetch = mocker.patch('api_nyt.fetch_bestsellers')
    mock_process = mocker.patch('api_nyt.process_books')
    mock_sleep = mocker.patch('api_nyt.sleep')
    mock_save = mocker.patch('api_nyt.save_as_json')

    mock_fetch.return_value = [{'book1': 'details'}, {'book2': 'details'}]
    mock_process.return_value = [{'book1': 'details', 'category': 'category1', 'bestsellers_date': '2022-01-01'}, 
                                 {'book2': 'details', 'category': 'category1', 'bestsellers_date': '2022-01-01'}]

    # Act
    try:
        get_nyt_bestsellers(api_key, categories, year)
        # Assert
        assert mock_fetch.call_count == 104  # fetch_bestsellers should be called once for each combination of date and category
        assert mock_process.call_count == 104  # process_books should be called once for each combination of date and category
        assert mock_save.called  # save_as_json should be called once at the end
    except Exception as e:
        pytest.fail(f"get_nyt_bestsellers() raised {type(e).__name__} unexpectedly!")
