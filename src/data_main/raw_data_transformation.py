#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: manage the extraction and transformation of data supplied during the previous stage of centralized raw data collection.

"""

import os
import sys
import json
import csv


# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from config import PROC_DATA_ABS_PATH
import src.data_ingestion.extract_transform as et


def save_to_file(data, filename, filetype='json'):
    """Saves provided data to the specified file.
    
    Args:
        data (list or dict): The data to be saved.
        filename (str): The path and name of the file to save the data.
        filetype (str): The format in which to save the data. Defaults to 'json'.
    """
    # Check if the directory exists and create if not
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        if filetype == 'json':
            json.dump(data, file)
        elif filetype == 'csv':
            writer = csv.writer(file)
            writer.writerow(data[0])  # write the header
            writer.writerows(data[1:])  # write the data rows
        else:
            raise ValueError(f"Unknown filetype: {filetype}")


def extract_transform(new_id, nyt_data, amazon_data, apple_data):
    """Extracts and transforms the data of a bestseller.

    This function creates the book, rank and review data of a bestseller, and 
    saves each into its respective file.

    Args:
        new_id (int): The ID of the new bestseller book.
        nyt_data (dict): The New York Times bestseller data.
        amazon_data (dict): The Amazon bestseller data.
        apple_data (dict): The Apple bestseller data.

    Return:
        None

    """
    # Create and save the book data
    book = et.create_a_book_table_item(new_id, nyt_data, amazon_data, apple_data)
    save_to_file(book, PROC_DATA_ABS_PATH + "book.json")

    # Create and save the rank data
    columns = ['id_book', 'date', 'category', 'rank', 'rank_last_week', 'weeks_on_list']
    rank = et.create_a_rank_table_item(new_id, nyt_data)
    save_to_file([columns, [rank]], PROC_DATA_ABS_PATH + "rank.csv", 'csv')

    # Create and save the review data
    columns = ['id_book', 'id_review', 'stars', 'title', 'text', 'date']
    review = et.create_of_review_table_items(new_id, amazon_data)
    save_to_file([columns, review], PROC_DATA_ABS_PATH + "review.csv", 'csv')
