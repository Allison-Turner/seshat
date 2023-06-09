#! /usr/bin/env python3


from glob import glob
import os, sys
#import json
import plotly.express as px
#import plotly.graph_objects as go
#import dash
from dash import Dash, dcc, html, Input, Output, dash_table, register_page, callback
import pandas as pd
#import dash_cytoscape

register_page(__name__, path='/', name='Home')

layout = html.Div("TODO")