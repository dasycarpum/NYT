#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-06-17

@author: Roland

@abstract: use an ML model to predict the success of a book based on certain parameters such as genre, author, price, and initial reviews. This can help publishers and authors understand which elements might contribute more towards a book's success.
"""

import re
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


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

# Data cleaning
# ==============

def dataset_cleaning(df):
    """
    Cleans the given pandas DataFrame in several ways including replacing 
    empty strings with NaN, removing rows with missing data in key 
    columns, extracting maximum prices from price lists, handling 
    punctuation in rating data, replacing missing genre data with the 
    mode, changing the data type of various columns, removing duplicates, 
    and dropping unnecessary columns.

    Args:
        df (pd.DataFrame): The DataFrame to clean. It's expected to 
        contain the following columns:
            - rating
            - number_of_stars
            - reviews_count
            - price
            - genre
            - dagger
            - number_of_pages
            - mean_first_stars
            - max_weeks
            - id
            - title

    Returns:
        df (pd.DataFrame): A clean version of the input DataFrame. It 
        includes a new 'max_price' column and no longer includes the 
        'id', 'title', and 'price' columns.

    Raises:
        ValueError: If the DataFrame doesn't contain the expected columns.
        TypeError: If the argument provided is not a pandas DataFrame.
    
    """
    # Replace blank by NaN
    df[df.select_dtypes(include=['object']).columns] = df.select_dtypes(include=['object']).replace('', np.nan)

    # Remove rows with concomitant NaN in 3 columns
    df = df.dropna(axis=0, how='all',                
                subset=['rating', 'number_of_stars', 'reviews_count']) 

    # Define a function to extract the maximum price from a list
    def extract_max_price(price_list):
        pattern = r'\d+\.\d+'
        matches = re.findall(pattern, price_list)
        numbers = [float(value) for value in matches]
        return max(numbers)

    # Apply the function to the 'price' column
    df['max_price'] = df['price'].apply(extract_max_price)

    # Replace comma in 'rating' column
    df['rating'] = df['rating'].replace(',', '', regex=True)

    # Replace NaN with the mode in the 'genre' column
    df['genre'].fillna(df['genre'].mode()[0], inplace = True)

    # Typing of numeric columns
    df.fillna(value={'dagger': False, 
                    'rating': 0, 
                    'number_of_stars': 0.0, 
                    'number_of_pages': 0, 
                    'reviews_count': 0,
                    'mean_first_stars' : 0.0}, inplace=True)

    df = df.astype({'dagger': 'bool', 
                    'rating' : 'int', 
                    'number_of_stars' : 'float', 
                    'number_of_pages' : 'int', 
                    'reviews_count' : 'int',
                    'mean_first_stars' : 'float'})

    # Deleting title-author duplicates
    df.sort_values(by='max_weeks', ascending=False, inplace=True)
    df.drop_duplicates(subset=['title','author'],
                    keep='first',
                    inplace=True)

    # Removing unnecessary columns
    df = df.drop(columns=['id', 'title', 'price'])

    return df


# Creation of a single target
# ===========================

def target_combination(df):
    """
    Combines the 'best_ranking' and 'max_weeks' features from a DataFrame into a single feature using StandardScaler and PCA. This function will add a new column 'combined_target' to the dataframe which represents the combined 
    feature.

    Args:
        df (pandas.DataFrame): DataFrame which includes at least 'best_ranking' and 'max_weeks' columns.

    Returns:
        df (pandas.DataFrame): DataFrame with an additional 'combined_target' column which is a combination of 'best_ranking' and 'max_weeks', standardized and reduced to one dimension using PCA.

    Raises:
        KeyError: If either 'best_ranking' or 'max_weeks' does not exist in the DataFrame.
        ValueError: If PCA fit fails.

    """
    # Standardize the features
    scaler = StandardScaler()
    targets_scaled = scaler.fit_transform(df[['best_ranking', 'max_weeks']])

    # Apply PCA
    pca = PCA(n_components=1)
    targets_pca = pca.fit_transform(targets_scaled)

    df['combined_target'] = targets_pca

    return df