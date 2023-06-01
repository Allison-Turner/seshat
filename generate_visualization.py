#! /usr/bin/env python3

import config

from db import get_all_node_coords, get_node_coords, get_links, get_geo_links, fetch_top_nodes, find_num_geo_nodes, find_num_non_geo_nodes, get_links_for_node, get_geo_links_for_node, get_meta_table_rows_for_node_ids

from glob import glob
import os, sys, json
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
import pandas as pd
import dash_cytoscape


css_colors = ['Aqua', 'Aquamarine', 'Blue', 'Indigo', 'Brown', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Crimson', 'Blue', 'GoldenRod', 'Green', 'Magenta', 'Gold', 'FireBrick', 'Fuchsia', 'DodgerBlue', 'DeepSkyBlue', 'DarkTurquoise', 'GreenYellow', 'IndianRed', 'LightGreen', 'Magenta', 'Maroon', 'Lime', 'Navy', 'Olive', 'Orange', 'OrangeRed', 'Orchid', 'Pink', 'Plum', 'Purple', 'Red', 'Yellow', 'Teal', 'YellowGreen']


itdk_dbs = glob(config.ITDK_DB_DIR + "*-itdk.db")

itdk_versions = [""] + [os.path.basename(itdk_vsn).replace("-itdk.db", "") for itdk_vsn in itdk_dbs]

styles = {
    'container': {
        'display': 'grid',
        'grid-template-rows': '1fr',
        'grid-template-columns': '1fr 1fr 4fr'
    },
    'pre': {
        'overflowX': 'wrap'
    }
}

app = Dash(__name__)

app.layout = html.Div(children=[

    html.H1(children='ITDK'),

    dcc.Checklist(
        id="itdk_versions",
        options=itdk_versions,
        value=[itdk_versions[0]],
        inline=True
    ),

    html.Details(children=[
        """
        MIDAR and Speedtrap are internet measurement techniques for something called 'alias resolution'. 'Alias resolution' describes the process of determining which router addresses are actually interfaces of the same router, which gives us a dataset that more accurately represents real-world internet infrastructure.The most accurate datasets result from combining MIDAR or Speedtrap with Kapar or Iffinder.

        The important difference between MIDAR and Speedtrap themselves is that MIDAR is used for IPv4, and Speedtrap is used for IPv6.
        """,
        html.Br(),html.Br(),
        "For more information, check out these resources from CAIDA:",
        html.Br(),
        html.A(href="https://www.caida.org/catalog/datasets/internet-topology-data-kit/",children=["Macroscopic Internet Topology Data Kit (ITDK)"]),
        html.Br(),
        html.A(href="https://www.caida.org/catalog/software/midar/", children=["Monotonic ID-based Alias Resolution (MIDAR)"]),
        html.Br(),
        html.A(href="https://www.caida.org/catalog/software/kapar/", children=["kapar"]),
        html.Br(),
        html.A(href="https://www.caida.org/catalog/software/iffinder/", children=["iffinder"]),
        html.Br(),
        html.A(href="https://catalog.caida.org/paper/2013_speedtrap", children=["Speedtrap"]),
        html.Summary(children=["What do 'midar' and 'speedtrap' mean?"])
    ]),

    dcc.Slider(0, 1000000, 5000, value=5000, id='num_nodes', marks={0:'0', 100000:'100,000', 200000:'200,000', 300000:'300,000', 400000:'400,000', 500000:'500,000', 600000:'600,000', 700000:'700,000', 800000:'800,000', 900000:'900,000', 1000000:'1,000,000'}),

    dcc.Graph(id='topo-map'),

    dcc.Dropdown(['node_outdegree', 'org_name', 'no data coloring'], 'no data coloring', id='color_by'),

    html.P(id="context-label"),

    html.Div(className='container', style=styles['container'], children=[
        html.Pre(id='selected_node_data', style=styles['pre'], className='item'),
        html.Pre(id='interface_addrs', style=styles['pre'], className='item'),
        html.Div(id='connected_asns',className='item'),
    ]),

])


@app.callback(
        [
            Output(component_id='topo-map', component_property='figure'),
            Output(component_id='context-label', component_property='children')
        ],
        [
            Input(component_id='itdk_versions', component_property='value'),
            Input(component_id='color_by', component_property='value'),
            Input(component_id='num_nodes', component_property='value')
        ]
)
def update_topo_map(itdk_versions, color_by, num_nodes):
    total_pts_displayed = 0
    num_geo_nodes = 0
    num_non_geo_nodes = 0

    min_outdegree = sys.maxsize * 2 + 1
    max_outdegree = -sys.maxsize - 1


    for itdk_vsn in itdk_versions:
        db_file = config.ITDK_DB_DIR + itdk_vsn + "-itdk.db"

        node_ids, outdegrees, asns, org_names, lats, longs = fetch_top_nodes(db_file, num_nodes)

        total_pts_displayed += len(node_ids)

        data_src = [db_file] * total_pts_displayed

        node_sample_df = pd.DataFrame({
            'node_id': node_ids,
            'outdegree': outdegrees,
            'asn': asns,
            'org_name': org_names,
            'latitude': lats,
            'longitude': longs,
            'data_src': data_src
        })

        num_geo_nodes += find_num_geo_nodes(db_file)
        num_non_geo_nodes += find_num_non_geo_nodes(db_file)

        if color_by == "no data coloring":
            fig = px.scatter_mapbox(
                data_frame=node_sample_df,
                lat='latitude', 
                lon='longitude', 
                hover_name='node_id',
                custom_data=['node_id', 'outdegree', 'asn', 'org_name', 'data_src']
                )            
        elif color_by == "node_outdegree":
            fig = px.scatter_mapbox(
                data_frame=node_sample_df,
                lat='latitude', 
                lon='longitude', 
                hover_name='node_id',
                custom_data=['node_id', 'outdegree', 'asn', 'org_name', 'data_src'],
                color='outdegree',
                color_continuous_scale='viridis'
                )
        elif color_by == "org_name":
            orgs = node_sample_df.org_name.unique()

            fig = px.scatter_mapbox(
                data_frame=node_sample_df,
                lat='latitude', 
                lon='longitude', 
                hover_name='node_id',
                custom_data=['node_id', 'outdegree', 'asn', 'org_name', 'data_src'],
                color='org_name',
                color_discrete_sequence=css_colors[:len(orgs)]
                )


        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_layout(showlegend=False)

    return fig, "{:,} nodes displayed out of {:,} mappable nodes, {:,} nodes not displayable on a map".format(total_pts_displayed, num_geo_nodes, num_non_geo_nodes)



@app.callback(
    [
        Output(component_id='selected_node_data', component_property='children'),
        Output(component_id='interface_addrs', component_property='children'),
        Output(component_id='connected_asns', component_property='children'),
     ],
    Input('topo-map', 'clickData'))
def display_click_data(clickData):
    if clickData is not None:
        node_data = clickData['points'][0]['customdata']
        node_id = node_data[0]
        outdegree = node_data[1]
        asn = node_data[2]
        org_name = node_data[3]
        data_src = node_data[4]

        #link_ids, node_ids_1, lat_1, long_1, addrs_1, node_ids_2, addrs_2, lat_2, long_2 = get_geo_links_for_node(data_src, node_id)
        """
        links_df = pd.DataFrame({
            'link_id': link_ids,
            'node_id_1': node_ids_1,
            'addr_1': addrs_1,
            'lat_1': lat_1,
            'long_1': long_1,
            'node_id_2': node_ids_2,
            'addr_2': addrs_2,
            'lat_2': lat_2,
            'long_2': long_2
        })"""
        link_ids, node_ids_1, addrs_1, node_ids_2, addrs_2 = get_links_for_node(data_src, node_id)

        links_df = pd.DataFrame({
            'link_id': link_ids,
            'node_id_1': node_ids_1,
            'addr_1': addrs_1,
            'node_id_2': node_ids_2,
            'addr_2': addrs_2,
        })

        nodes = links_df.node_id_2.unique().tolist()
        addrs = links_df.addr_1.unique().tolist()
        r_node_ids, outdegrees, as_numbers, org_names, latitudes, longitudes = get_meta_table_rows_for_node_ids(data_src, nodes)
        neighbors_df = pd.DataFrame({
            'node_id': r_node_ids,
            'outdegree': outdegrees,
            'as_number': as_numbers,
            'org_name': org_names,
            'latitude': latitudes,
            'longitude': longitudes
        })

        return "Node ID: {}\nOutdegree: {}\nASN: {}\nOrg Name: {}".format(node_id, outdegree, asn, org_name), "\n".join(addrs), dash_table.DataTable(id="table", data=neighbors_df.to_dict('records'), columns=[{'id': c, 'name': c, } for c in neighbors_df])

    else:
        return "", "", ""


# view in browser at http://127.0.0.1:8050/
if __name__ == '__main__':
    app.run_server(debug=True)

