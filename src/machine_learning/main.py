#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-13

@author: Roland

@abstract: the aim of this part of the application is to use the "nyt" database to learn patterns and predict certain events.

"""

import os
import sys
from sqlalchemy import create_engine
import dash
import dash_core_components as dcc
import dash_html_components as html
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
from src.machine_learning.book_success import sql_query_to_create_dataset, dataset_cleaning, target_combination, create_3D_scatter, create_heatmap, create_box_plot, preprocessing, regression_model



def main():
   
    # Create a SQLAlchemy engine that will interface with the database.
    engine = create_engine(DB_ENGINE)

    df_raw = sql_query_to_create_dataset(engine)
    df_cleaned =  dataset_cleaning(df_raw)
    df_complete = target_combination(df_cleaned)

    var_3D_scatter_fig = create_3D_scatter(df_complete)
    var_heatmap_fig = create_heatmap(df_complete)
    var_box_plot_fig = create_box_plot(df_complete)

    columns, X_train, X_test, y_train, y_test = preprocessing(df_complete)
    reg, y_pred, r2 = regression_model(X_train, X_test, y_train, y_test)

    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='Variable preview', value='tab-1'),
            dcc.Tab(label='2', value='tab-2'),
            dcc.Tab(label='3', value='tab-3'),
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
            return html.Div([])  # Empty for now
        elif tab == 'tab-3':
            return html.Div([])  # Empty for now

    app.run_server(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    main()
