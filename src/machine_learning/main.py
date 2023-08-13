#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-13

@author: Roland

@abstract: the aim of this part of the application is to use the "nyt" database to learn patterns and predict certain events.

"""

import os
import sys
from sqlalchemy import create_engine

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from config import DB_ENGINE
from src.machine_learning.book_success import sql_query_to_create_dataset

  

def main():
   
    # Create a SQLAlchemy engine that will interface with the database.
    engine = create_engine(DB_ENGINE)

    df = sql_query_to_create_dataset(engine)

    print("Dataframe :", df.shape)

if __name__ == "__main__":
    main()
