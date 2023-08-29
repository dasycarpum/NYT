#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-13

@author: Roland

@abstract: the aim of this part of the application is to use the "nyt" database to learn patterns and predict certain events. The results are displayed in a dashboard.

"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Getting the absolute path of the current script file
current_script_path = os.path.abspath(__file__)
# Getting the directory of the current script file
current_script_dir = os.path.dirname(current_script_path)
# Constructing the absolute path of the src directory
src_dir = os.path.join(current_script_dir, '../..')
# Adding the absolute path to system path
sys.path.append(src_dir)
from config import DB_ENGINE
from src.machine_learning.book_success import sql_query_to_create_dataset, dataset_cleaning, target_combination, create_3D_scatter, create_heatmap, create_box_plot, preprocessing, regression_model, plot_actual_vs_predicted_values, plot_feature_importances, plot_predicted_values_vs_residual



def get_data_from_database():
    try:
        # Attempt to create the database engine
        engine = create_engine(DB_ENGINE)
    except Exception as e:
        raise RuntimeError(f"Failed to create database engine: {e}")

    try:
        # Attempt to fetch data
        df_raw = sql_query_to_create_dataset(engine)
        
        # Check if the DataFrame is empty
        if df_raw.empty:
            raise ValueError("Fetched dataset is empty.")
            
        return df_raw
    
    except SQLAlchemyError as e:
        # Specific handling for SQLAlchemy errors
        raise RuntimeError(f"SQLAlchemy error occurred: {e}")
    except Exception as e:
        # General error handling
        raise RuntimeError(f"Failed to fetch dataset: {e}")



def main():
    """
    Main function that initializes and runs a regression model and displays the results in a dashboard.
    
    This function does the following:
    1. Connects to the database and fetches the dataset.
    2. Performs data cleaning and transformation.
    3. Creates visualizations for variables.
    4. Conducts preprocessing and trains a regression model.
    5. Plots some result indicators
    6. Sets up and runs the Dash application.

    Args:
        None

    Returns:
        None

    """
    # 1.Create a SQLAlchemy engine that will interface with the database and fetch the raw dataset
    df_raw = get_data_from_database()
    
    # 2. Perform data cleaning and transformation.
    df_cleaned =  dataset_cleaning(df_raw)
    df_complete = target_combination(df_cleaned)

    # 3. Create visualizations for variables.
    var_3D_scatter_fig = create_3D_scatter(df_complete)
    var_heatmap_fig = create_heatmap(df_complete)
    var_box_plot_fig = create_box_plot(df_complete)

    # 4. Conduct preprocessing and train regression model.
    columns, X_train, X_test, y_train, y_test = preprocessing(df_complete)
    reg, y_pred, score_train, score_test, mse, r2 = regression_model(X_train, X_test, y_train, y_test)

    # 5. Plot some result indicators
    pred_val_fig_1 = plot_actual_vs_predicted_values(y_test, y_pred)
    pred_val_fig_2 = plot_predicted_values_vs_residual(y_test, y_pred)
    feat_imp_fig = plot_feature_importances(reg, columns)

    # 6. Set up and run the Dash application.
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='Variable preview', value='tab-1'),
            dcc.Tab(label='Predicted values', value='tab-2'),
            dcc.Tab(label='Model evaluation', value='tab-3'),
        ]),
        html.Div(id='tabs-example-content')
    ])

    @app.callback(Output('tabs-example-content', 'children'),
                  Input('tabs-example', 'value'))
    def render_content(tab):
        if tab == 'tab-1':
            return html.Div([
                html.Div([  # This is a container Div
                    html.Div([dcc.Graph(figure=var_heatmap_fig)], style={'width': '50%', 'display': 'inline-block'}),  # side-by-side divs
                    html.Div([dcc.Graph(figure=var_3D_scatter_fig)], style={'width': '50%', 'display': 'inline-block'})  # side-by-side divs
                ]),
                html.Div([dcc.Graph(figure=var_box_plot_fig)])  # below div
            ])
        elif tab == 'tab-2':
            return html.Div([
                html.Div([  # This is a container Div
                    html.Div([dcc.Graph(figure=pred_val_fig_1)], style={'width': '50%', 'display': 'inline-block'}),  # side-by-side divs
                    html.Div([dcc.Graph(figure=pred_val_fig_2)], style={'width': '50%', 'display': 'inline-block'})  # side-by-side divs
                ])
            ])
        elif tab == 'tab-3':
            return html.Div([
                html.H4("Main metrics", style={'textAlign': 'center'}),  # Title for the section
                html.Div(  # This Div centers its children
                    dash_table.DataTable(
                        columns=[
                            {"name": "Metric", "id": "Metric"},
                            {"name": "Value", "id": "Value"},
                            {"name": "Comment", "id": "Comment"},
                        ],
                        data=[
                            {"Metric": "Training error", "Value": f"{score_train:.2f}", "Comment": "Error from training data"},
                            {"Metric": "Testing error", "Value": f"{score_test:.2f}", "Comment": "Error from testing data"},
                            {"Metric": "MSE", "Value": f"{mse:.4f}", "Comment": "Mean squared error on test set"},
                            {"Metric": "R² score", "Value": f"{r2:.4f}", "Comment": "R² score on the test set"}
                        ],
                        style_table={'width': '50%', 'marginLeft': '25%', 'marginRight': '25%'}  # This centers the table by setting left and right margins to 25%
                    ),
                    style={'textAlign': 'center'}
                ),
                html.Div([dcc.Graph(figure=feat_imp_fig)], style={'marginTop': 20})  # Displaying feature importance below the metrics
            ])

    app.run_server(debug=True, host='0.0.0.0', port=8050)


if __name__ == "__main__":
    main()
