#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-19

@author: Roland

@abstract: json file manipulation tools

"""

import os
import json
import glob


def json_field_to_list(json_file, field, link_name=None):
    """
    Extracts the values of a specified field from a JSON file and returns them
    as a list.

    Args:
        json_file (str): the name (and path) of the JSON file.
        field (str): the name of the field to extract values from.
        link_name (str) : the name of a secondary dictionary 

    Returns:
        list: A list of the values of the specified field in the JSON file.
        
    Example:
        >>> field_values_of_JSON_file('example.json', 'url')
        ['https://www.example1.com', 'https://www.example2.com', ...]
    
    """
    # Opening a JSON file containing the field
    if os.path.isfile(json_file):
        try:
            with open(json_file, "r", encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {json_file}")
            return []
    else:
        print(f"Error: File not found: {json_file}")
        return []

    # Iterating through the JSON list and create a list
    list_of_field_values = []
    for row in data:
        if field in row:
            if isinstance(row[field], list) and link_name:
                # Handle fields which are lists of objects
                for link in row[field]:
                    if link['name'] == link_name:
                        list_of_field_values.append(link['url'])
            else:
                # Handle fields which are strings
                list_of_field_values.append(row[field])

    return list(set(list_of_field_values))


def merge_json_files(input_files, output_file):
    """
    Merges multiple JSON files into one, where each file contains data for a 
    single item.

    The function reads all the JSON files in the specified directory that match
    the pattern "xxx_*.json", where the asterisk is a wildcard that matches 
    any number of characters. The contents of these files are merged into a
    single list, which is then written to a single JSON file.

    Args:
        input_files (str) : path of the files to merge
        output_file (str) : output name of merged files

    Returns:
        None.
   
    """
    result = []
    matching_files = glob.glob(os.path.join(input_files, "*.json"))

    # Raise an error if no files were found
    if not matching_files:
        raise FileNotFoundError(f"No files matching {input_files + '.json'} were found")

    for f in matching_files:
        with open(f, "r", encoding="utf-8") as infile:
            data = json.load(infile)
            for item in data:
                result.append(item)

    dir_name = os.path.dirname(output_file)
    if dir_name and not os.path.exists(dir_name):
        raise FileNotFoundError(f"Directory {dir_name} does not exist")

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(result, outfile)
