#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: create for the 'raw_data_transformation .py' source file,
    3 unit tests for the 'save_to_file' function
    1 unit test for the 'extract_transform' function
    
"""

import os
import sys
from unittest.mock import mock_open, patch, call
import pytest

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from src.data_main.raw_data_transformation import save_to_file, extract_transform
from src.data_ingestion.extract_transform import create_a_book_table_item, create_a_rank_table_item, create_of_review_table_items
from config import PROC_DATA_ABS_PATH


# This test checks if the save_to_file function is correctly handling data when the filetype is specified as 'json'
from unittest.mock import patch, mock_open

def test_save_to_file_json_success():
    mock = mock_open()
    data = {"key": "value"}

    with patch('builtins.open', mock), \
         patch('os.path.exists', return_value=False), \
         patch('os.makedirs'):
        save_to_file(data, 'test.json')

    mock.assert_called_once_with('test.json', 'w', newline='', encoding='utf-8')
    handle = mock()
    assert handle.write.called


# This test checks if the save_to_file function is correctly handling data when the filetype is specified as 'csv'
def test_save_to_file_csv_success():
    mock = mock_open()
    data = [['header1', 'header2'], ['data1', 'data2']]

    with patch('builtins.open', mock), patch('csv.writer') as writer_mock:
        save_to_file(data, 'test.csv', 'csv')

    mock.assert_called_once_with('test.csv', 'w', newline='', encoding='utf-8')
    writer_mock.assert_called_once_with(mock())
    writer_mock.return_value.writerow.assert_called_once_with(data[0])
    writer_mock.return_value.writerows.assert_called_once_with(data[1])


# This test checks that the save_to_file function raises a ValueError when given an unknown filetype. 
def test_save_to_file_unknown_type():
    mock = mock_open()
    data = {"key": "value"}

    with patch('builtins.open', mock):
        with pytest.raises(ValueError):
            save_to_file(data, 'test.txt', 'txt')



# Test data
nyt_data = {
        "rank": 3,
        "rank_last_week": 7,
        "weeks_on_list": 15,
        "asterisk": 0,
        "dagger": 0,
        "primary_isbn10": "1943200084",
        "primary_isbn13": "9781943200085",
        "publisher": "Compendium",
        "description": "An ode to teachers.",
        "price": "0.00",
        "title": "BECAUSE I HAD A TEACHER",
        "author": "Kobi Yamada.",
        "contributor": "by Kobi Yamada. Illustrated by Natalie Russell",
        "contributor_note": "Illustrated by Natalie Russell",
        "amazon_product_url": "https://www.amazon.com/Because-Had-Teacher-teachers-everywhere/dp/1943200084?tag=NYTBSREV-20",
        "buy_links": [
            {
                "name": "Amazon",
                "url": "https://www.amazon.com/Because-Had-Teacher-teachers-everywhere/dp/1943200084?tag=NYTBSREV-20"
            },
            {
                "name": "Apple Books",
                "url": "https://goto.applebooks.apple/9781943200085?at=10lIEQ"
            }
        ],
        "book_uri": "nyt://book/b4c3cb4e-6aa2-5cbf-b314-48274c249dc3",
        "category": "Picture Books",
        "bestsellers_date": "2023-6-5"
    }  # Fill with suitable data
amazon_data = [
        {
            "url": "https://www.amazon.com/Because-Had-Teacher-teachers-everywhere/dp/1943200084?tag=NYTBSREV-20",
            "rating": "4,373",
            "number_of_stars": "4.9",
            "price": "$7.85",
            "number_of_pages": "40",
            "language": "English",
            "publication_date": "2017-03-01",
            "ISBN-10": "1943200084",
            "ISBN-13": "978-1943200085",
            "reviews_count": 497,
            "reviews": [{
                    "stars": "5.0",
                    "title": "the title of review 1",
                    "text": "the text of review 1",
                    "date": "Reviewed in the United States on April 24, 2023"
                },
                {
                    "stars": "4.0",
                    "title": "the title of review 2",
                    "text": "the text of review 2",
                    "date": "Reviewed in the United States on April 25, 2023"
                }]
        }
    ]  # Fill with suitable data
apple_data = "undetermined" # Fill with suitable data
book_data = {"id": 5832, "url": "https://www.amazon.com/Because-Had-Teacher-teachers-everywhere/dp/1943200084?tag=NYTBSREV-20", "title": "BECAUSE I HAD A TEACHER", "author": "Kobi Yamada.", "isbn10": ["1943200084"], "isbn13": ["9781943200085"], "book_uri": ["nyt://book/b4c3cb4e-6aa2-5cbf-b314-48274c249dc3"], "contributor": "by Kobi Yamada. Illustrated by Natalie Russell", "description": ["An ode to teachers."], "publisher": "Compendium", "price": ["0.00", "$7.85"], "dagger": 0, "asterisk": [0], "genre": "undetermined", "rating": "4,373", "number_of_stars": "4.9", "number_of_pages": "40", "language": "English", "publication_date": "2017-03-01", "reviews_count": 497} # Expected book data
rank_data = [[5832,2023-6-5,'Picture Books',3,7,15]]  # Expected rank data
review_data = [[5832,99,5.0,"the title of review 1","the text of review 1",'2023-04-24'], [5832,100,4.0,"the title of review 2","the text of review 2",'2023-04-25']]  # Expected review data

# This test checks if the extract_transform function is correctly handling data 
def test_extract_transform_success():
    new_id = 1

    # Mock the file saving function and the creation functions to isolate the unit under test
    with patch('src.data_main.raw_data_transformation.save_to_file') as mock_save, \
            patch('src.data_ingestion.extract_transform.create_a_book_table_item', return_value=book_data) as mock_book, \
            patch('src.data_ingestion.extract_transform.create_a_rank_table_item', return_value=rank_data) as mock_rank, \
            patch('src.data_ingestion.extract_transform.create_of_review_table_items', return_value=review_data) as mock_review:
        extract_transform(new_id, nyt_data, amazon_data, apple_data)

        # Check that the mock functions were called with the expected arguments
        mock_book.assert_called_once_with(new_id, nyt_data, amazon_data, apple_data)
        mock_rank.assert_called_once_with(new_id, nyt_data)
        mock_review.assert_called_once_with(new_id, amazon_data)
        
        # Check that the mock saving function was called with the correct arguments
        assert mock_save.call_args_list[0] == call({"id": 5832, "url": "https://www.amazon.com/Because-Had-Teacher-teachers-everywhere/dp/1943200084?tag=NYTBSREV-20", "title": "BECAUSE I HAD A TEACHER", "author": "Kobi Yamada.", "isbn10": ["1943200084"], "isbn13": ["9781943200085"], "book_uri": ["nyt://book/b4c3cb4e-6aa2-5cbf-b314-48274c249dc3"], "contributor": "by Kobi Yamada. Illustrated by Natalie Russell", "description": ["An ode to teachers."], "publisher": "Compendium", "price": ["0.00", "$7.85"], "dagger": 0, "asterisk": [0], "genre": "undetermined", "rating": "4,373", "number_of_stars": "4.9", "number_of_pages": "40", "language": "English", "publication_date": "2017-03-01", "reviews_count": 497}, PROC_DATA_ABS_PATH + 'book.json')
        
        assert mock_save.call_args_list[1] == call([['id_book', 'date', 'category', 'rank', 'rank_last_week', 'weeks_on_list'], [[[5832, 2012, 'Picture Books', 3, 7, 15]]]], PROC_DATA_ABS_PATH + 'rank.csv', 'csv')
        
        assert mock_save.call_args_list[2] == call([['id_book', 'id_review', 'stars', 'title', 'text', 'date'], [[5832,99,5.0,"the title of review 1","the text of review 1",'2023-04-24'], [5832,100,4.0,"the title of review 2","the text of review 2",'2023-04-25']]], PROC_DATA_ABS_PATH + 'review.csv', 'csv')
