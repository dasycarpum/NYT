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
from src.data_collection.scraping_apple import scrape_apple_store_book


def main():
    """
    Execute the main for data collection, extraction, transformation, loading, and announcement.
    
    """
    
    genre = scrape_apple_store_book("https://goto.applebooks.apple/9781250284327?at=10lIEQ")
    print(genre)
    

if __name__ == "__main__":
    main()
