#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-23

@author: Roland

@abstract: create 3 unit tests for the 'scrape_apple_store_book' function in the 'scraping_apple.py' source file, , and 2 unit tests for the 'scrape_apple_store_books' function in the same source file.
"""

import os
import sys
import pytest
import requests
import responses
from unittest import mock

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
from scraping_apple import scrape_apple_store_book, scrape_apple_store_books


# If the book's page contains a 'book-badge__caption' div, the genre of the book is correctly scraped.
def test_scrape_apple_store_book_success():
    url = 'http://fakeapple.com/book1'
    html = """
    <html>
        <body>
            <div class='book-badge__caption'>
                Fiction
            </div>
        </body>
    </html>
    """
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=html, status=200)
        genre = scrape_apple_store_book(url)
    assert genre == 'Fiction', 'Genre is not correctly scraped'


# If the book's page does not contain a 'book-badge__caption' div, the function should return 'undetermined'.
def test_scrape_apple_store_book_failure_no_genre():
    url = 'http://fakeapple.com/book2'
    html = """
    <html>
        <body>
        </body>
    </html>
    """
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=html, status=200)
        genre = scrape_apple_store_book(url)
    assert genre == 'undetermined', 'Genre should be undetermined when badge is missing'


# If the book's page is not accessible (returns a 404 status), the function should raise a requests.exceptions.RequestException.
def test_scrape_apple_store_book_failure_no_page():
    url = 'http://fakeapple.com/book3'
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=404)
        with pytest.raises(requests.exceptions.RequestException):
            scrape_apple_store_book(url)


# Scenario 1 : when the scrape_apple_store_book function works as expected, it asserts that the CSV file is written with the correct content.
@mock.patch("scraping_apple.scrape_apple_store_book")
@mock.patch("csv.reader")
@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("scraping_apple.json_field_to_list", return_value=['http://fakeapple.com/book1', 'http://fakeapple.com/book2'])  
def test_scrape_apple_store_books_success(mock_json_field_to_list, mock_open, mock_csv_reader, mock_scrape_book):
    # Mocking the CSV file content
    mock_csv_reader.return_value = iter([['url', 'genre'], ['http://fakeapple.com/book1', 'Fiction']])
    
    # Mocking the scrape_apple_store_book function
    mock_scrape_book.side_effect = ['Fiction', 'Fiction']
    
    # Call the function under test
    scrape_apple_store_books("dummy_csv_path", "dummy_json_path")
    
    # Assert that the csv.writer function was called with the expected content
    calls = [mock.call.write('url,genre\r\n'), 
             mock.call.write('http://fakeapple.com/book1,Fiction\r\n'),
             mock.call.write('http://fakeapple.com/book2,Fiction\r\n')]
    mock_open.return_value.write.assert_has_calls(calls)


# Scenario 2 : when the scrape_apple_store_book function raises a requests.exceptions.RequestException, it asserts that the URL which raised the exception is skipped.
@mock.patch("scraping_apple.scrape_apple_store_book", side_effect=requests.exceptions.RequestException()) 
@mock.patch("csv.reader")
@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("scraping_apple.json_field_to_list", return_value=['http://fakeapple.com/book1', 'http://fakeapple.com/book2']) 
def test_scrape_apple_store_books_request_exception(mock_json_field_to_list, mock_open, mock_csv_reader, mock_scrape_book):
    # Mocking the CSV file content
    mock_csv_reader.return_value = iter([['url', 'genre'], ['http://fakeapple.com/book1', 'Fiction']])
    
    # Call the function under test
    scrape_apple_store_books("dummy_csv_path", "dummy_json_path")
    
    # Assert that the csv.writer function was called with the expected content
    calls = [mock.call.write('url,genre\r\n'), 
             mock.call.write('http://fakeapple.com/book1,Fiction\r\n')]  # No entry for book2 due to request exception
    mock_open.return_value.write.assert_has_calls(calls)
