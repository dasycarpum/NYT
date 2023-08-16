#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-13

@author: Roland

@abstract: create for the 'book_success.py' source file,
    2 unit tests for the 'sql_query_to_create_dataset' function
    8 unit tests for the 'dataset_cleaning' function
    3 unit tests for the 'target_combination' function
    9 unit tests for the variable previews (3 functions)
    5 unit tests for the 'preprocessing' function
    3 unit tests for the 'regression_model' function
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from sqlalchemy.engine import Engine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
import plotly.graph_objs as go

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'machine_learning')
# Adding the absolute path to system path
sys.path.append(src_dir)
from book_success import sql_query_to_create_dataset, dataset_cleaning, target_combination, create_heatmap, create_3D_scatter, create_box_plot, preprocessing, regression_model


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


def test_missing_columns_raises_error():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Fantasy'],
        'dagger': [1, 0],
        'number_of_stars': [4, 5],
        'reviews_count': [100, 50]
        # 'combined_target' column is missing
    })
    
    with pytest.raises(ValueError, match="The DataFrame is missing the following columns: combined_target"):
        preprocessing(df)


def test_non_dataframe_input_raises_error():
    data = [
        ('Sci-Fi', 1, 4, 100, 150),
        ('Romance', 0, 5, 50, 100)
    ]

    with pytest.raises(TypeError):
        preprocessing(data)


def test_output_shapes_match_expected():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Romance', 'Romance', 'Thriller'],
        'dagger': [1, 0, 1, 0],
        'number_of_stars': [4, 5, 4, 3],
        'reviews_count': [100, 50, 60, 120],
        'combined_target': [150, 100, 110, 140]
    })
    
    columns, X_train_scaled, X_test_scaled, y_train, y_test = preprocessing(df)
    
    assert X_train_scaled.shape[0] == y_train.shape[0], "Training data and labels size mismatch"
    assert X_test_scaled.shape[0] == y_test.shape[0], "Test data and labels size mismatch"


def test_encoded_columns_match():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Sci-Fi', 'Romance', 'Thriller'],
        'dagger': [1, 0, 1, 0],
        'number_of_stars': [4, 5, 4, 3],
        'reviews_count': [100, 50, 60, 120],
        'combined_target': [150, 100, 110, 140]
    })
    
    columns, _, _, _, _ = preprocessing(df)
    
    # Check if the 'genre' column has been one-hot encoded
    assert 'genre_Sci-Fi' in columns
    assert 'genre_Thriller' in columns
    assert 'genre_Thriller' in columns


def test_scaling():
    df = pd.DataFrame({
        'genre': ['Sci-Fi', 'Romance', 'Romance', 'Thriller'],
        'dagger': [1, 0, 1, 0],
        'number_of_stars': [4, 5, 4, 3],
        'reviews_count': [100, 50, 60, 120],
        'combined_target': [150, 100, 110, 140]
    })
    
    columns, X_train_scaled, _, _, _ = preprocessing(df)
    
    # Check if mean is approximately 0 and standard deviation is approximately 1 for scaled training data
    assert np.isclose(X_train_scaled.mean(axis=0), 0).all(), "Means are not close to 0"
    assert np.isclose(X_train_scaled.std(axis=0), 1).all(), "Standard deviations are not close to 1"


def test_input_type():
    X_train, X_test = np.array([[1], [2], [3]]), np.array([[4], [5], [6]])
    y_train, y_test = np.array([1, 2, 3]), np.array([4, 5, 6])

    # Ensure it doesn't raise an error with correct input
    try:
        regression_model(X_train, X_test, y_train, y_test)
    except ValueError:
        pytest.fail("ValueError was raised with valid input")

    # Ensure it raises an error with invalid input
    with pytest.raises(ValueError):
        regression_model(X_train.tolist(), X_test, y_train, y_test)


def test_model_output():
    X_train = np.array([[i] for i in range(1, 11)])  
    X_test = np.array([[i] for i in range(11, 16)])
    y_train = np.array([i*1.1 + np.random.normal(0, 0.1) for i in range(1, 11)])
    y_test = np.array([i*1.1 + np.random.normal(0, 0.1) for i in range(11, 16)])

    reg, y_pred, r2 = regression_model(X_train, X_test, y_train, y_test)
    
    assert isinstance(reg, GradientBoostingRegressor)
    assert len(y_pred) == len(X_test)
    assert not np.isnan(r2)


def test_r2_score_range():
    X_train = np.array([[i] for i in range(1, 1001)])  # Train on more data
    X_test = np.array([[i] for i in range(101, 1051)])
    
    y_train = np.array([i*1.1 for i in range(1, 1001)])  # No noise
    y_test = np.array([i*1.1 for i in range(101, 1051)])
    
    _, _, r2 = regression_model(X_train, X_test, y_train, y_test)
    
    assert -1 <= r2 <= 1


