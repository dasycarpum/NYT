#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-18

@author: Roland

@abstract: the Books API provides information about The New York Times Best Sellers lists. https://developer.nytimes.com/docs/books-product/1/overview

"""

import time
from datetime import datetime
import json
import pandas as pd
import requests
from pynytimes import NYTAPI

# import api_request
from src.data_collection.api_request import api_request


def get_nyt_book_categories(api_key, max_year=2022):
    """
    Retrieves a list of weekly updated New York Times book categories published within a specified date range.  This function queries the New York Times Books API to get a list of all book categories. 
    It filters this list to include only those categories that are updated on a weekly basis and have been published between the start of 2013 and the end of 2022 (or max year choice).

    Args:
        api_key (str): The API key for the New York Times Books API.
        year (int) : the maximum year of the best-seller collection period

    Returns:
        list(str): A list of weekly updated book category names published 

    Example:
        >>> api_key = 'your-api-key'
        >>> get_nyt_book_categories(api_key)
        ['Hardcover Fiction', 'Paperback Nonfiction', 'Children’s Middle Grade', ...]

    Raises:
        ValueError: If the API key is not valid.
        Exception: If there is any issue with the API request.
    """

    # 1) Choice of the bestseller collection period
    start = 2014
    stop = max_year-1

    # 2) Choose the categories of books to retrieve, i.e. those with a weekly update and that have been available for the period.
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    
    try:
        df = api_request(endpoint, api_key)
    except requests.exceptions.ReadTimeout:
        raise Exception("API request failed due to a timeout.")
    
    if df is None:
        raise Exception("API request returned no data.")

    # Convert dates to datetime and extract the year
    df['oldest_published_date'] = pd.to_datetime(df['oldest_published_date']).dt.year
    df['newest_published_date'] = pd.to_datetime(df['newest_published_date']).dt.year

    df = df.loc[(df['updated'] == 'WEEKLY') & 
                (df['oldest_published_date'] < start) & 
                (df['newest_published_date'] >= stop)]

    category_list = df['list_name'].tolist()
    
    return category_list


# 3) Collecting information on the New York Times bestseller lists.
def fetch_bestsellers(nyt, cat, date):
    """
    Fetches the list of bestseller books from New York Times API for a specific category and date.

    Args:
        nyt (pynytimes.NYTAPI): The pynytimes API client instance.
        cat (str): The category for which to fetch the bestsellers.
        date (datetime): The date for which to fetch the bestsellers.

    Returns:
        list: A list of dictionaries. Each dictionary contains information about a book. If an exception occurs during the request, an empty list is returned.

    Raises:
        TypeError: If improper arguments are provided to nyt.best_sellers_list().
        Exception: If any other exception occurs during the execution.
    """
    try:
        books = nyt.best_sellers_list(name=cat, date=date)
    except TypeError as te:
        print(f"TypeError occurred: {te}")
        books = []
    except Exception as e:
        print(f"Error occurred: {e}")
        books = []

    return books


def process_books(books, cat, monday):
    """
    Processes the list of books obtained from the New York Times API by adding 
    'category' and 'bestsellers_date' fields to each book dictionary.

    Args:
        books (list): A list of dictionaries, each containing information about a book.
        cat (str): The category for which the books were fetched.
        monday (str): The date (Monday) for which the books were fetched.

    Returns:
        list: The processed list of book dictionaries with additional 'category' and 'bestsellers_date' fields.

    Note:
        The function modifies the input books list directly and returns the modified list.
    """
    for i, b in enumerate(books):
        books[i]["category"] = cat
        books[i]["bestsellers_date"] = monday

    return books


def sleep():
    """
    Pauses the execution of the program for 3.1 seconds.

    Note:
        This function is used to prevent rapid, successive calls to an external API, ensuring the program adheres to the API's rate limits.
    """
    time.sleep(3.1)


def save_as_json(data, year, month, day):
    """
    Saves a given data object as a JSON file. The filename is generated using the provided year, month, and day values. The JSON file is stored in the 'data/raw_data' directory.

    Args:
        data (list or dict): The data to be saved as a JSON file. This should be a list or dictionary.
        year (int): The year to be included in the filename.
        month (int): The month to be included in the filename.
        day (int): The day to be included in the filename.

    Raises:
        FileNotFoundError: If the specified file path does not exist.
        TypeError: If the provided data object is not serializable.
    """
    try:
        with open('data/raw_data/best_sellers_{}_{}_{}.json'.format(year, month, day), 'w', encoding='utf-8') as jsonfile: 
            json.dump(data, jsonfile)
    except FileNotFoundError:
        print("Error: File not found.")
        raise
    except TypeError:
        print("Error: Object is not JSON serializable.")
        raise


def get_nyt_bestsellers(api_key, categories, year=2022, month=None, day=None):
    """
    Retrieves the New York Times bestsellers for a given year, month, and day for each provided category, and saves the data as a JSON file.

    This function queries the New York Times Books API to get the bestsellers for each Monday of the provided year, month, and day for each category in the given list. It then saves the data to a JSON file.

    Args:
        api_key (str): The API key for the New York Times Books API.
        categories (list): A list of book categories to query.
        year (int, optional): The year to query. Defaults to 2022.
        month (int, optional): The month to query. If None, queries all months of the year. Defaults to None.
        day (int, optional): The day to query. If None, queries all days of the month. Defaults to None.

    Returns:
        None

    Example:
        >>> api_key = 'your-api-key'
        >>> categories = ['Hardcover Fiction', 'Paperback Nonfiction', 'Children’s Middle Grade']
        >>> get_nyt_bestsellers(api_key, categories, year=2023, month=5, day=24)

    Raises:
        ValueError: If the API key is not valid.
        TypeError: If the arguments 'name' and 'date' are not correctly provided to the 'nyt.best_sellers_list' function.
        Exception: If there is any issue with the API request or saving the data.
    """
    nyt = NYTAPI(api_key, parse_dates=False)
    
    books_of_the_period = []
    period = range(year, year+1)

    for year in period:
        books_of_a_year = []
        if month is None:
            dates = pd.date_range(start=str(year), end=str(year+1), freq='W-MON').strftime('%Y-%m-%d').tolist()
        elif day is None:
            dates = pd.date_range(start=f"{year}-{month}-01", end=f"{year}-{month+1}-01", freq='W-MON').strftime('%Y-%m-%d').tolist()
        else:
            dates = [f"{year}-{month}-{day}"]
        
        for monday in dates:       
            books_of_the_week= []
            for cat in categories:
                books = fetch_bestsellers(nyt, cat, datetime.strptime(monday, '%Y-%m-%d'))
                processed_books = process_books(books, cat, monday)
                books_of_the_week.append(processed_books) 
            books_of_a_year.append(books_of_the_week)
            
            sleep()
            print('date :', monday)

        books_of_the_period.append(books_of_a_year) 

    full_list_of_books = []
    for yearly_list in books_of_the_period:
        for weekly_list in yearly_list:
            for best_sellers_category in weekly_list:
                for book in best_sellers_category:
                    full_list_of_books.append(book)

    save_as_json(full_list_of_books, year, month, day)



