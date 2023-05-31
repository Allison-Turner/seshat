#! /usr/bin/env python3

import config

from db import get_all_node_coords, get_node_coords, get_links, get_geo_links, fetch_top_nodes, find_num_geo_nodes, find_num_non_geo_nodes, get_links_for_node, get_geo_links_for_node

from glob import glob
import os, sys, json
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
import pandas as pd
import dash_cytoscape


css_colors = ['Aqua', 'Aquamarine', 'Blue', 'Indigo', 'Brown', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Crimson', 'Blue', 'GoldenRod', 'Green', 'Magenta', 'Gold', 'FireBrick', 'Fuchsia', 'DodgerBlue', 'DeepSkyBlue', 'DarkTurquoise', 'GreenYellow', 'IndianRed', 'LightGreen', 'Magenta', 'Maroon', 'Lime', 'Navy', 'Olive', 'Orange', 'OrangeRed', 'Orchid', 'Pink', 'Plum', 'Purple', 'Red', 'Yellow', 'Teal', 'YellowGreen']


itdk_dbs = glob(config.ITDK_DB_DIR + "*-itdk.db")

itdk_versions = [os.path.basename(itdk_vsn).replace("-itdk.db", "") for itdk_vsn in itdk_dbs]

#top_nodes_df = pd.read_csv(config.DB_DIR + "top-outdegree." + "midar-iff-2022-02" + ".txt", header=None, names=["node_id","outdegree","asn","org_name","latitude","longitude"])

app = Dash(__name__)

app.layout = html.Div(children=[

    html.H1(children='ITDK'),

    dcc.Checklist(
        id="itdk_versions",
        options=itdk_versions,
        value=[itdk_versions[0]],
        inline=True
    ),

    dcc.Slider(0, 1000000, 5000, value=5000, id='num_nodes', marks={0:'0', 100000:'100,000', 200000:'200,000', 300000:'300,000', 400000:'400,000', 500000:'500,000', 600000:'600,000', 700000:'700,000', 800000:'800,000', 900000:'900,000', 1000000:'1,000,000'}),

    dcc.Graph(id='topo-map'),

    html.P(id="context-label"),

    html.Pre(id='hover-data'),

    html.Div(id='node_selected'),

    html.Div(id='links_view'),

    dcc.Dropdown(['node_outdegree', 'org_name', 'no data coloring'], 'no data coloring', id='color_by'),

    #dash_table.DataTable(id="table",
    #    data=top_nodes_df.to_dict('records'),
    #    columns=[{'id': c, 'name': c, } for c in top_nodes_df]
    #),

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
        #node_ids, latitudes, longitudes = get_all_node_coords(config.DB_DIR + itdk_vsn + "-itdk.db")
        #node_coords_df = pd.DataFrame({'node_id': node_ids, 'latitude' : latitudes, 'longitude' : longitudes})
        #fig = px.scatter_mapbox(lat=node_coords_df['latitude'], lon=node_coords_df['longitude'], hover_name=node_coords_df['node_id'])

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
    Output('hover-data', 'children'),
    Input('topo-map', 'hoverData'))
def display_node_data_on_hover(hoverData):
    if hoverData is not None:
        #hover_action = json.loads(hoverData)
        node_data = hoverData['points'][0]['customdata']
        node_id = node_data[0]
        outdegree = node_data[1]
        asn = node_data[2]
        org_name = node_data[3]
        data_src = node_data[4]

        return "Node ID: {}\nOutdegree: {}\nASN: {}\nOrg Name: {}".format(node_id, outdegree, asn, org_name)
        #return json.dumps(hoverData, indent=2)


@app.callback(
    Output(component_id='links_view', component_property='children'),
    Input('topo-map', 'clickData'))
def display_click_data(clickData):
    if clickData is not None:
        node_data = clickData['points'][0]['customdata']
        node_id = node_data[0]
        #outdegree = node_data[1]
        #asn = node_data[2]
        #org_name = node_data[3]
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
        node_dicts = [{'data': {'id': str(x), 'label': str(x)}} for x in nodes]
        edge_dicts = [{'data': {'source': str(node_id), 'target': str(y)}} for y in links_df.node_id_2]

        return dash_cytoscape.Cytoscape(
            id='links',
            autoungrabify=True,
            minZoom=0.2,
            maxZoom=1,
            style={'width': '100%', 'height': '500px'},
            elements=[{'data': {'id': str(node_id), 'label': str(node_id)}}] + node_dicts + edge_dicts,
            layout={'name': 'concentric'}
        )

    #return json.dumps(clickData, indent=2)
    #return link_table


# view in browser at http://127.0.0.1:8050/
if __name__ == '__main__':
    app.run_server(debug=True)

