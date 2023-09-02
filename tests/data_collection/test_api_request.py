#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-22

@author: Roland

@abstract: create 2 unit tests for the 'api_request.py' source file.
"""

import os
import sys
import pytest
import pandas as pd
import requests
import requests_mock
from requests.exceptions import Timeout, RequestException
from unittest.mock import patch
from io import StringIO

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the project root
root_dir = os.path.join(current_script_dir, '../..')
sys.path.append(root_dir)
from config import NYT_api_key
# Constructing the absolute path of the src/data_collection directory
src_dir = os.path.join(root_dir, 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
from api_request import api_request


def test_api_request():
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    api_key = "NYT_api_key_here"

    # Mock valid API response
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, status_code=200, headers={'Content-Type': 'application/json'}, json={"results": [{"id": 1, "name": "Test"}]})
        df = api_request(endpoint, api_key, save=False)
    expected_df = pd.DataFrame([{"id": 1, "name": "Test"}])
    pd.testing.assert_frame_equal(df, expected_df)

    # Mock Timeout
    with requests_mock.Mocker() as m, patch("builtins.print") as mock_print:
        m.get(endpoint + 'api-key=' + api_key, exc=Timeout)
        df = api_request(endpoint, api_key, save=False)
        mock_print.assert_called_with("The request timed out")

    # Mock other RequestException
    with requests_mock.Mocker() as m, patch("builtins.print") as mock_print:
        m.get(endpoint + 'api-key=' + api_key, exc=RequestException("Some request exception"))
        df = api_request(endpoint, api_key, save=False)
        mock_print.assert_called_with("An error occurred: Some request exception")

    # Mock invalid status code
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, status_code=400)
        df = api_request(endpoint, api_key, save=False)
        assert df is None

    # Mock invalid content type
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, status_code=200, headers={'Content-Type': 'text/plain'}, text="Some text")
        df = api_request(endpoint, api_key, save=False)
        assert df is None


def test_api_request_error():
    endpoint = "https://api.nytimes.com/svc/books/v3/lists/names.json?"
    api_key = "NYT_api_key_here"  # Replace this

    # Mock the API response with an error
    with requests_mock.Mocker() as m:
        m.get(endpoint + 'api-key=' + api_key, status_code=500)
        
        # Capture stdout
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout

        df = api_request(endpoint, api_key, save=False)

        # Restore stdout
        sys.stdout = old_stdout
        assert "Failed to get data: 500" in new_stdout.getvalue()

