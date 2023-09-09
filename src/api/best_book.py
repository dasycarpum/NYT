#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-08

@author: Roland

@abstract: by setting the book genre and year of publication, the API will return the titles and authors of the top 5 bestsellers, based on the number of weeks remaining in the ranking.
"""

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


async def read_all_genres(engine, app):
    """
    Fetches all distinct genres from the 'book' table.

    This function uses SQLAlchemy to execute a SQL query against a PostgreSQL database. The query fetches all distinct genres present in the 'book' table.

    Args:
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.
        app(FastAPI): The FastAPI application instance.

    Returns:
        List[str]: A list of all distinct genres in the 'book' table.

    Raises:
        HTTPException: An exception is raised if no data is found (HTTP status code 404), or if there is a SQLAlchemy error (HTTP status code 500).
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


async def read_best_books(engine, app, year: str, genre: str):
    """
    Fetches the best books based on the specified year and genre.

    This function uses SQLAlchemy to execute a SQL query against a PostgreSQL database. The query fetches the top 5 books of the specified genre and year, sorted by their weeks on the list, while ensuring that each 'author - title' pair is unique. The result is returned in JSON format.

    Args:
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.
        app (FastAPI): The FastAPI application instance.
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
