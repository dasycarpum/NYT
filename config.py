#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-07-10

@author: Roland

@abstract: shared variables are organized using this file, it includes constants and configurations.
"""

# NYTimes
NYT_api_key = "pNHWGr1vumfKOJ2QwkQHELoH5zbhslrp"

# PostgreSQL
DB_NAME = 'nyt'
DB_USER = 'postgres'
DB_PASS = 'admin'
DB_HOST = 'db'
DB_PORT = '5432'
DB_ENGINE='postgresql://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME

