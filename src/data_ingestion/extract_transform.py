#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-22

@author: Roland

@abstract: from the raw data provided by the API and scraping, the functions extract and build the structure of the 3 relational tables that will be stored in the database (book, rank and review). Some functions process entire tables, while others transform single items.

"""

import re
from datetime import datetime
import json
import csv
from collections import defaultdict



def combine_book_data(best_sellers_json, merged_amazon_books_json, apple_store_books_csv, output_json):
    """
    Function to combine book data from JSON and CSV files, and save the combined data into a JSON file.

    Args:
        best_sellers_json (str): The path to the JSON file with best seller books data.
        merged_amazon_books_json (str): The path to the JSON file with merged Amazon books data.
        apple_store_books_csv (str): The path to the CSV file with Apple Store books data.
        output_json (str): The path to the JSON file where the combined data will be saved.

    Returns: 
        None

    """

    # Read and parse the best_sellers.json file
    with open(best_sellers_json, "r", encoding='utf-8') as f:
        book_data = json.load(f)

    # Read and parse the merged_Amazon_books.json file
    with open(merged_amazon_books_json, "r",encoding='utf-8') as f:
        amazon_data = json.load(f)

    # Read and parse the apple_store_books.csv file
    apple_data = {}
    with open(apple_store_books_csv, "r", encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            apple_data[row[0]] = row[1]

    # Combine the data
    combined_data = defaultdict(dict)
    id_counter = 1 

    for book in book_data:
        amazon_url = book["amazon_product_url"]
        if amazon_url is None:
            continue
        
        if amazon_url not in combined_data:
            combined_data[amazon_url] = {
                "id": id_counter,
                "url": amazon_url,
                "title": book["title"],
                "author": book["author"],
                "isbn10": set(),
                "isbn13": set(),
                "book_uri": set(),
                "contributor": book["contributor"],
                "description": set(),
                "publisher": book["publisher"],
                "price": set(),
                "dagger": book["dagger"],
                "asterisk": set(),
                "genre": ""
            }
            id_counter += 1

        for isbn in book["isbns"]:
            combined_data[amazon_url]["isbn10"].add(isbn["isbn10"])
            combined_data[amazon_url]["isbn13"].add(isbn["isbn13"])

        combined_data[amazon_url]["book_uri"].add(book["book_uri"])
        combined_data[amazon_url]["description"].add(book["description"])
        combined_data[amazon_url]["price"].add(book["price"])
        combined_data[amazon_url]["asterisk"].add(book["asterisk"])

        apple_url = next((link["url"] for link in book["buy_links"] if link["name"] == "Apple Books"), None)
        if apple_url in apple_data:
            combined_data[amazon_url]["genre"] = apple_data[apple_url]

    for item in amazon_data:
        amazon_url = item["url"]
        if amazon_url in combined_data:
            combined_data[amazon_url].update({
                "id": combined_data[amazon_url]["id"], 
                "rating": item["rating"],
                "number_of_stars": item["number_of_stars"],
                "price": combined_data[amazon_url]["price"].union({item.get("price", None)}),
                "number_of_pages": item.get("number_of_pages", None),
                "language": item.get("language", None),
                "publication_date": item.get("publication_date", None),
                "reviews_count": item["reviews_count"],
                "random_pages_count": item["random_pages_count"]
            })

    # Convert sets to lists
    for amazon_url in combined_data:
        for key in ["isbn10", "isbn13", "book_uri", "description", "price", "asterisk"]:
            combined_data[amazon_url][key] = list(combined_data[amazon_url][key])

    # Save combined_data to a JSON file
    with open(output_json, "w", encoding='utf-8') as f:
        json.dump(list(combined_data.values()), f, ensure_ascii=False, indent=4)


def write_rank(best_sellers_json, book_json, rank_csv):
    """
    Function to read book data from JSON files, combine the data, and save the combined data into a CSV file.

    Args:
        best_sellers_json (str): The path to the JSON file with best seller books data.
        book_json (str): The path to the JSON file with book identifiers.
        rank_csv (str): The path to the CSV file where the combined data will be saved.

    Returns:
        None

    """
    # Read and parse the best_sellers.json file
    with open(best_sellers_json, "r", encoding='utf-8') as f:
        data = json.load(f)

    # Read and parse the book.json file
    with open(book_json, "r", encoding='utf-8') as f:
        data_id = json.load(f)

    # Write the CSV file
    with open(rank_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header
        header = ['id_book', 'date', 'category', 'rank', 'rank_last_week', 'weeks_on_list']
        writer.writerow(header)

        # Write the data
        url_to_id = {i['url']: i["id"] for i in data_id}

        # Create an empty set to store written rows
        written_rows = set()
        
        for item in data:
            target_url = item['amazon_product_url']
            if target_url is None:
                continue
            
            # Create the row
            row = [url_to_id.get(target_url),
                   item['bestsellers_date'],
                   item['category'],
                   item['rank'],
                   item['rank_last_week'],
                   item['weeks_on_list']]
            
            # Convert the row to a tuple so it can be stored in the set
            row_tuple = tuple(row)
            
            # If the row has not been written yet, write it and add it to the set
            if row_tuple not in written_rows:
                writer.writerow(row)
                written_rows.add(row_tuple)


def convert_to_date(text):
    """
    Converts a given date string within a text into a specific format ('%Y-%m-%d').

    This function expects the date in the text to be in the format '%B %d, %Y' (e.g., 'July 12, 2023') and comes after the substring 'on '. The function uses regex to extract the date string and converts it into the '%Y-%m-%d' format.

    Args:
        text (str): The text containing the date string to be converted.

    Returns:
        str: The converted date string in '%Y-%m-%d' format.

    Raises:
        AttributeError: If the pattern 'on ' followed by a date string in the format '%B %d, %Y' 
        is not found in the input text.
        
    Examples:
        >>> convert_to_date('The event will happen on July 12, 2023')
        '2023-07-12'

    """
    # Extract the date string using regex
    date_str = re.search(r'(?<=on\s).+', text).group()
    
    # Parse the date string and convert it to the desired format
    date = datetime.strptime(date_str, '%B %d, %Y')
    
    return date.strftime('%Y-%m-%d')


def write_reviews(merged_amazon_books_json, book_json, review_csv):
    """
    Function to read book review data from JSON files, combine the data, and save the combined data into a CSV file.

    Args:
        merged_amazon_books_json (str): The path to the JSON file with merged Amazon books data.
        book_json (str): The path to the JSON file with book identifiers.
        review_csv (str): The path to the CSV file where the combined data will be saved.

    Returns:
        None

    """
    # Read and parse the merged_amazon_books.json file, with the review data
    with open(merged_amazon_books_json, "r", encoding='utf-8') as f:
        data = json.load(f)

    # Read and parse the book.json file, with the book identifier
    with open(book_json, "r", encoding='utf-8') as f:
        data_id = json.load(f)

    # Write the CSV file
    with open(review_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header
        header = ['id_book', 'id_review', 'stars', 'title', 'text', 'date']
        writer.writerow(header)

        # Write the data
        url_to_id = {j["url"]: j["id"] for j in data_id}
        for item in data:
            target_url = item['url']
            for index, review in enumerate(item['reviews']):
                writer.writerow([url_to_id.get(target_url),
                                  index + 1,
                                  review['stars'],
                                  review['title'],
                                  review['text'],
                                  convert_to_date(review['date'])])


def create_a_book_table_item(new_id, nyt_data, amazon_data, apple_data):
    """
    Creates a new item for the book table.
    
    This function forms a new book record by pulling relevant data from the New York Times, Amazon, and Apple bestseller lists. The resultant book record 
    is formatted as a dictionary.

    Args:
        new_id (int): The ID of the new bestseller book.
        nyt_data (dict): The New York Times bestseller data.
        amazon_data (list): The Amazon bestseller data.
        apple_data (list): The Apple bestseller data.

    Returns:
        dict: A dictionary containing the combined book data from the New York Times, Amazon, and Apple bestseller lists.
    """
    book = {
        'id': new_id,
        'url': amazon_data[0]['url'],
        'title': nyt_data['title'],
        'author': nyt_data['author'],
        'isbn10': [isbn['isbn10'] for isbn in nyt_data['isbns']],
        'isbn13': [isbn['isbn13'] for isbn in nyt_data['isbns']],
        'book_uri': [nyt_data['book_uri']],
        'contributor': nyt_data['contributor'],
        'description': [nyt_data['description']],
        'publisher': nyt_data['publisher'],
        'price': [nyt_data['price'], amazon_data[0]['price']],
        'dagger': nyt_data['dagger'],
        'asterisk': [nyt_data['asterisk']],
        'genre': apple_data,
        'rating': amazon_data[0]['rating'],
        'number_of_stars': amazon_data[0]['number_of_stars'],
        'number_of_pages': amazon_data[0]['number_of_pages'],
        'language': amazon_data[0]['language'],
        'publication_date': amazon_data[0]['publication_date'],
        'reviews_count': amazon_data[0]['reviews_count'],
    }

    return book


def create_a_rank_table_item(new_id, nyt_data):
    """
    Creates a new rank table item using the new book id and data from The New York Times.

    Args:
        new_id (int): The id of the book for which the rank table item is to be created.
        nyt_data (dict): The data dictionary from The New York Times.

    Returns:
        list: A list representing the rank table item.
    
    Raises:
        TypeError: If the data in the nyt_data dictionary is not of the expected type.
    """
    if not isinstance(nyt_data['bestsellers_date'], str):
        raise TypeError("bestsellers_date must be a string")
    if not isinstance(nyt_data['category'], str):
        raise TypeError("category must be a string")
    if not isinstance(nyt_data['rank'], int):
        raise TypeError("rank must be an integer")
    if not isinstance(nyt_data['rank_last_week'], int):
        raise TypeError("rank_last_week must be an integer")
    if not isinstance(nyt_data['weeks_on_list'], int):
        raise TypeError("weeks_on_list must be an integer")

    rank = [new_id, nyt_data['bestsellers_date'], nyt_data['category'], nyt_data['rank'], nyt_data['rank_last_week'], nyt_data['weeks_on_list']]

    return rank



def create_of_review_table_items(new_id, amazon_data):
    """
    Creates review table items for a given book using its id and Amazon data.

    This function constructs a list of lists, each sublist representing a review table item. Each review table item includes the book 'id', review id, stars, title, text, and date.

    Args:
        new_id (int): The id of the book for which the review table items are to be created. 
        amazon_data (list): The data list from Amazon, where each item is a dictionary that contains a 'reviews' key with a list of review data.

    Returns:
        list: A list of lists, where each sublist represents a review table item.

    """
    # Create an empty result list
    review = []

    # Iterate over each dictionary in the list
    for book in amazon_data:
        reviews = book['reviews']  # get the list of reviews

        # Iterate over each review
        for i, r in enumerate(reviews, start=1):
            # Extract the data you want and add it to the result list
            review_data = [new_id, i, r['stars'], r['title'], r['text'], convert_to_date(r['date'])]
            review.append(review_data)
    
    return review
