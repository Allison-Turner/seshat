#! /usr/bin/env python3


from glob import glob
import os, sys, math
#import json
import plotly.express as px
#import plotly.graph_objects as go
#import dash
from dash import Dash, dcc, html, Input, Output, dash_table, register_page, callback
import pandas as pd
#import dash_cytoscape


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from data_status_checker import check_download_status_for_each_itdk_version


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])



register_page(__name__, path='/browser', name='Dataset Browser')

download_status = check_download_status_for_each_itdk_version(config.ITDK_ARCHIVE_URL, config.ITDK_DOWNLOAD_TO_DIR)

itdk_versions = sorted(list(download_status.keys()))

downloaded = [v for v in itdk_versions if download_status[v] is True]
undownloaded = [v for v in itdk_versions if download_status[v] is False]

archive_file_sizes_df = pd.DataFrame(columns=['file_name', 'archive_date', 'size_bytes', 'size_human_readable'])

for itdk_archive_date in downloaded:
    archive_dir = config.ITDK_DOWNLOAD_TO_DIR + itdk_archive_date + "/*.*"
    files = glob(archive_dir)

    total_archive_size = 0

    for f in files:
        file_size_bytes = os.stat(f).st_size
        total_archive_size += file_size_bytes
        human_readable_size = convert_size(file_size_bytes)

        new_row = pd.DataFrame(
            data=list(zip([f], [itdk_archive_date], [file_size_bytes], [human_readable_size])), 
            columns=['file_name', 'archive_date', 'size_bytes', 'size_human_readable']
            )
        
        archive_file_sizes_df = pd.concat([archive_file_sizes_df, new_row])


styles = {
    'container': {
        'display': 'grid',
        'grid-template-columns': '1fr 1fr',
        'grid-template-rows': '1fr',
        'grid-gap': '1em',
    },
}


layout = html.Div(children=
    [
        dcc.Tabs(id="data_source_to_manage", value='manage_itdk', children=[
            dcc.Tab(label='Macroscopic Internet Topology Data Kit (ITDK)', value='manage_itdk'),
            dcc.Tab(label='AS to Organization (AS2Org)', value='manage_as2org'),
        ]),
        html.Div(className='container', style=styles['container'], children=[
            html.Div(id='storage_stats', className='item'),
            html.Div(id='data_management_content', className='item'),
        ])
    ]

)


@callback(
        [
            Output(component_id='data_management_content', component_property='children'),
            Output(component_id='storage_stats', component_property='children')
        ], 
          Input('data_source_to_manage', 'value')
        )
def render_content(tab):
    if tab == 'manage_itdk':
        download_options = [
                            html.H2("Download More Dataset Editions"),
                            dcc.Checklist(id='itdk_releases_to_download', options=undownloaded, value=[]),
                            html.Button(id='download_selected_itdk_releases', children="Download Selected ITDK Releases"),
                        ]
        
        storage_stats = [
                            html.H2("Storage Usage"),
                            dash_table.DataTable(archive_file_sizes_df.to_dict('records'), columns=[{'id': c, 'name': c, } for c in archive_file_sizes_df])
                        ]

        return download_options, storage_stats
    
    elif tab == 'manage_as2org':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs-dcc',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])

"""
AS to Organization Dataset
AS Rank
Holistic Orthography of Internet Hostname Observations (Hoiho)
Prefix-to-AS Mappings
Internet eXchange Points Dataset
AS Classification
PeeringDB
Spoofer
"""