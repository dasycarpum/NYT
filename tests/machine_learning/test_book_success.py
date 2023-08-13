#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-13

@author: Roland

@abstract: create for the 'book_success.py' source file,
    2 unit tests for the 'sql_query_to_create_dataset' function
    y unit tests for the '' function
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import MagicMock
from sqlalchemy.engine import Engine

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'machine_learning')
# Adding the absolute path to system path
sys.path.append(src_dir)
from book_success import sql_query_to_create_dataset


def test_sql_query_to_create_dataset_valid_output(mocker):
    # Mocking the engine and database query
    mock_engine = mocker.MagicMock(spec=Engine)
    mock_query_result = [
        {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "genre": "Test Genre",
            "price": "20",
            "dagger": "test dagger",
            "asterisk": "test asterisk",
            "rating": "4.5",
            "number_of_stars": "4",
            "number_of_pages": "200",
            "reviews_count": "100",
            "mean_first_stars": "4.5",
            "best_ranking": "1",
            "max_weeks": "10"
        }
    ]
    
    mocker.patch('pandas.read_sql_query', return_value=pd.DataFrame(mock_query_result))

    # Run the function
    result_df = sql_query_to_create_dataset(mock_engine)
    
    # Asserts
    assert not result_df.empty
    assert list(result_df.columns) == ["id", "title", "author", "genre", "price", "dagger", "asterisk", "rating", "number_of_stars", "number_of_pages", "reviews_count", "mean_first_stars", "best_ranking", "max_weeks"]
    assert result_df.iloc[0]["id"] == 1


def test_sql_query_to_create_dataset_empty_output(mocker):
    # Mocking the engine and database query
    mock_engine = mocker.MagicMock(spec=Engine)
    
    mocker.patch('pandas.read_sql_query', return_value=pd.DataFrame())
    
    # Run the function
    result_df = sql_query_to_create_dataset(mock_engine)
    
    # Assert
    assert result_df.empty


