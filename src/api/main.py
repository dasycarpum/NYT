#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-08

@author: Roland

@abstract: The aim of this part of the application is to use the "nyt" database to allow the user to query it via an API. The results will be returned in the form of a JSON file.
"""

import os
import sys
from fastapi import FastAPI
from sqlalchemy import create_engine
from typing import List

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
# from config import DB_ENGINE
from src.api.best_book import read_all_genres, read_best_books

DB_NAME = 'nyt'
DB_USER = 'postgres'
DB_PASS = 'admin'
DB_HOST = 'db'
DB_PORT = '5432'
DB_ENGINE='postgresql://'+DB_USER+':'+DB_PASS+'@'+DB_HOST+':'+DB_PORT+'/'+DB_NAME

try:
    # Attempt to create the database engine
    engine = create_engine(DB_ENGINE)
except Exception as e:
    raise RuntimeError(f"Failed to create database engine: {e}")

app = FastAPI()

@app.get("/status")
async def read_status():
    """
    Check the health and functionality of the API.

    Args: None
        
    Returns:
        dict: a dictionary with "status": "ok" if the API is healthy
    """
    return {"status": "OK"}

@app.get("/all_genres", response_model=List[str], summary="List of all genres")
async def read_all_genres_route():
    return await read_all_genres(engine, app)

@app.get("/best_book", summary="The 5 best books by year and genre") 
async def read_best_books_route(year: str, genre: str):
    return await read_best_books(engine, app, year, genre)