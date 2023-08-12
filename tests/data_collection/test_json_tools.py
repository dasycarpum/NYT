#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-23

@author: Roland

@abstract: create 3 unit tests for the 'json_field_to_list' function in the 'json_tools.py' source file, and 5 test for the 'merge_json_files' function in the same source file
"""

import os
import sys
import pytest
import json
from unittest.mock import mock_open, patch

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src/01_data_collection directory
src_dir = os.path.join(current_script_dir, '../..', 'src', 'data_collection')
# Adding the absolute path to system path
sys.path.append(src_dir)
from json_tools import json_field_to_list, merge_json_files


# Test when the function is given a valid JSON file and a valid field.
def test_json_field_to_list_valid_file_valid_field(mocker):
    mock_json_file = [
        {"title": "Book 1", "url": "https://www.example1.com"},
        {"title": "Book 2", "url": "https://www.example2.com"}
    ]
    mocker.patch('os.path.isfile', return_value=True)
    mocker.patch('builtins.open', new_callable=mock_open, read_data=json.dumps(mock_json_file))

    result = json_field_to_list("dummy.json", "url")
    expected_result = ["https://www.example1.com", "https://www.example2.com"]
    
    assert sorted(result) == sorted(expected_result)


# Test when the function is given a valid JSON file and an invalid field.
def test_json_field_to_list_valid_file_invalid_field(mocker):
    mock_json_file = [
        {"title": "Book 1", "url": "https://www.example1.com"},
        {"title": "Book 2", "url": "https://www.example2.com"}
    ]
    mocker.patch('builtins.open', new_callable=mock_open, read_data=json.dumps(mock_json_file))

    result = json_field_to_list("dummy.json", "invalid_field")

    assert result == []

# Test when the function is given an invalid JSON file.
@patch('os.path.isfile', return_value=False)
def test_json_field_to_list_invalid_file(mock_isfile):
    result = json_field_to_list("non_existent.json", "url")

    assert result == []
    mock_isfile.assert_called_once_with("non_existent.json")


# The test should ensure that the merge_json_files function works correctly with valid input.
def test_merge_json_files_valid_input(tmpdir):
    # Prepare input json files
    data1 = [{"key1": "value1"}, {"key2": "value2"}]
    data2 = [{"key3": "value3"}, {"key4": "value4"}]
    file1 = tmpdir.join("file1.json")
    file1.write(json.dumps(data1))
    file2 = tmpdir.join("file2.json")
    file2.write(json.dumps(data2))

    # Output file
    output_file = str(tmpdir.join("output.json"))

    # Call the function
    merge_json_files(str(tmpdir), output_file)

    # Check if the output file exists
    assert tmpdir.join("output.json").check()

    # Check if the output file has correct data
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == data1 + data2


# The test should test the function's behavior with invalid input.
def test_merge_json_files_invalid_input():
    invalid_json = "[{'not': 'valid json'}]"
    with patch('glob.glob', return_value=['file1.json']), \
        patch('builtins.open', new_callable=mock_open, read_data=invalid_json):
        with pytest.raises(json.JSONDecodeError):
            merge_json_files('file1', 'output.json')


# The test should test if the function is able to handle empty JSON files.
def test_merge_json_files_empty_file():
    empty_json = ""
    with patch('glob.glob', return_value=['file1.json']), \
        patch('builtins.open', new_callable=mock_open, read_data=empty_json):
        with pytest.raises(json.JSONDecodeError):
            merge_json_files('file1', 'output.json')


# Test when there are no matching files
def test_merge_json_files_no_matching_files():
    with patch('glob.glob', return_value=[]), pytest.raises(FileNotFoundError):
        merge_json_files('no_files', 'output.json')


# Test when the output directory does not exist
def test_merge_json_files_nonexistent_output_directory():
    with patch('glob.glob', return_value=['file1.json']), \
        patch('builtins.open', new_callable=mock_open, read_data="[]"), \
        patch('os.path.exists', return_value=False), \
        patch('builtins.open', side_effect=OSError):
        with pytest.raises(OSError):
            merge_json_files('file1', 'nonexistent_directory/output.json')
