#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-24

@author: Roland

@abstract: create for the 'scraping_amazon.py' source file,
    2 unit tests for the 'find_customer_reviews_page' function,
    4 unit tests for the 'transform_url_for_specific_page' function,
    4 unit tests for the 'scrape_amazon_books' function.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
from scraping_amazon import find_customer_reviews_page, transform_url_for_specific_page, scrape_amazon_books


class MockActionChains(ActionChains):
    def __init__(self, driver):
        self.driver = driver

    def move_to_element(self, element):
        return self

    def click(self):
        return self

    def perform(self):
        return self


@pytest.fixture
def mock_driver():
    # Mock driver and related methods
    mock_driver = Mock()
    mock_driver.get = MagicMock()
    mock_driver.execute_script = MagicMock()
    mock_driver.find_element = MagicMock()

    # Mock WebDriverWait and related methods
    WebDriverWait(mock_driver, 10).until = MagicMock()

    # Mock ActionChains
    ActionChains.__init__ = MockActionChains.__init__
    ActionChains.move_to_element = MockActionChains.move_to_element
    ActionChains.click = MockActionChains.click
    ActionChains.perform = MockActionChains.perform

    return mock_driver

# The test verifies that the find_customer_reviews_page function correctly navigates to a product's 'All Customer Reviews' page on Amazon and returns the correct URL when provided with a valid product URL and a functional web driver.
def test_find_customer_reviews_page_success(mock_driver):
    # Test success case
    mock_driver.find_element.return_value.get_attribute.return_value = 'https://amazon.com/reviews'
    mock_driver.current_url = 'https://amazon.com/product'

    assert find_customer_reviews_page('https://amazon.com/product', mock_driver) == 'https://amazon.com/reviews'

    assert mock_driver.get.call_count == 2
    mock_driver.execute_script.assert_called_once()
    assert mock_driver.find_element.call_count == 2


#  Instead of asserting on the error message, we can assert that an exception is raised when the "See all reviews" button cannot be found.
def test_find_customer_reviews_page_failure(mock_driver):
    # Test failure case
    mock_driver.find_element.side_effect = Exception('Cannot find element')

    with pytest.raises(Exception):
        find_customer_reviews_page('https://amazon.com/product', mock_driver)


# In these tests, we are validating that the transform_url_for_specific_page function is correctly transforming the URLs for different pages of reviews. The tests check various scenarios : wWhen the page number is 2 or 3, and when the "cm_cr_dp_d_show_all_btm" string is not present in the URL.
def test_transform_url_for_specific_page():
    # Test with page number 2
    url = "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_dp_d_show_all_btm"
    assert transform_url_for_specific_page(url, 2) == "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_arp_d_paging_btm_next_2&pageNumber=2"

    # Test with page number 3
    assert transform_url_for_specific_page(url, 3) == "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_arp_d_paging_btm_next_3&pageNumber=3"

    # Test with no "cm_cr_dp_d_show_all_btm" in the URL
    url = "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20"
    assert transform_url_for_specific_page(url, 2) == "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&pageNumber=2"

@pytest.mark.parametrize("url,page,expected", [
    ("https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_dp_d_show_all_btm", 2, "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_arp_d_paging_btm_next_2&pageNumber=2"),
    ("https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_dp_d_show_all_btm", 3, "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&cm_cr_arp_d_paging_btm_next_3&pageNumber=3"),
    ("https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20", 2, "https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20&pageNumber=2")
])
def test_transform_url_for_specific_page_parametrized(url, page, expected):
    assert transform_url_for_specific_page(url, page) == expected

# This test checks the functionality of the scrape_amazon_books function when a NoSuchElementException is encountered during execution.
@patch('scraping_amazon.webdriver.Remote')
def test_scrape_amazon_books_no_such_element(mock_firefox):
    # Mock the `scrape_amazon_book` function to raise NoSuchElementException
    with patch('scraping_amazon.scrape_amazon_book', side_effect=NoSuchElementException):
        with pytest.raises(NoSuchElementException):
            scrape_amazon_books("http://some-url.com")
        mock_firefox.return_value.quit.assert_called_once()

#  This test is similar to the previous one, but instead checks for a WebDriverException.
@patch('scraping_amazon.webdriver.Remote')
def test_scrape_amazon_books_web_driver_exception(mock_firefox):
    # Mock the `scrape_amazon_book` function to raise WebDriverException
    with patch('scraping_amazon.scrape_amazon_book', side_effect=WebDriverException):
        with pytest.raises(WebDriverException):
            scrape_amazon_books("http://some-url.com")
        mock_firefox.return_value.quit.assert_called_once()

# This test checks the functionality of the scrape_amazon_books function when it encounters an AttributeError.
@patch('scraping_amazon.webdriver.Remote')
def test_scrape_amazon_books_attribute_error(mock_firefox):
    # Mock the `scrape_amazon_book` function to raise AttributeError
    with patch('scraping_amazon.scrape_amazon_book', side_effect=AttributeError):
        with pytest.raises(AttributeError):
            scrape_amazon_books("http://some-url.com")
        mock_firefox.return_value.quit.assert_called_once()

# This test is checking the functionality of the scrape_amazon_books function when it encounters an unexpected or general Exception.
@patch('scraping_amazon.webdriver.Remote')
def test_scrape_amazon_books_general_exception(mock_firefox):
    # Mock the `scrape_amazon_book` function to raise a general Exception
    with patch('scraping_amazon.scrape_amazon_book', side_effect=Exception):
        with pytest.raises(Exception):
            scrape_amazon_books("http://some-url.com")
        mock_firefox.return_value.quit.assert_called_once()

