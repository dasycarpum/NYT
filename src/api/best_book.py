#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-08

@author: Roland

@abstract: by setting the book genre and year of publication, the API will return the titles and authors of the top 5 bestsellers, based on the number of weeks remaining in the ranking.
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
# from config import DB_ENGINE

app = FastAPI()

DB_NAME = 'nyt'
DB_USER = 'postgres'
DB_PASS = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_ENGINE='postgresql://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME


try:
    # Attempt to create the database engine
    engine = create_engine(DB_ENGINE)
except Exception as e:
    raise RuntimeError(f"Failed to create database engine: {e}")


@app.get("/status")
async def read_status():
    """
    Check the health and functionality of the API.

    Args: None
        
    Returns:
        dict: a dictionary with "status": "ok" if the API is healthy
    """
    return {"status": "OK"}


@app.get("/all_genres", response_model=List[str])
async def read_all_genres():
    """
    Fetches all distinct genres from the 'book' table.

    This function uses SQLAlchemy to execute a SQL query against a PostgreSQL database.
    The query fetches all distinct genres present in the 'book' table.

    Returns:
        List[str]: A list of all distinct genres in the 'book' table.

    Raises:
        HTTPException: An exception is raised if no data is found (HTTP status code 404),
                       or if there is a SQLAlchemy error (HTTP status code 500).
    """
    query = "SELECT DISTINCT data->>'genre' AS genre FROM book;"
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            genres = [row[0] for row in result]
            
            if not genres:
                raise HTTPException(status_code=404, detail="No genres found")
            return genres
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/best_book")
async def read_best_books(year: str, genre: str):
    """
    Fetches the best books based on the specified year and genre.

    This function uses SQLAlchemy to execute a SQL query against a PostgreSQL database. The query fetches the top 5 books of the specified genre and year, sorted by their weeks on the list, while ensuring that each 'author - title' pair is unique. The result is returned in JSON format.

    Args:
        year (str): The year the books were published.
        genre (str): The genre of the books.

    Returns:
        JSON: A JSON-formatted list containing the top 5 books of the specified genre and year.

    Raises:
        HTTPException: An exception is raised if no data is found (HTTP status code 404), or if there is a SQLAlchemy error (HTTP status code 500).

    """
    query = f"""
    WITH UniqueBooks AS (
        SELECT DISTINCT ON (b.data->>'author', b.data->>'title')
            b.data->>'title' AS title,
            b.data->>'author' AS author,
            r.weeks_on_list
        FROM
            book AS b
        JOIN
            rank AS r ON b.id = r.id_book
        WHERE
            b.data->>'publication_date' LIKE '{year}-%'
            AND b.data->>'genre' = '{genre}'
        ORDER BY
            b.data->>'author',
            b.data->>'title',
            r.weeks_on_list DESC
    )
    SELECT json_agg(row_to_json(UniqueBooks.*))
    FROM (SELECT * FROM UniqueBooks ORDER BY weeks_on_list DESC LIMIT 5) AS UniqueBooks;
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            best_book_json = result.fetchone()[0]
            if not best_book_json:
                raise HTTPException(status_code=404, detail="No data found")
            return best_book_json
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"SQLAlchemy error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dataset: {e}")
