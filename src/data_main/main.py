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
from src.data_collection.scraping_amazon import scrape_amazon_books
from src.data_ingestion.extract_transform import create_of_review_table_items


def main():
    """
    Execute the main for data collection, extraction, transformation, loading, and announcement.
    
    """
    
    amazon_data = scrape_amazon_books("https://www.amazon.com/dp/0593441273?tag=NYTBSREV-20")
    
    review = create_of_review_table_items(9999, amazon_data)

    print(review)
    

if __name__ == "__main__":
    main()
