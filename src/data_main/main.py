#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: the aim of this part of the application is to supplement the "nyt" database with information from a new bestseller selected by the NY Times.

"""

import os
import sys
import json
from sqlalchemy import create_engine, text
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from config import DB_ENGINE, RAW_DATA_ABS_PATH, PROC_DATA_ABS_PATH
from src.data_ingestion.load import load_book_into_database, load_rank_into_database, load_review_into_database
from src.data_main.raw_data_summary import data_collection
from src.data_main.raw_data_transformation import extract_transform


def new_book_announcement(engine):
    """
    Announces the details of the most recently added bestseller in the database.

    This function connects to the given SQL engine and executes a query to fetch the details of the most recently added book in the 'book' table. It then prints the ID, URL, title, and author of this book. The function considers the book with the highest 'id' value as the most recent one.

    Args:
        engine (sqlalchemy.Engine): An instance of SQLAlchemy's Engine that will be used for database communication.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: An error occurred while executing the SQL command.
        sqlalchemy.exc.DBAPIError: The parent class for all exceptions thrown by the DBAPI2.
        
    """
    book_rank_query = """
    SELECT 
        b.id AS book_id,
        b.data->>'url' AS url,
        b.data->>'title' AS title,
        b.data->>'author' AS author,
        r.id_book AS book_id_rank, 
        r.date AS rank_date,
        r.category AS rank_category,
        r.rank AS current_rank,
        r.rank_last_week AS rank_last_week,
        r.weeks_on_list AS weeks_on_list
    FROM 
        book b
    LEFT JOIN 
        rank r ON b.id = r.id_book
    WHERE 
        b.id = (SELECT MAX(id) FROM book);
    """

    # Query to fetch the first and last reviews from the 'review' table based on the 'id'
    review_query = """
    (SELECT id_book, id_review, stars, title, text, date
    FROM review
    WHERE id_book = :book_id
    ORDER BY id_review ASC LIMIT 1)
    UNION ALL
    (SELECT id_book, id_review, stars, title, text, date
    FROM review
    WHERE id_book = :book_id
    ORDER BY id_review DESC LIMIT 1);
    """

    with engine.connect() as connection:
        result = connection.execute(text(book_rank_query))
        result = result.fetchall()

        last_book_id = 0
        print("New bestseller details:")
        for (book_id, url, title, author, book_id_rank, rank_date, rank_category, current_rank, rank_last_week, weeks_on_list) in result:
            print(f"id: {book_id}, url: {url}, title: {title}, author: {author}")
            if book_id_rank:
                print(f"  - Rank date: {rank_date}, Category: {rank_category}, Rank: {current_rank}, Rank last week: {rank_last_week}, Weeks on list: {weeks_on_list}, Book id rank: {book_id_rank}")
                last_book_id = book_id_rank

        # Fetch first and last reviews based on the book id
        reviews = connection.execute(text(review_query).bindparams(book_id=last_book_id)).fetchall()

        # Print reviews
        for (rev_book_id, rev_id, stars, rev_title, rev_text, rev_date) in reviews:
            shortened_text = " ".join(rev_text.split()[:10]) + "..." if len(rev_text.split()) > 10 else rev_text
            print(f"\nReview ID: {rev_id}, Stars: {stars}, Title: {rev_title}, Date: {rev_date}, Book id review: {rev_book_id}")
            print(f"Text: {shortened_text}")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Individual Book Insights', value='tab-1'),
        dcc.Tab(label='Comparative Insights', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            # Your individual book insights components go here
            html.H1("Individual Book Insights")
            # Example: dbc.Card(), dcc.Graph(), etc.
        ])
    elif tab == 'tab-2':
        return html.Div([
            # Your comparative insights components go here
            html.H1("Comparative Insights")
            # Example: dbc.Card(), dcc.Graph(), etc.
        ])



def main():
    """
    Execute the main for data collection, extraction, transformation, loading, and announcement.

    This function follows these steps:
    1. Creates a SQLAlchemy engine to interface with the database.
    2. Collects book data from The New York Times, Amazon, and Apple Store for the specific date.
    3. Extracts and transforms the collected raw data.
    4. Loads the processed data into book, rank, and review tables in the PostgreSQL database.
    5. Announces the details of the most recently added book in the database.

    Global Variables:
        DB_ENGINE (str): The database engine connection string.
        RAW_DATA_ABS_PATH (str): The path where raw data is stored.
        PROC_DATA_ABS_PATH (str): The path where processed data is stored.
    
    """
    year = os.environ.get("YEAR")
    month = os.environ.get("MONTH")
    day = os.environ.get("DAY")
    
    # Create a SQLAlchemy engine that will interface with the database.
    engine = create_engine(DB_ENGINE)

    """
    # Collect book data from The New York Times, Amazon, and Apple Store. 
    data_collection(year=int(year), month=int(month), day=int(day), engine= engine)

    # Manage the extraction and transformation of the data collected
    with open(RAW_DATA_ABS_PATH + "raw_data.json", encoding='utf-8') as json_file:
        raw_data = json.load(json_file)

    extract_transform(raw_data['new_id'], raw_data['nyt_data'], raw_data['amazon_data'], raw_data['apple_data'])

    # Load data tables in the PostgreSQL database
    load_book_into_database(PROC_DATA_ABS_PATH + 'book.json', engine, 'book')
    load_rank_into_database(PROC_DATA_ABS_PATH + 'rank.csv', engine, 'rank')
    load_review_into_database(PROC_DATA_ABS_PATH + 'review.csv', engine, 'review')
    """

    # Message following the incorporation of a new bestseller
    # new_book_announcement(engine)

    app.run_server(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    main()
