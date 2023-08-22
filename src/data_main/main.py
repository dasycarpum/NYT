#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-25

@author: Roland

@abstract: the aim of this part of the application is to supplement the "nyt" database with information from a new bestseller selected by the NY Times, and display in a dashboard the main features of this new book.

"""

import os
import sys
import json
from sqlalchemy import create_engine, text
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
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


# Create a SQLAlchemy engine that will interface with the database.
engine = create_engine(DB_ENGINE)

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
    """
    Render content for the given tab.

    This function fetches book details, review details, and rank details from
    a database and uses them to generate insights in the form of text, tables,
    and plots. It supports two tabs: 'tab-1' for individual book insights, and
    'tab-2' for comparative insights.

    Args:
        tab (str): Identifier for the tab whose content is to be rendered. Supported values are 'tab-1' and 'tab-2'.

    Returns:
        dash_html_components.Div: A Dash Div component containing the rendered content for the given tab.

    Raises:
        ValueError: If an unsupported tab identifier is provided.
    """
    
    if tab == 'tab-1':
        return _render_individual_insights()
    
    elif tab == 'tab-2':
        return _render_comparative_insights()

    else:
        raise ValueError(f"Unsupported tab identifier: {tab}")


def _fetch_latest_book_details():
    """Fetch the details of the latest book in the database."""
    book_query = """
        SELECT 
            b.id AS book_id,
            b.data->>'publisher' AS publisher,
            b.data->>'title' AS title,
            b.data->>'author' AS author,
            b.data->>'genre' AS genre,
            b.data->>'number_of_pages' AS number_of_pages,
            b.data->>'price' AS price,
            b.data->>'number_of_stars' AS number_of_stars,
            b.data->>'reviews_count' AS reviews_count
        FROM 
            book b
        WHERE 
            b.id = (SELECT MAX(id) FROM book);
        """
    with engine.connect() as connection:
        result = connection.execute(text(book_query))
        book_details = result.fetchone()

    return book_details


def _fetch_best_and_worst_reviews():
    """Fetch the latest reviews from the database."""
    review_query = """
        WITH LatestBook AS (
            SELECT MAX(id) AS max_id FROM book
        )
        (SELECT id_book, stars, title, text, date
        FROM review
        WHERE id_book = (SELECT max_id FROM LatestBook)
        ORDER BY stars ASC LIMIT 1)
        UNION ALL
        (SELECT id_book, stars, title, text, date
        FROM review
        WHERE id_book = (SELECT max_id FROM LatestBook)
        ORDER BY stars DESC LIMIT 1);
        """
        
    with engine.connect() as connection:
        result = connection.execute(text(review_query))
        reviews = result.fetchall()

    # Extract the worst and best reviews
    worst_review, best_review = reviews

    return worst_review, best_review

def _fetch_rank_data():
    """Fetch rank data for the latest book from the database."""
    rank_query = """
        WITH LatestBook AS (
            SELECT MAX(id) AS max_id FROM book
        )
        SELECT id_book, AVG(rank) AS avg_rank, date FROM rank
        WHERE id_book = (SELECT max_id FROM LatestBook)
        GROUP BY id_book, date
        ORDER BY date ASC;
    """
    with engine.connect() as connection:
        result = connection.execute(text(rank_query))
        rank_data = result.fetchall()

    # Extract rank and date for plotting
    dates = [row[2] for row in rank_data]
    avg_ranks = [row[1] for row in rank_data]

    return dates, avg_ranks

def _render_individual_insights():
    """Render insights for an individual book."""
    book_details = _fetch_latest_book_details()
    worst_review, best_review = _fetch_best_and_worst_reviews()
    dates, avg_ranks = _fetch_rank_data()

    # Create book ratings and reviews gauges
    fig = make_subplots(rows=1, cols=2, 
                specs=[[{"type": "indicator"}, {"type": "indicator"}]])

        # Adding the Star Rating Gauge to the first column
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=float(book_details[7]),  # Convert number_of_stars to float
            delta={'reference': 2.5},  # The midpoint of the gauge
            gauge={
                'axis': {'range': [0, 5]},
                'bar': {'color': 'gold'},
                'steps': [
                    {'range': [0, 1], 'color': 'gray'},
                    {'range': [1, 2], 'color': 'lightgray'},
                    {'range': [2, 3], 'color': 'white'},
                    {'range': [3, 4], 'color': 'lightyellow'},
                    {'range': [4, 5], 'color': 'yellow'},
                ],
            },
            title={'text': '<br>Star Rating on Amazon'} 
        ),
        row=1, col=1
    )

        # Adding the Reviews Gauge to the second column
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=int(book_details[8]),  # Convert reviews_count to integer
            gauge={
                'axis': {'range': [None, int(book_details[8]) + 1000]},
                'bar': {'color': 'blue'},
            },
            title={'text': '<br>Total Number of Amazon Reviews'}  # Adjusting vertical position of title
        ),
        row=1, col=2
    )

    fig.update_layout(title_text='Book Ratings & Reviews')

    # Create the rank evolution graph
    rank_evolution_fig = {
        'data': [
            {
                'x': dates,
                'y': avg_ranks,
                'type': 'line',
                'name': 'Rank Evolution',
                'line': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': 'Rank Evolution by Date',
            'xaxis': {
                'title': 'Date'
            },
            'yaxis': {
                'title': 'Rank',
                'autorange': 'reversed'  # To display lower ranks (which are better) at the top
            }
        }
    }

    return html.Div([
        html.H1("Individual Book Insights"),
        html.Hr(),
        html.H3("Book Details Pane"),
        html.P(f"Title : {book_details[2]}"),
        html.P(f"Author : {book_details[3]}"),
        html.P(f"Publisher : {book_details[1]}"),
        html.P(f"Genre : {book_details[4]}"),
        html.P(f"Number of Pages : {book_details[5]}"),
        html.Hr(),
        html.H3("Pricing and Rating Pane"),
        html.P(f"Price: ${book_details[6]}"),
        dcc.Graph(figure=fig),
        html.Hr(),
        html.H3("Reviews Snapshot"),
        html.Div([
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Worst Review"),
                        html.Th("Best Review")
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(worst_review[4].strftime('%B %d, %Y')),  # Worst review date
                        html.Td(best_review[4].strftime('%B %d, %Y'))   # Best review date
                    ]),
                    html.Tr([
                        html.Td(f"Stars : {worst_review[1]}"),  # Worst review star rating
                        html.Td(f"Stars : {best_review[1]}")    # Best review star rating
                    ]),
                    html.Tr([
                        html.Td(worst_review[2]),  # Worst review title
                        html.Td(best_review[2])    # Best review title
                    ]),
                    html.Tr([
                        html.Td(worst_review[3]),  # Worst review text
                        html.Td(best_review[3])    # Best review text
                    ])
                ])
            ])
        ], style={'width': '100%', 'overflowX': 'auto'}),  # Style to make sure the table fits and scrolls if needed
        html.Hr(),
        html.H3("Rank Evolution Pane"),
        dcc.Graph(figure=rank_evolution_fig)
    ])

def _render_comparative_insights():
    """Render comparative insights across multiple books."""
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

    app.run_server(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    main()
