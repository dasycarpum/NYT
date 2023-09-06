#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-10

@author: Roland

@abstract: shared variables are organized using this file, it includes constants and configurations.
"""

import os

# NYTimes
NYT_api_key = os.environ.get('NYT_API_KEY')

# PostgreSQL
DB_NAME = 'nyt'
DB_USER = 'postgres'
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = 'postgres-service'
DB_PORT = '5432'
DB_ENGINE='postgresql://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME

# Data paths
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))
RAW_DATA_ABS_PATH = os.path.join(PARENT_DIR, 'data', 'raw_data', '')
PROC_DATA_ABS_PATH = os.path.join(PARENT_DIR, 'data', 'processed_data', '')
