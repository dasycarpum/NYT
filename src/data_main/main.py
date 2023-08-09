#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: the aim of this part of the application is to supplement the "nyt" database with information from a new bestseller selected by the NY Times..

"""

import os
import sys
from sqlalchemy import create_engine, text

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from config import DB_ENGINE
from src.data_main.raw_data_summary import data_collection


def main():
    """
    Execute the main for data collection, extraction, transformation, loading, and announcement.
    
    """
    year = os.environ.get("YEAR")
    month = os.environ.get("MONTH")
    day = os.environ.get("DAY")
    
    # Create a SQLAlchemy engine that will interface with the database.
    engine = create_engine(DB_ENGINE)

    data_collection(year=int(year), month=int(month), day=int(day), engine= engine)


if __name__ == "__main__":
    main()
