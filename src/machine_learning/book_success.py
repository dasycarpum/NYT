#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-06-17

@author: Roland

@abstract: use an ML model to predict sales ranking of a book based on certain parameters such as genre, author, price, and initial reviews. This can help publishers and authors understand which elements might contribute more towards a book's success.
"""

import re
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import GradientBoostingRegressor

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


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
    df.fillna(value={'dagger':0,
                    'rating': 0, 
                    'number_of_stars': 0.0, 
                    'number_of_pages': 0, 
                    'reviews_count': 0,
                    'mean_first_stars' : 0.0}, inplace=True)

    df = df.astype({'dagger': 'int',
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


# Relationships visualization between target and feature variables
# ==================================================================

cols = ['combined_target', 'rating', 'number_of_stars', 'number_of_pages', 'reviews_count', 'mean_first_stars', 'max_price']
    
def create_heatmap(df):
    """
    Create a correlation heatmap for numeric columns of a DataFrame.

    This function takes a DataFrame, extracts its numeric columns, and then
    calculates the correlation matrix for these columns. It then visualizes
    this correlation matrix as a heatmap using Plotly's graph_objects.

    Args:
        df (pd.DataFrame): Input DataFrame for which the correlation heatmap
            is to be generated.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly Figure object visualizing 
            the correlation heatmap.
    
    """
    # Correlation heatmap between numeric variables
    numeric_df = df[cols]
    correlation_matrix = numeric_df.corr()
    
    # Creating a heatmap using Plotly's graph_objects
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='rdbu', 
        zmin=-1,  # because correlation coefficients range from -1 to 1
        zmax=1,
        colorbar=dict(title='Correlation Coefficient'),
        hoverinfo='z'
    ))
    
    heatmap_fig.update_layout(
        title='Correlation Heatmap',
        xaxis=dict(tickangle=-45),
    )
    
    return heatmap_fig


def create_3D_scatter(df):
    """
    Create a 3D scatter plot visualizing reviews, rating, and sales ranking.

    This function uses Plotly Express to generate a 3D scatter plot. The x, y, and z dimensions of the scatter plot represent the 'reviews_count', rating', and 'combined_target' columns of the input DataFrame respectively. Additionally, the color of each point is determined by the 'dagger' column of the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame containing the columns 'reviews_count', 'rating', 'combined_target', and 'dagger'.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly Figure object visualizing the 3D scatter plot.

    """
    fig = px.scatter_3d(df, x="reviews_count", y="rating", z="combined_target",
                    color="dagger", opacity=0.7)
    
    fig.update_layout(title_text="3D Scatter Plot of Reviews, Rating, and Sales Ranking")
    
    return fig


def create_box_plot(df):
    """
    Create a box plot visualizing the distribution of sales ranking by genre.

    This function utilizes Seaborn to plot a box plot of the 'combined_target' column grouped by the 'genre' column from the input DataFrame. The resulting Seaborn plot is then converted to a Plotly figure to be returned.

    Args:
        df (pd.DataFrame): Input DataFrame containing the columns 'genre' and 'combined_target'.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly Figure object visualizing the box plot.

    Note:
        This function both creates a Seaborn plot and returns a Plotly figure. However, only the Plotly figure
        is returned; the Seaborn plot will be displayed when this function is called if using a Jupyter environment 
        or another plotting backend that displays plots automatically.
    
    """
    # Using seaborn to create the box plot
    plt.figure(figsize=(10, 6))
    box_plot = sns.boxplot(x='genre', y='combined_target', data=df)
    box_plot.set_xticklabels(box_plot.get_xticklabels(), rotation=45)
    
    # Convert the matplotlib figure to plotly
    plotly_fig = go.Figure(
        data=[go.Box(y=df[df['genre'] == genre]['combined_target'], name=genre) for genre in df['genre'].unique()])

    plotly_fig.update_layout(title='Sales Ranking by Genre', xaxis_title='Genre', yaxis_title='Sales Ranking')
    
    return plotly_fig


# Preprocessing
# =============

def preprocessing(df):
    """
    Performs pre-processing on a pandas DataFrame to prepare it for a 
    machine learning model. It combines one-hot encodes the 'genre' column, splits the DataFrame into training and test sets, and scales the resulting 
    features.

    Args:
        df (pd.DataFrame): The DataFrame to process. It's expected to 
        contain the following columns:
            - genre
            - dagger
            - number_of_stars
            - reviews_count
            - combined_target

    Returns:
        X_train columns (list[str]) : the header of each column
        X_train_scaled (np.ndarray): The scaled features for the training set.
        X_test_scaled (np.ndarray): The scaled features for the test set.
        y_train (pd.Series): The target variable for the training set.
        y_test (pd.Series): The target variable for the test set.

    Raises:
        ValueError: If the DataFrame doesn't contain the expected columns.
        TypeError: If the argument provided is not a pandas DataFrame.
    
    """
    # Check if the input is a pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input should be a pandas DataFrame")

    # Check for the expected columns explicitly
    expected_columns = ['genre', 'dagger', 'number_of_stars', 'reviews_count', 'combined_target']
    if not set(expected_columns).issubset(df.columns):
        missing_columns = set(expected_columns) - set(df.columns)
        raise ValueError(f"The DataFrame is missing the following columns: {', '.join(missing_columns)}")

    features = df[['reviews_count', 'number_of_stars', 'dagger', 'genre']]
    target = df['combined_target']

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # One-hot encode the categorical features
    encod = OneHotEncoder( drop="first", sparse=False)    
    categ = ['genre']

    transformed_data_train = encod.fit_transform(X_train[categ])
    transformed_df_train = pd.DataFrame(transformed_data_train, columns=encod.get_feature_names_out(categ), index=X_train.index)
    X_train = pd.concat([X_train.drop(categ, axis=1), transformed_df_train], axis=1)

    transformed_data_test = encod.transform(X_test[categ])
    transformed_df_test = pd.DataFrame(transformed_data_test, columns=encod.get_feature_names_out(categ), index=X_test.index)
    X_test = pd.concat([X_test.drop(categ, axis=1), transformed_df_test], axis=1)

    # Scale the features
    scaler = StandardScaler()                     
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train.columns, X_train_scaled, X_test_scaled, y_train, y_test


# Model ML - regression
# =====================

def regression_model(X_train, X_test, y_train, y_test):
    """
    Trains a GradientBoostingRegressor model on the given training data and evaluates its performance on the test data. It also prints out the mean absolute error for both the training and test sets, and the mean squared error for the test set.

    Args:
        X_train (array-like): The feature matrix for the training set.
        X_test (array-like): The feature matrix for the test set.
        y_train (array-like): The target variable for the training set.
        y_test (array-like): The target variable for the test set.

    Returns:
        reg (Object): A fitted model object. Typically, this could be a fitted instance of a scikit-learn estimator (GradientBoostingRegressor).
        y_pred (array-like): The model's predictions for the test set.
        r2 (float): The R-squared score of the model on the test set.

    Raises:
        ValueError: If the inputs are not as expected (wrong type, shape, 
        etc.).
        
    """
    if not isinstance(X_train, np.ndarray) or not isinstance(X_test, np.ndarray):
        raise ValueError("X_train and X_test should be numpy arrays")

    # Initialize the model
    reg = GradientBoostingRegressor(n_estimators=50, learning_rate=0.2,  max_depth = 3, random_state=42)

    # Fit the model
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    target_predicted = reg.predict(X_train)
    score_train = mean_absolute_error(y_train, target_predicted)
    
    target_predicted = reg.predict(X_test)
    score_test = mean_absolute_error(y_test, target_predicted)
    
    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    
    r2 = r2_score(y_test, y_pred)

    return reg, y_pred, score_train, score_test, mse, r2

# Visualizing results
# ===================

def plot_actual_vs_predicted_values(y_test, y_pred):
    """
    Plots actual values (y_test) against the predicted values (y_pred).

    The function uses plotly.graph_objects's Scatter function to create the plot. 
    The x-axis represents the actual values, and the y-axis represents the predicted values. 
   
    Args:
        y_test (array-like or list): The actual values. These values are expected to be real numbers.
        y_pred (array-like or list): The predicted values, expected to be in line with y_test in terms of shape and content.

    Returns:
        plotly.graph_objects.Figure

    """
    fig = go.Figure(data=[go.Scatter(x=y_test, y=y_pred, mode='markers')])
    
    fig.update_layout(
        title="Actual vs. Predicted Values",
        xaxis_title="Actual Values",
        yaxis_title="Predicted Values"
    )
    
    return fig


def plot_predicted_values_vs_residual(y_test, y_pred):
    """
    Plots predicted values (y_pred) against the residuals (y_test - y_pred).

    This function calculates residuals as the difference between actual and predicted values. It uses plotly.graph_objects's Scatter function to create the plot. The x-axis represents the predicted values, and the y-axis represents the residuals. 

    Args:
        y_test (array-like or list): The actual values. These values are expected to be real numbers.
        y_pred (array-like or list): The predicted values, expected to be in line with y_test in terms of shape and content.

    Returns:
        plotly.graph_objects.Figure

    """
    # Convert input lists to numpy arrays for element-wise operations
    y_test_array = np.array(y_test)
    y_pred_array = np.array(y_pred)

    # Check for mismatched shapes
    if y_test_array.shape != y_pred_array.shape:
        raise ValueError("y_test and y_pred must have the same shape")

    residuals = y_test_array - y_pred_array
    fig = go.Figure(data=[go.Scatter(x=y_pred, y=residuals.tolist(), mode='markers')])

    fig.update_layout(
        title="Predicted vs. Residuals",
        xaxis_title="Predicted Values",
        yaxis_title="Residuals"
    )
    
    return fig


def plot_feature_importances(reg, columns, top_n=7):
    """
    Plots the importance of features as determined by a fitted model.

    The importance of each feature is represented by the length of the bar in the bar chart. Features are sorted in descending order of importance, with the most important feature at the top.

    Args:
        reg (Object): A fitted model object that exposes a `feature_importances_` attribute. Typically, this could be a fitted instance of a scikit-learn estimator like RandomForestRegressor or GradientBoostingRegressor.
        
        columns (list): The names of the features (columns in your dataset), as a list of strings. The order should be the same as the order of feature values fed to the estimator.

        top_n (int): Number of top features to display. Default is 7.

    Raises:
        AttributeError: If `reg` does not have a `feature_importances_` attribute.

    Returns:
        plotly.graph_objects.Figure

    """
    if not hasattr(reg, 'feature_importances_'):
        raise AttributeError("The provided model object does not have a 'feature_importances_' attribute.")
    
    feature_importances = reg.feature_importances_
    sorted_idx = np.argsort(feature_importances)[-top_n:] 

    fig = go.Figure(data=[go.Bar(
        x=feature_importances[sorted_idx],
        y=np.array(columns)[sorted_idx],
        orientation='h'
    )])

    fig.update_layout(
        title=f"Top {top_n} Feature Importances",
        xaxis_title="Importance",
        yaxis_title="Feature"
    )
    
    return fig
