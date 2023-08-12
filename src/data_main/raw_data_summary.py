#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: centralized collection of raw data from various sources (NY Times, Amazon and Apple Store).

"""

import os
import sys
from os.path import exists
import json
from sqlalchemy import text

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the project root
root_dir = os.path.join(current_script_dir, '../..')
sys.path.append(root_dir)
from config import NYT_api_key, RAW_DATA_ABS_PATH
# Constructing the absolute path of the src/data_collection directory
src_dir = os.path.join(root_dir, 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
import api_nyt as nyt
import scraping_apple as apple
import scraping_amazon as amazon
import json_tools as jt



def checking_for_a_new_bestseller(nyt_file, engine):
    """
    Checks for new bestsellers that have not yet been scraped from Amazon.

    This function compares the list of bestsellers from a given New York Times file with the list of bestsellers already scraped on Amazon. If there are any new bestsellers, it identifies the maximum ID from the existing database and returns it incremented by one along with the Amazon URL of the first new bestseller.

    Args:
        nyt_file (str): The file containing the New York Times bestseller list.
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.

    Returns:
        tuple: A tuple containing the new ID for the book (int) and the Amazon URL (str) of the first new bestseller to scrape.
    
    """
    # Extract the list of Amazon URLs for the bestsellers from the provided NYT file.
    new_amazon_urls = jt.json_field_to_list(nyt_file, 'amazon_product_url')
    
    # Connect to the database and execute a SQL query to fetch the book IDs and URLs already exists.
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, data->>'url' AS url FROM book;"))
        result = result.fetchall()

        # Identify the maximum book ID in the database.
        max_id = max([id[0] for id in result]) if result else 0

        # Create a list of URLs that have already been scraped.
        urls_already_scraped = [url[1] for url in result]
    
    # Identify any new URLs in the bestseller list that have not yet been scraped.
    url_left_to_scrape = list(set(new_amazon_urls) - set(urls_already_scraped))
    
    print("new id : ", max_id +1,  "\nnew Amazon url to scrape :", url_left_to_scrape[0])

    # Return the incremented maximum ID and the first URL from the list of new bestsellers.
    return max_id + 1, url_left_to_scrape[0]


def data_collection(year, month, day, engine):
    """
    Collects bestseller book data from The New York Times, Amazon, and Apple Store. 

    This function checks if the bestseller list from The New York Times for the given date has already been downloaded. If not, it downloads the list and saves it as a JSON file. It then scrapes book data from Amazon and Apple Store for one book in the bestseller list and save the raw data to a JSON file.

    Args:
        year (int): The year of the bestseller list.
        month (int): The month of the bestseller list.
        day (int): The day of the bestseller list.
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.

    Returns:
        None

    """
    nyt_file = os.path.join(RAW_DATA_ABS_PATH, 'best_sellers_{}_{}_{}.json'.format(year, month, day))

    # Check if the NYT weekly list has already been downloaded
    file_exists = exists(nyt_file)
    
    # New Monday bestseller list stored in a json file
    if not file_exists:
        category_list = nyt.get_nyt_book_categories(NYT_api_key, max_year= year)
        nyt.get_nyt_bestsellers(NYT_api_key, category_list, year=year, month=month, day=day)

    # Check that the bestseller doesn't yet exist in the database
    new_id, amazon_url = checking_for_a_new_bestseller(nyt_file, engine)

    if not amazon_url:
       return  # Exit if there's no Amazon URL, without creating the NYT file or scraping anything else.

    # Scraping Amazon
    amazon_data = amazon.scrape_amazon_books(amazon_url)
    
    # Data NY Times
    with open(nyt_file, 'r', encoding='utf-8') as f:
        nyt_data = json.load(f)

    # Get the item from the list
    selected_item = None
    for item in nyt_data:
        if item['amazon_product_url'] == amazon_url:
            selected_item = item
            break

    # Scraping Apple Store
    apple_url = None
    if selected_item is not None:
        # Scraping Apple Store
        for link in selected_item['buy_links']:
            # If the 'name' field is 'Apple Books', print the URL and break the loop
            if link['name'] == 'Apple Books':
                apple_url = link['url']
                break
    
    genre = apple.scrape_apple_store_book(apple_url) if apple_url is not None else None

    # Save the raw data to a JSON file
    raw_data = {
        "new_id": new_id,
        "nyt_data": selected_item,
        "amazon_data": amazon_data,
        "apple_data": genre
    }

    with open(RAW_DATA_ABS_PATH + "raw_data.json", "w", encoding='utf-8') as outfile:
        json.dump(raw_data, outfile)
    
