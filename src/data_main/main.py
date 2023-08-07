#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: the aim of this part of the application is to supplement the "nyt" database with information from a new bestseller selected by the NY Times..

"""

import os
import sys

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from config import NYT_api_key
from src.data_collection.api_nyt import get_nyt_book_categories, get_nyt_bestsellers
from src.data_collection.json_tools import json_field_to_list


def main():
    """
    Execute the main for data collection, extraction, transformation, loading, and announcement.
    
    """
    
    year = os.environ.get("YEAR")
    month = os.environ.get("MONTH")
    day = os.environ.get("DAY")

    # Validate the values
    if not year or not month or not day:
        raise ValueError("Please provide YEAR, MONTH, and DAY as environment variables.")

    list_of_categories = get_nyt_book_categories(NYT_api_key)
    print(list_of_categories)

    get_nyt_bestsellers(NYT_api_key, ["Hardcover Fiction", "Picture Books"], year=int(year), month=int(month), day=int(day))

    list_of_values = json_field_to_list("data/raw_data/best_sellers_{}_{}_{}.json".format(int(year), int(month), int(day)), 'buy_links', 'Apple Books')
    print(list_of_values)


if __name__ == "__main__":
    main()


