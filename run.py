#! /usr/bin/env python3

import config

from db import get_itdk_files, populate_db

import sqlite3
import plotly.express as px



def render_topo_map(db_file, html_file_name):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    node_ids = []
    latitudes = []
    longitudes = []

    cursor.execute("SELECT node_id, latitude, longitude FROM map_node_to_geo")
    rows = cursor.fetchall()

    for r in rows:
        node_ids.append("N" + str(r[0]))
        latitudes.append(r[1])
        longitudes.append(r[2])

    cnxn.close()

    fig = px.scatter_geo(lat=latitudes, lon=longitudes, text=node_ids)
    fig.write_html(html_file_name)


def __main__():
    itdk_date, files = get_itdk_files()

    midar_iff_files = []
    speedtrap_files = []
    other_files = []

    for f in files:
        if "midar-iff" in f:
            midar_iff_files.append(f)
        elif "speedtrap" in f:
            speedtrap_files.append(f)
        else:
            other_files.append(f)

    midar_iff_db = config.DB_DIR + "midar-iff-" + itdk_date + "-itdk.db"
    speedtrap_db = config.DB_DIR + "speedtrap-" + itdk_date + "-itdk.db"

    populate_db(midar_iff_db, midar_iff_files)
    #populate_db(speedtrap_db, speedtrap_files)

    render_topo_map(midar_iff_db, config.FIG_DIR + "midar-iff-" + itdk_date + "-nodes-geo.html")



if __name__ == '__main__':
    __main__()