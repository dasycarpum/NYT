"""
Created on 2023-08-13

@author: Roland

@abstract: create for the 'best_book.py' source file,
    2 unit tests for the 'read_all_genres' function
    2 unit tests for the 'read_best_books' function
    
"""

import os
import sys
from unittest.mock import MagicMock
import pytest
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'api')
# Adding the absolute path to system path
sys.path.append(src_dir)
from best_book import read_all_genres, read_best_books


@pytest.mark.asyncio
async def test_read_all_genres_successful():
    mock_engine = MagicMock()
    mock_app = MagicMock()
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.return_value = [(1,), (2,), (3,)]

    result = await read_all_genres(mock_engine, mock_app)
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_read_all_genres_exception():
    mock_engine = MagicMock()
    mock_app = MagicMock()
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.side_effect = Exception("Database Error")
    
    with pytest.raises(HTTPException) as exc_info:
        await read_all_genres(mock_engine, mock_app)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Database Error"


@pytest.mark.asyncio
async def test_read_best_books_successful():
    mock_engine = MagicMock()
    mock_app = MagicMock()
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = [{'title': 'Book1', 'author': 'Author1', 'weeks_on_list': 12}]

    mock_connection.execute.return_value.fetchone.return_value = [mock_result]

    best_books = await read_best_books(mock_engine, mock_app, '2023', 'Fiction')
    
    assert best_books == mock_result


@pytest.mark.asyncio
async def test_read_best_books_sqlalchemy_error():
    mock_engine = MagicMock()
    mock_app = MagicMock()
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    
    mock_connection.execute.side_effect = SQLAlchemyError("SQLAlchemy error")

    with pytest.raises(HTTPException) as exc_info:
        await read_best_books(mock_engine, mock_app, '2023', 'Fiction')

    assert exc_info.value.status_code == 500
    assert "SQLAlchemy error occurred" in exc_info.value.detail
