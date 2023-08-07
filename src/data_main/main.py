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

def main():
    """
    Execute the main for data collection, extraction, transformation, loading, and announcement.
    
    """

    list_of_categories = get_nyt_book_categories(NYT_api_key)
    print(list_of_categories)

    get_nyt_bestsellers(NYT_api_key,
                        ["Hardcover Fiction", "Picture Books"],
                        year=2022, month=7, day=3)
    

if __name__ == "__main__":
    main()
