#! /usr/bin/env python3

import os, glob, datetime, sqlite3, re, csv

from argparse import ArgumentParser

import config

from parse_datasets import convert_itdk_files_to_csvs, convert_as2org_file_to_csvs

parser = ArgumentParser(prog='ITDK-SQLite', description='Turn ITDK files into a local SQLite database')

parser.add_argument('--online', action='store_true')
parser.add_argument('--offline', dest='online', action='store_false')
parser.set_defaults(feature=True)

class Args:
    pass



def populate_itdk_db(db_file, itdk_csvs):

    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    schema_files = glob.glob(os.getcwd() + "/schemas/itdk/*.schema")

    for schema in schema_files:
        with open(schema, "r") as inf:
            cmd = inf.read()

        cursor.execute(cmd)
        cnxn.commit()

    nodes_csv = None
    nodes_as_csv = None
    nodes_geo_csv = None
    links_csv = None
    ifaces_csv = None

    for f in itdk_csvs:
        print(f)
        fname = os.path.basename(f)

        if fname.endswith(".ifaces.csv"):
            ifaces_csv = f
        elif fname.endswith(".links.csv"):
            links_csv = f
        elif fname.endswith(".nodes.as.csv"):
            nodes_as_csv = f
        elif fname.endswith(".nodes.geo.csv"):
            nodes_geo_csv = f
        elif fname.endswith(".nodes.csv"):
            nodes_csv = f
    
    print("{} Inserting .nodes data to {}".format(datetime.datetime.now(), db_file))
    with open(nodes_csv,'r') as f: 
        nodes_reader = csv.reader(f)
        cursor.executemany("INSERT INTO map_address_to_node (address, node_id) VALUES (?, ?);", nodes_reader)

    cnxn.commit()

    print("{} Inserting .nodes.as data to {}".format(datetime.datetime.now(), db_file))
    with open(nodes_as_csv,'r') as f: 
        nodes_as_reader = csv.reader(f)
        cursor.executemany("INSERT INTO map_node_to_asn (node_id, as_number) VALUES (?, ?);", nodes_as_reader)

    cnxn.commit()
    
    print("{} Inserting .nodes.geo data to {}".format(datetime.datetime.now(), db_file))
    with open(nodes_geo_csv,'r') as f: 
        nodes_geo_reader = csv.reader(f)
        value_list = [(int(each_row[0]), each_row[1], each_row[2], each_row[3], each_row[4], float(each_row[5]), float(each_row[6])) for each_row in nodes_geo_reader]
        cursor.executemany("INSERT INTO map_node_to_geo (node_id, continent, country, region, city, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?);", value_list)
    
    cnxn.commit()

    print("{} Inserting .links data to {}".format(datetime.datetime.now(), db_file))
    with open(links_csv,'r') as f: 
        links_reader = csv.reader(f)
        cursor.executemany("INSERT INTO map_link_to_nodes(link_id, node_id_1, address_1, node_id_2, address_2) VALUES (?, ?, ?, ?, ?);", links_reader)
    
    print("{} Creating map_link_to_geo".format(datetime.datetime.now()))
    cursor.execute(
    """
        CREATE TABLE map_link_to_geo AS
        SELECT link_id, node_id_1, address_1, node_1_geo.latitude AS latitude_1, node_1_geo.longitude AS longitude_1, node_id_2, address_2, node_2_geo.latitude AS latitude_2, node_2_geo.longitude AS longitude_2
        FROM map_link_to_nodes
        INNER JOIN map_node_to_geo AS node_1_geo ON map_link_to_nodes.node_id_1 = node_1_geo.node_id
        INNER JOIN map_node_to_geo AS node_2_geo ON map_link_to_nodes.node_id_2 = node_2_geo.node_id;
    """
    )

    cnxn.commit()

    #print("{} Creating nodes_without_geo".format(datetime.datetime.now()))
    #cursor.execute(
    """
    CREATE TABLE nodes_without_geo AS
    SELECT node_id
    FROM map_address_to_node
    WHERE node_id NOT IN (SELECT node_id FROM map_node_to_geo)
    """
    #)
    #cnxn.commit()

    cnxn.close()

    print("{} Finished creating ITDK tables".format(datetime.datetime.now()))



