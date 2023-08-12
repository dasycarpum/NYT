#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-19

@author: Roland

@abstract: The objective is to extract from the Apple Store the genre of each NYT bestseller. 

"""

import time
import csv
import requests
from bs4 import BeautifulSoup as bs

from src.data_collection.json_tools import json_field_to_list



def scrape_apple_store_book(apple_url):
    """
    From the url of the book sold on the Apple store, the function will 
    scrape the main page to return the genre of the book

    Args:
        url (str): the URL of a book sold on Apple store.

    Returns:
        str: the genre of the book.
        
    """
    response = requests.get(apple_url, timeout=5)

    if response.status_code != 200:
        raise requests.exceptions.RequestException(f"Unable to get page {apple_url}, status code: {response.status_code}")

    time.sleep(2.1)

    soup = bs(response.text,'html.parser')
    badge = soup.find('div', attrs={'class':'book-badge__caption'})

    if badge is None:
        return 'undetermined'
    else:
        return badge.string.strip()


def scrape_apple_store_books(apple_store_books_csv, best_sellers_json):
    """
    Function to read the existing genres from a CSV file, scrape new genres from Apple Books URLs found in a JSON file, and save all genres into another CSV file.

    Args:
        apple_store_books_csv (str): The path to the CSV file where all genres will be saved.
        best_sellers_json (str): The path to the JSON file with best seller books and their Apple Books URLs.

    Returns:
        None
        
    """
    # Read the existing csv file to find out what's already been scraped
    existing_genres = {}
    try:
        with open(apple_store_books_csv, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                existing_genres[row[0]] = row[1]
    except FileNotFoundError:
        pass  # If file doesn't exist yet, it's fine

    # Load urls
    urls = json_field_to_list(best_sellers_json, 'buy_links', 'Apple Books')

    # Scrape new genres
    new_genres = {}
    for url in urls:
        if url not in existing_genres:
            try:
                new_genres[url] = scrape_apple_store_book(url)
            except requests.exceptions.RequestException as e:
                print("Apple couldn't find the page :", e)
                continue

    # Combine old and new genres
    all_genres = {**existing_genres, **new_genres}

    # Write them all out to the genres.csv
    with open(apple_store_books_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['url', 'genre'])
        for url, genre in all_genres.items():
            writer.writerow([url, genre])


