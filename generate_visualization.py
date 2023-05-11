#! /usr/bin/env python3

import plotly.express as px

from dash import Dash, dcc, html, Input, Output

import pandas as pd

from db import get_node_coords

import config


app = Dash(__name__)

app.layout = html.Div(children=[

    html.H1(children='ITDK'),

    dcc.RadioItems(
        id="itdk_version",
        options=["midar-iff-2022-02"],
        value="midar-iff-2022-02",
        inline=True
    ),

    dcc.Graph(id='topo-map')

])


@app.callback(
    Output(component_id='topo-map', component_property='figure'),
    Input(component_id='itdk_version', component_property='value')
)
def update_topo_map(itdk_version):
    #node_coords = pd.DataFrame(get_node_coords("/home/allison/Desktop/ITDK/" + itdk_version + "-itdk.db"), columns=['node_id','latitude','longitude'])
    node_ids = ["N1", "N2", "N3", "N4", "N5"]
    latitudes = [0, -25, 25, -50]
    longitudes = [30, -30, 90, -100]
    node_coords = pd.DataFrame(list(zip(node_ids, latitudes, longitudes)), columns=['node_id','latitude','longitude'])

    fig = px.scatter_geo(lat=node_coords['latitude'], lon=node_coords['longitude'], text=node_coords['node_id'])

    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}
        )
    
    return fig


# view in browser at http://127.0.0.1:8050/
if __name__ == '__main__':
    app.run_server(debug=True)