def populate_as2org_db(asn_csv, org_csv, db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    schema_files = glob.glob(os.getcwd() + "/schemas/as2org/*.schema")

    for schema in schema_files:
        with open(schema, "r") as inf:
            cmd = inf.read()

        cursor.execute(cmd)
        cnxn.commit()

    print("{} Inserting as2org.as_num data to {}".format(datetime.datetime.now(), db_file))
    with open(asn_csv,'r') as f: 
        asn_reader = csv.reader(f)
        cursor.executemany("INSERT INTO map_as_to_org_id (as_num, changed, as_name, org_id, opaque_id, source) VALUES (?, ?, ?, ?, ?, ?);", asn_reader)

    cnxn.commit()

    print("{} Inserting as2org.org data to {}".format(datetime.datetime.now(), db_file))
    with open(org_csv,'r') as f: 
        org_reader = csv.reader(f)
        cursor.executemany("INSERT INTO map_org_id_to_org_name (org_id, changed, org_name, country, source) VALUES (?, ?, ?, ?, ?);", org_reader)

    cnxn.commit()

    print("{} Creating asn_org_names table".format(datetime.datetime.now()))
    cursor.execute("""
    CREATE TABLE asn_org_names AS
    SELECT as_num, org_name
    FROM map_as_to_org_id
    INNER JOIN map_org_id_to_org_name ON map_as_to_org_id.org_id = map_org_id_to_org_name.org_id;
    """)

    cnxn.commit()

    cnxn.close()

    print("{} Finished creating AS2Org tables".format(datetime.datetime.now()))



def create_meta_tables(db_file):

    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    print("{} Creating node_outdegrees".format(datetime.datetime.now()))
    cursor.execute(
    """
    CREATE TABLE node_outdegrees AS
    SELECT node_id, outdegree
    FROM (
        SELECT node_id_1 AS node_id, count(*) AS outdegree
        FROM map_link_to_nodes
        GROUP BY node_id
        ORDER BY outdegree DESC
        );
    """
    )    
    cnxn.commit()

    print("{} Creating node_indegrees".format(datetime.datetime.now()))
    cursor.execute(
    """
    CREATE TABLE node_indegrees AS
    SELECT node_id, indegree
    FROM (
        SELECT node_id_2 AS node_id, count(*) AS indegree
        FROM map_link_to_nodes
        GROUP BY node_id
        ORDER BY indegree DESC
        );
    """
    )    
    cnxn.commit()

    print("{} Creating meta table".format(datetime.datetime.now()))
    cursor.execute(
    """
    CREATE TABLE meta_table AS
    SELECT nodes.node_id, node_outdegrees.outdegree, node_indegrees.indegree, map_node_to_asn.as_number, asn_org_names.org_name, map_node_to_geo.latitude, map_node_to_geo.longitude
    FROM (
        SELECT DISTINCT node_id
        FROM node_outdegrees

        UNION

        SELECT DISTINCT node_id
        FROM node_indegrees
    )nodes
    LEFT JOIN node_outdegrees ON nodes.node_id = node_outdegrees.node_id
    LEFT JOIN node_indegrees ON nodes.node_id = node_indegrees.node_id
    LEFT JOIN map_node_to_asn ON nodes.node_id = map_node_to_asn.node_id
    LEFT JOIN asn_org_names ON map_node_to_asn.as_number = asn_org_names.as_num
    LEFT JOIN map_node_to_geo ON nodes.node_id = map_node_to_geo.node_id;
    """
    )
    cnxn.commit()

    #print("{} Inserting non-geolocated nodes to meta table".format(datetime.datetime.now()))
    #cursor.execute(
    """
    INSERT INTO meta_table (node_id, outdegree, as_number, org_name)
    SELECT nodes_without_geo.node_id, node_outdegrees.outdegree, map_node_to_asn.as_number, asn_org_names.org_name
    FROM nodes_without_geo
    INNER JOIN node_outdegrees ON nodes_without_geo.node_id = node_outdegrees.node_id
    INNER JOIN map_node_to_asn ON nodes_without_geo.node_id = map_node_to_asn.node_id
    INNER JOIN asn_org_names ON map_node_to_asn.as_number = asn_org_names.as_num;
    """
    #)
    #cnxn.commit()

    print("{} Creating meta table index".format(datetime.datetime.now()))
    cursor.execute("CREATE UNIQUE INDEX node_index ON meta_table(node_id);")
    cnxn.commit()

    print("{} Finished creating meta table".format(datetime.datetime.now()))

    cnxn.close()


def list_tables_in_db(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cursor.fetchall()

    tables = [r[0] for r in rows]

    cnxn.close()

    return tables



def fetch_top_nodes(db_file, num_to_fetch):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("""SELECT node_id, outdegree, indegree, as_number, org_name, latitude, longitude
                   FROM meta_table
                   LIMIT {};""".format(num_to_fetch))

    rows = cursor.fetchall()

    node_ids = [r[0] for r in rows]
    outdegrees = [r[1] for r in rows]
    indegrees = [r[2] for r in rows]
    asns = [r[3] for r in rows]
    org_names = [r[4] for r in rows]
    lats = [r[5] for r in rows]
    longs = [r[6] for r in rows]

    cnxn.close() 

    return node_ids, outdegrees, indegrees, asns, org_names, lats, longs



def find_num_non_geo_nodes(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("""
    SELECT count(*)
    FROM meta_table
    WHERE latitude IS NULL;
    """
    )

    result = cursor.fetchone()

    cnxn.close() 

    return int(result[0])



def find_num_geo_nodes(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("""
    SELECT count(*)
    FROM meta_table
    WHERE latitude IS NOT NULL;
    """
    )

    result = cursor.fetchone()

    cnxn.close() 

    return int(result[0])



def get_all_node_coords(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT node_id, latitude, longitude FROM map_node_to_geo")
    rows = cursor.fetchall()

    node_ids = [r[0] for r in rows]
    latitudes = [r[1] for r in rows]
    longitudes = [r[2] for r in rows]

    cnxn.close()

    return node_ids, latitudes, longitudes



def get_node_coords(db_file, node_id):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT latitude, longitude FROM map_node_to_geo WHERE node_id = ?", (node_id,))
    result = cursor.fetchone()
    lat = result[0]
    long = result[1]

    cnxn.close()

    return lat, long



def get_links(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT link_id, node_id_1, address_1, node_id_2, address_2 FROM map_link_to_nodes")
    rows = cursor.fetchall()

    link_ids = [r[0] for r in rows]
    node_ids_1 = [r[1] for r in rows]
    addrs_1 = [r[2] for r in rows]
    node_ids_2 = [r[3] for r in rows]
    addrs_2 = [r[4] for r in rows]

    cnxn.close()

    return (link_ids, node_ids_1, addrs_1, node_ids_2, addrs_2)



def get_ingress_links_for_node(db_file, node_id):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT link_id, node_id_1, address_1, node_id_2, address_2 FROM map_link_to_nodes WHERE node_id_2 = ?", (node_id,))
    rows = cursor.fetchall()

    link_ids = [r[0] for r in rows]
    node_ids_1 = [r[1] for r in rows]
    addrs_1 = [r[2] for r in rows]
    node_ids_2 = [r[3] for r in rows]
    addrs_2 = [r[4] for r in rows]

    cnxn.close()

    return (link_ids, node_ids_1, addrs_1, node_ids_2, addrs_2)



def get_egress_links_for_node(db_file, node_id):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT link_id, node_id_1, address_1, node_id_2, address_2 FROM map_link_to_nodes WHERE node_id_1 = ?", (node_id,))
    rows = cursor.fetchall()

    link_ids = [r[0] for r in rows]
    node_ids_1 = [r[1] for r in rows]
    addrs_1 = [r[2] for r in rows]
    node_ids_2 = [r[3] for r in rows]
    addrs_2 = [r[4] for r in rows]

    cnxn.close()

    return (link_ids, node_ids_1, addrs_1, node_ids_2, addrs_2)



def get_geo_links_for_node(db_file, node_id):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT link_id, node_id_1, address_1, latitude_1, longitude_1, node_id_2, address_2, latitude_2, longitude_2 FROM map_link_to_geo WHERE node_id_1 = ?", (node_id,))
    rows = cursor.fetchall()

    link_ids = [r[0] for r in rows]
    node_ids_1 = [r[1] for r in rows]
    addrs_1 = [r[2] for r in rows]
    lat_1 = [r[3] for r in rows]
    long_1 = [r[4] for r in rows]
    node_ids_2 = [r[5] for r in rows]
    addrs_2 = [r[6] for r in rows]
    lat_2 = [r[7] for r in rows]
    long_2 = [r[8] for r in rows]

    cnxn.close()

    return (link_ids, node_ids_1, lat_1, long_1, addrs_1, node_ids_2, addrs_2, lat_2, long_2)



def get_geo_links(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT link_id, node_id_1, address_1, latitude_1, longitude_1, node_id_2, address_2, latitude_2, longitude_2 FROM map_link_to_geo")
    rows = cursor.fetchall()

    link_ids = [r[0] for r in rows]
    node_ids_1 = [r[1] for r in rows]
    addrs_1 = [r[2] for r in rows]
    lat_1 = [r[3] for r in rows]
    long_1 = [r[4] for r in rows]
    node_ids_2 = [r[5] for r in rows]
    addrs_2 = [r[6] for r in rows]
    lat_2 = [r[7] for r in rows]
    long_2 = [r[8] for r in rows]

    cnxn.close()

    return (link_ids, node_ids_1, addrs_1, lat_1, long_1, node_ids_2, addrs_2, lat_2, long_2)



def get_asn_for_node_id(db_file, node_id):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT as_number FROM map_node_to_asn WHERE node_id = ?", (node_id,))
    result = cursor.fetchone()[0]

    cnxn.close()

    return result



def get_org_name_for_as_number(as_number, db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT org_id FROM map_as_to_org_id WHERE as_num = ?", (as_number,))
    org_id = cursor.fetchone()[0]

    cursor.execute("SELECT org_name FROM map_org_id_to_org_name WHERE org_id= ?", (org_id,))
    org_name = cursor.fetchone()[0]

    cnxn.close()

    return org_name



def get_meta_table_rows_for_node_ids(db_file, node_ids):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    placeholder = '?'
    placeholder_seq = ', '.join(placeholder for n in node_ids)
    query = "SELECT node_id, outdegree, indegree, as_number, org_name, latitude, longitude FROM meta_table WHERE node_id IN (%s)" % placeholder_seq

    cursor.execute(query, node_ids)
    rows = cursor.fetchall()

    r_node_ids = [r[0] for r in rows]
    outdegrees = [r[1] for r in rows]
    indegrees = [r[2] for r in rows]
    as_numbers = [r[3] for r in rows]
    org_names = [r[4] for r in rows]
    latitudes = [r[5] for r in rows]
    longitudes = [r[6] for r in rows]

    cnxn.close()

    return r_node_ids, outdegrees, indegrees, as_numbers, org_names, latitudes, longitudes


def __main__():
    args = Args()
    parser.parse_args(namespace=args)

    as2org_file = None
    
    if args.online is True:
        config.initialize_directories()
        from get_files import get_itdk_files, get_contemporary_as2org_release_for_itdk_version
        itdk_date, files = get_itdk_files(config.ITDK_ARCHIVE_URL, config.ITDK_DOWNLOAD_TO_DIR)
        as2org_file = get_contemporary_as2org_release_for_itdk_version(itdk_date, config.AS2ORG_ARCHIVE_URL, config.AS2ORG_DOWNLOAD_TO_DIR)

    else:
        files = glob.glob(config.ITDK_DOWNLOAD_TO_DIR + config.ITDK_VERSION + "/*.*")
        itdk_date = config.ITDK_VERSION
    
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
    
    midar_iff_db = config.ITDK_DB_DIR + "midar-iff-" + itdk_date + "-itdk.db"
    speedtrap_db = config.ITDK_DB_DIR + "speedtrap-" + itdk_date + "-itdk.db"

    #midar_iff_csvs = convert_itdk_files_to_csvs(midar_iff_files, itdk_date, config.ITDK_CSV_DIR)

    #populate_itdk_db(midar_iff_db, midar_iff_csvs)
    
    files = glob.glob(config.AS2ORG_DOWNLOAD_TO_DIR + "*")
    for f in files:
        if ".as-org2info.txt" in f:
            as2org_file = f

    #asn_outfile, org_outfile = convert_as2org_file_to_csvs(as2org_file, config.AS2ORG_CSV_DIR)

    #as2org_dt = os.path.basename(as2org_file).split(".")[0]
    #year = as2org_dt[0:4]
    #month = as2org_dt[4:6]
    #day = as2org_dt[6:]
    #as2org_date = year + "-" + month + "-" + day
    #as2org_db = config.AS2ORG_DB_DIR + "as2org." + as2org_date + ".db"
    
    #populate_as2org_db(asn_outfile, org_outfile, midar_iff_db)

    create_meta_tables(midar_iff_db)



    
"""
2023-05-25 18:21:06.370722 Downloading ITDK files from 2022-02
2023-05-25 18:38:47.127378 Finished downloading and decompressing latest ITDK edition files
2023-05-25 18:38:51.172688 Processing .nodes file


2023-05-26 09:47:55.053104 Downloading ITDK files from 2022-02
2023-05-26 09:47:55.194160 Finished downloading and decompressing latest ITDK edition files
2023-05-26 09:47:56.290026 Processing .nodes file
2023-05-26 09:50:52.400490 Processing .nodes.geo file
2023-05-26 09:58:02.227410 Processing .nodes.as file
2023-05-26 09:59:32.469684 Processing .links file

2023-05-26 10:22:01.414023 Downloading ITDK files from 2022-02
2023-05-26 10:22:01.608301 Finished downloading and decompressing latest ITDK edition files
2023-05-26 10:22:03.737238 CSV files: [/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.csv, /home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.as.csv, /home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.geo.csv, /home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.links.csv]
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.csv
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.as.csv
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.geo.csv
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.links.csv
2023-05-26 10:22:03.738021 Inserting .nodes data to /home/allison/Desktop/interactive-internet-topology/ITDK/db/midar-iff-2022-02-itdk.db
2023-05-26 10:24:41.609438 Inserting .nodes.as data to /home/allison/Desktop/interactive-internet-topology/ITDK/db/midar-iff-2022-02-itdk.db
2023-05-26 10:26:10.244818 Inserting .nodes.geo data to /home/allison/Desktop/interactive-internet-topology/ITDK/db/midar-iff-2022-02-itdk.db
2023-05-26 10:33:41.475173 Inserting .links data to /home/allison/Desktop/interactive-internet-topology/ITDK/db/midar-iff-2022-02-itdk.db
2023-05-26 10:39:20.343354 Creating map_link_to_geo
2023-05-26 10:43:38.123299 Creating nodes_without_geo

2023-05-30 09:28:22.557117 CSV files: [/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.csv, /home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.as.csv, /home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.geo.csv, /home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.links.csv]
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.csv
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.as.csv
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.nodes.geo.csv
/home/allison/Desktop/interactive-internet-topology/ITDK/csv/2022-02.midar-iff.links.csv
2023-05-30 09:28:22.558073 Creating nodes_without_geo
2023-05-30 09:30:48.603090 Creating node_outdegrees
2023-05-30 09:32:20.612142 Finished creating database
2023-05-30 09:32:20.969836 Inserting as2org.as_num data to /home/allison/Desktop/interactive-internet-topology/ITDK/db/midar-iff-2022-02-itdk.db
2023-05-30 09:32:21.449815 Inserting as2org.org data to /home/allison/Desktop/interactive-internet-topology/ITDK/db/midar-iff-2022-02-itdk.db
2023-05-30 09:32:21.828536 Creating asn_org_names table
2023-05-30 09:32:22.168595 Finished creating database
"""

if __name__ == '__main__':
    __main__()