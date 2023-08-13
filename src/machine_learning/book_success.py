#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-06-17

@author: Roland

@abstract: use an ML model to predict the success of a book based on certain parameters such as genre, author, price, and initial reviews. This can help publishers and authors understand which elements might contribute more towards a book's success.
"""

import pandas as pd

# SQL query
# =========
def sql_query_to_create_dataset(engine):
    """
    Run a specific SQL query in the 'nyt' PostgreSQL database, to pull data related to books (including features like title, author, genre, price, dagger, asterisk, rating, number_of_stars, number_of_pages, reviews_count, mean_first_stars, best_ranking, and max_weeks), and returns the result as a pandas DataFrame.

    The query joins three tables ('book', 'rank', and 'first_reviews') 
    based on the book ID, and applies aggregation functions MIN() and 
    MAX() on certain columns.

    Args:
        engine (Engine): The SQLAlchemy database connection, to provide a source of database connectivity and behavior.

    Returns:
        df (pd.DataFrame): A DataFrame containing the result of the SQL 
        query. The DataFrame includes the following columns:
            - book.id: The unique identifier of the book
            - title: The title of the book
            - author: The author of the book
            - genre: The genre of the book
            - price: The price of the book
            - dagger: A feature of the book denoted as 'dagger'
            - asterisk: A feature of the book denoted as 'asterisk'
            - rating: The rating of the book
            - number_of_stars: The number of stars of the book
            - number_of_pages: The number of pages in the book
            - reviews_count: The count of reviews for the book
            - mean_first_stars: The average of the first stars of the book
            - best_ranking: The best ranking of the book
            - max_weeks: The maximum weeks of the book's record

    """
    
    # Create a database query to supply potential data, features and targets
    query = """
    SELECT  book.id,
            book.data->>'title' AS title,
            book.data->>'author' AS author,
            book.data->>'genre' AS genre,    
            book.data->>'price' AS price, 
            book.data->>'dagger' AS dagger,
            book.data->>'dagger' AS asterisk,
            book.data->>'rating' AS rating, 
            book.data->>'number_of_stars' AS number_of_stars,
            book.data->>'number_of_pages' AS number_of_pages,
            book.data->>'reviews_count' AS reviews_count,
            first_reviews.avg_stars AS mean_first_stars,
            MIN(rank.rank) AS best_ranking,
            MAX(rank.weeks_on_list) AS max_weeks
    FROM book
    LEFT JOIN rank ON book.id = rank.id_book
    LEFT JOIN first_reviews ON book.id = first_reviews.id_book
    GROUP BY book.id, 
            book.data->>'title',   
            book.data->>'author',
            book.data->>'genre',    
            book.data->>'price',
            book.data->>'dagger',
            book.data->>'asterisk',
            book.data->>'rating', 
            book.data->>'number_of_stars',
            book.data->>'number_of_pages',
            book.data->>'reviews_count',
            first_reviews.avg_stars;
    """

    # Create the DataFrame
    df = pd.read_sql_query(query, con=engine)
    
    return df

