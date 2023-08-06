#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-22

@author: Roland

@abstract: create 4 unit tests for the 'api_request.py' source file.
"""

import os
import sys
import pytest
import pandas as pd
import requests
import requests_mock

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
from api_request import api_request


NYT_api_key = "pNHWGr1vumfKOJ2QwkQHELoH5zbhslrp"


def test_api_request():
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    api_key = NYT_api_key

    # Mock the API response
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, json={"results": [{"id": 1, "name": "Test"}]})
        
        # Call the function and get the result
        df = api_request(endpoint, api_key, save=False)

    # The expected result
    expected_df = pd.DataFrame([{"id": 1, "name": "Test"}])

    # Check that the returned DataFrame matches the expected result
    pd.testing.assert_frame_equal(df, expected_df)

def test_api_request_error():
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    api_key = NYT_api_key

    # Mock the API response with an error
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, status_code=500)

        # Call the function and get the result
        with pytest.raises(requests.exceptions.RequestException):
            df = api_request(endpoint, api_key, save=False)

def test_api_request_missing_keys():
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    api_key = NYT_api_key

    # Mock the API response without 'results' key
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, json={"invalid_key": [{"id": 1, "name": "Test"}]})
        
        # Call the function and get the result
        df = api_request(endpoint, api_key, save=False)

        # Should return None due to missing 'results' key
        assert df is None

def test_api_request_save():
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    api_key = NYT_api_key

    # Create directories if they don't exist
    os.makedirs('../../data/raw_data', exist_ok=True)

    # Mock the API response
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, json={"results": [{"id": 1, "name": "Test"}]})
        
        # Call the function and get the result with save=True
        df = api_request(endpoint, api_key, save=True)

    # The expected result
    expected_df = pd.DataFrame([{"id": 1, "name": "Test"}])

    # Check that the returned DataFrame matches the expected result
    pd.testing.assert_frame_equal(df, expected_df)

    # Check that the file was saved correctly
    saved_df = pd.read_csv('../../data/raw_data/api_results.csv')

    pd.testing.assert_frame_equal(saved_df, expected_df)

    # Cleanup: Remove the saved file after test
    os.remove('../../data/raw_data/api_results.csv')
