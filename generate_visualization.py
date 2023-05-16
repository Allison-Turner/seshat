#! /usr/bin/env python3

import config

from db import get_all_node_coords, get_node_coords, get_links

from glob import glob
import os
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import pandas as pd


itdk_dbs = glob(config.DB_DIR + "*-itdk.db")

itdk_versions = [os.path.basename(itdk_vsn).replace("-itdk.db", "") for itdk_vsn in itdk_dbs]

app = Dash(__name__)

app.layout = html.Div(children=[

    html.H1(children='ITDK'),

    dcc.Checklist(
        id="itdk_versions",
        options=itdk_versions,
        value=[itdk_versions[0]],
        inline=True
    ),

    dcc.Graph(id='topo-map')

])


@app.callback(
    Output(component_id='topo-map', component_property='figure'),
    Input(component_id='itdk_versions', component_property='value')
)
def update_topo_map(itdk_versions):
    for itdk_vsn in itdk_versions:
        #node_coords = pd.DataFrame(list(zip(get_all_node_coords(config.DB_DIR + itdk_vsn + "-itdk.db"))), columns=['node_id','latitude','longitude'])
        node_ids = ["N1", "N2", "N3", "N4", "N5"]
        latitudes = [0, -25, 25, -50, 75]
        longitudes = [30, -30, 90, -100, 110]
        node_lat_dict = {}
        node_long_dict = {}

        for i in range(len(node_ids)):
            node_lat_dict[node_ids[i]] = latitudes[i]
            node_long_dict[node_ids[i]] = longitudes[i]

        node_coords = list(zip(node_ids, latitudes, longitudes))
        node_coords_df = pd.DataFrame(node_coords, columns=['node_id','latitude','longitude'])

        fig = px.scatter_geo(lat=node_coords_df['latitude'], lon=node_coords_df['longitude'], hover_name=node_coords_df['node_id'])

        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0}
            )
    
        link_ids, node_ids_1, addrs_1, node_ids_2, addrs_2 = get_links(config.DB_DIR + itdk_vsn + "-itdk.db")

        node_1_lats = []
        node_1_longs = []
        node_2_lats = []
        node_2_longs = []

        for row_num in range(len(link_ids)):
            #node_id_1 = node_ids_1[row_num]
            #node_id_2 = node_ids_2[row_num]
            if node_ids_1[row_num] in node_lat_dict.keys() and node_ids_2[row_num] in node_lat_dict.keys():
                lat_1 = node_lat_dict[node_ids_1[row_num]]
                lat_2 = node_long_dict[node_ids_1[row_num]]
                long_1 = node_lat_dict[node_ids_2[row_num]]
                long_2 = node_long_dict[node_ids_2[row_num]]
            else:
                lat_1 = None
                lat_2 = None
                long_1 = None
                long_2 = None

            """
            for i in range(len(node_ids)):
                if node_ids[i] == node_id_1:
                    lat_1 = latitudes[i]
                    long_1 = longitudes[i]

                if node_ids[i] == node_id_2:
                    lat_2 = latitudes[i]
                    long_2 = longitudes[i]
            
            result_1 = get_node_coords(config.DB_DIR + itdk_vsn + "-itdk.db", node_id_1)

            if result_1 is not None:
                lat_1 = result_1[0]
                long_1 = result_1[1]
            else:
                continue

            result_2 = get_node_coords(config.DB_DIR + itdk_vsn + "-itdk.db", node_id_2)

            if result_2 is not None:
                lat_2 = result_2[0]
                long_2 = result_2[1]
            else:
                continue
            """
            node_1_lats.append(lat_1)
            node_1_longs.append(long_1)

            node_2_lats.append(lat_2)
            node_2_longs.append(long_2)

        links_geo_df = pd.DataFrame(list(zip(link_ids, node_ids_1, addrs_1, node_1_lats, node_1_longs, node_ids_2, addrs_2, node_2_lats, node_2_longs)), columns=['link_id', 'node_id_1', 'address_1', 'lat_1', 'long_1', 'node_id_2', 'address_2', 'lat_2', 'long_2'])

        for i in range(len(links_geo_df)):

            fig.add_trace(go.Scattergeo(
                lon = [links_geo_df['long_1'][i], links_geo_df['long_2'][i]],
                lat = [links_geo_df['lat_1'][i], links_geo_df['lat_2'][i]],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
            ))

    return fig


# view in browser at http://127.0.0.1:8050/
if __name__ == '__main__':
    app.run_server(debug=True)