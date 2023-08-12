#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-18

@author: Roland

@abstract: convert api request results into usable table data
"""

import requests
import pandas as pd



def api_request(endpoint, api_key, save=False):
    """
    The function begins by making a GET request to the specified endpoint and returning the JSON response data. It uses the requests library to make the request and .json() to parse the response into a JSON object. It then extracts the results key from the response JSON and normalizes it using the pd.json_normalize() function.

    If the save flag is True, it saves the resulting data to a CSV file in the data folder named results.csv. Finally, it returns the normalized results data as a pandas DataFrame.

    Args:
        endpoint (str): This is a URL endpoint that the API request will be made to.
        api_key (str): This is a string representing the user's API key.
        save (bool): This is a boolean flag that, if True, will save the results to a CSV file.

    Returns:
        pandas DataFrame : normalized results data
    """
    response = requests.get(endpoint + 'api-key=' + api_key, timeout=5).json()

    try:
        json_results = response['results']
        df_results = pd.json_normalize(json_results)

        if save:
            df_results.to_csv('../../data/raw_data/api_results.csv', index=False) 

        return df_results
    except KeyError as e:
        print(f"The key {e} does not exist in the response.")
        return None
