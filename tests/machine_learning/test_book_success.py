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

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'machine_learning')
# Adding the absolute path to system path
sys.path.append(src_dir)
from book_success import sql_query_to_create_dataset, dataset_cleaning, target_combination


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


