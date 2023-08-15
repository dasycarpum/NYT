#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-13

@author: Roland

@abstract: create for the 'book_success.py' source file,
    2 unit tests for the 'sql_query_to_create_dataset' function
    8 unit tests for the 'dataset_cleaning' function
    3 unit tests for the 'target_combination' function

"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock
from sqlalchemy.engine import Engine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objs as go
import plotly.express as px

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'machine_learning')
# Adding the absolute path to system path
sys.path.append(src_dir)
from book_success import sql_query_to_create_dataset, dataset_cleaning, target_combination, create_heatmap, create_3D_scatter, create_box_plot


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


# Sample Data
sample_data = {
    'rating': [',45', '45,', '67'],
    'number_of_stars': [np.nan, '4', '5'],
    'reviews_count': [np.nan, '23', '45'],
    'price': ['$12.45, $15.89', '$10.50', '$5.67'],
    'genre': ['thriller', np.nan, 'fiction'],
    'dagger': [0, 1, 0],
    'asterisk': [0, np.nan, 1],
    'number_of_pages': [np.nan, 300, 200],
    'mean_first_stars': ['3.5', '4.0', np.nan],
    'max_weeks': [12, 15, 20],
    'best_ranking':[1, 11, 24], 
    'id': [1, 2, 3],
    'title': ['Book1', 'Book2', 'Book3'],
    'author': ['Author1', 'Author1', 'Author3']
}

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(sample_data)


def test_dataset_cleaning_structure(sample_dataframe):
    df = dataset_cleaning(sample_dataframe.copy())
    
    # Expected columns after cleaning
    expected_columns = ['rating', 'number_of_stars', 'reviews_count', 'genre', 'dagger', 'asterisk', 'number_of_pages', 'mean_first_stars', 'max_weeks', 'best_ranking', 'author', 'max_price']
    assert list(df.columns) == expected_columns


def test_dataset_cleaning_replace_empty_with_nan(sample_dataframe):
    df = sample_dataframe.copy()
    
    # Set genre at index 0 to an empty string
    df['genre'].iloc[0] = ''
    
    # Clean the dataframe
    cleaned_df = dataset_cleaning(df)
    
    # Check if the value at index 0 is now the mode
    mode_genre = sample_dataframe['genre'].mode()[0]
    assert cleaned_df['genre'].iloc[0] == mode_genre


def test_dataset_cleaning_remove_rows_with_nan(sample_dataframe):
    df = sample_dataframe.copy()
    df['rating'].iloc[0] = np.nan
    df['number_of_stars'].iloc[0] = np.nan
    df['reviews_count'].iloc[0] = np.nan
    cleaned_df = dataset_cleaning(df)
    assert len(cleaned_df) == len(df) - 1


def test_dataset_cleaning_max_price(sample_dataframe):
    df = dataset_cleaning(sample_dataframe.copy())
    assert df['max_price'].iloc[0] == 5.67


def test_dataset_cleaning_rating_replace_comma(sample_dataframe):
    df = dataset_cleaning(sample_dataframe.copy())
    assert df['rating'].iloc[0] == 67


def test_dataset_cleaning_genre_fillna_mode(sample_dataframe):
    df = dataset_cleaning(sample_dataframe.copy())
    mode_genre = sample_dataframe['genre'].mode()[0]
    assert df['genre'].iloc[1] == mode_genre


def test_dataset_cleaning_data_types(sample_dataframe):
    df = dataset_cleaning(sample_dataframe.copy())
    assert df['dagger'].dtype == 'int'
    assert df['rating'].dtype == 'int'
    assert df['genre'].dtype == 'object'
    assert df['author'].dtype == 'object'
    assert df['number_of_stars'].dtype == 'float'
    assert df['number_of_pages'].dtype == 'int'
    assert df['reviews_count'].dtype == 'int'
    assert df['mean_first_stars'].dtype == 'float'
    assert df['best_ranking'].dtype == 'int'
    assert df['max_weeks'].dtype == 'int'


def test_dataset_cleaning_unnecessary_columns(sample_dataframe):
    df = dataset_cleaning(sample_dataframe.copy())
    assert 'id' not in df.columns
    assert 'title' not in df.columns
    assert 'price' not in df.columns


def test_combined_target_column():
    df = pd.DataFrame({
        'best_ranking': [1, 2, 3, 4],
        'max_weeks': [10, 20, 30, 40]
    })
    df_transformed = target_combination(df)
    assert 'combined_target' in df_transformed.columns

def test_keyerror_for_missing_target_columns():
    df1 = pd.DataFrame({'best_ranking': [1, 2, 3, 4]})
    with pytest.raises(KeyError):
        target_combination(df1)

    df2 = pd.DataFrame({'max_weeks': [10, 20, 30, 40]})
    with pytest.raises(KeyError):
        target_combination(df2)

