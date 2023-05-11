#! /usr/bin/env python3

import config

from db import get_itdk_files, populate_db
from generate_visualization import render_topo_map

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