def test_value_transformation():
    df = pd.DataFrame({
        'best_ranking': [1, 2, 3, 4],
        'max_weeks': [10, 20, 30, 40]
    })
    
    # Manually compute the transformed values
    scaler = StandardScaler()
    targets_scaled = scaler.fit_transform(df[['best_ranking', 'max_weeks']])
    pca = PCA(n_components=1)
    targets_pca = pca.fit_transform(targets_scaled)

    df_transformed = target_combination(df)
    
    np.testing.assert_array_almost_equal(df_transformed['combined_target'].values, targets_pca.ravel())


def test_return_type_of_create_heatmap():
    # Test data
    df = pd.DataFrame({
        'combined_target': np.random.randn(10),
        'rating': np.random.randn(10),
        'number_of_stars': np.random.randn(10),
        'number_of_pages': np.random.randn(10),
        'reviews_count': np.random.randn(10),
        'mean_first_stars': np.random.randn(10),
        'max_price': np.random.randn(10)
    })
    result = create_heatmap(df)
    assert isinstance(result, go._figure.Figure), "Expected output type is plotly.graph_objs._figure.Figure"

def test_keyerror_for_missing_columns():
    # Missing 'rating' column
    df = pd.DataFrame({
        'combined_target': np.random.randn(10),
        'number_of_stars': np.random.randn(10),
        'number_of_pages': np.random.randn(10),
        'reviews_count': np.random.randn(10),
        'mean_first_stars': np.random.randn(10),
        'max_price': np.random.randn(10)
    })
    with pytest.raises(KeyError):
        create_heatmap(df)

cols = ['combined_target', 'rating', 'number_of_stars', 'number_of_pages', 'reviews_count', 'mean_first_stars', 'max_price']

def test_heatmap_values_correspond_to_correlation_coefficients():
    # Test data with known correlations
    df = pd.DataFrame({
        'combined_target': np.array([1, 2, 3, 4, 5]),
        'rating': np.array([5, 4, 3, 2, 1]),
        'number_of_stars': np.array([1, 2, 3, 4, 5]),
        'number_of_pages': np.array([2, 4, 6, 8, 10]),
        'reviews_count': np.array([10, 9, 8, 7, 6]),
        'mean_first_stars': np.array([1, 1.5, 2, 2.5, 3]),
        'max_price': np.array([5, 10, 15, 20, 25])
    })
    result = create_heatmap(df)
    correlation_matrix = df[cols].corr()
    # Assert that the heatmap values correspond to the correlation matrix
    assert np.array_equal(result.data[0]['z'], correlation_matrix.values), "Heatmap values don't match correlation coefficients"


def test_return_type_of_create_3D_scatter():
    # Test data
    df = pd.DataFrame({
        'reviews_count': np.random.randn(10),
        'rating': np.random.randn(10),
        'combined_target': np.random.randn(10),
        'dagger': np.random.choice(['yes', 'no'], size=10)
    })
    result = create_3D_scatter(df)
    assert isinstance(result, go._figure.Figure), "Expected output type is plotly.graph_objs._figure.Figure"

def test_valueerror_for_missing_columns():
    # Missing 'rating' column
    df = pd.DataFrame({
        'reviews_count': np.random.randn(10),
        'combined_target': np.random.randn(10),
        'dagger': np.random.choice(['yes', 'no'], size=10)
    })
    with pytest.raises(ValueError):
        create_3D_scatter(df)

def test_scatter_values_correspond_to_dataframe():
    # Test data with known values
    df = pd.DataFrame({
        'reviews_count': np.array([1, 2, 3, 4, 5]),
        'rating': np.array([5, 4, 3, 2, 1]),
        'combined_target': np.array([10, 20, 30, 40, 50]),
        'dagger': [1, 0, 1, 0, 1]
    })
    result = create_3D_scatter(df)
    # Assert that scatter plot values correspond to DataFrame columns
    assert np.array_equal(result.data[0]['x'], df['reviews_count'].values), "x values don't match 'reviews_count' column"
    assert np.array_equal(result.data[0]['y'], df['rating'].values), "y values don't match 'rating' column"
    assert np.array_equal(result.data[0]['z'], df['combined_target'].values), "z values don't match 'combined_target' column"


def test_returns_plotly_figure():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Fantasy', 'Romance'],
        'combined_target': [100, 200, 150]
    })
    
    result = create_box_plot(df)
    assert str(type(result)) == "<class 'plotly.graph_objs._figure.Figure'>", f"Expected Plotly Figure, got {type(result)}"

def test_correct_number_of_box_plots():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Fantasy', 'Sci-Fi', 'Romance', 'Fantasy'],
        'combined_target': [100, 200, 110, 150, 210]
    })
    
    result = create_box_plot(df)
    assert len(result.data) == len(df['genre'].unique()), "Number of box plots doesn't match number of unique genres"

def test_box_plot_data_matches_dataframe():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Fantasy', 'Sci-Fi', 'Romance', 'Fantasy'],
        'combined_target': [100, 200, 110, 150, 210]
    })
    
    result = create_box_plot(df)
    
    for trace in result.data:
        genre = trace.name
        expected_data = df[df['genre'] == genre]['combined_target'].values
        assert np.array_equal(trace['y'], expected_data), f"Data mismatch for genre {genre}"
