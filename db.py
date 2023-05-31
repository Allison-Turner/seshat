#! /usr/bin/env python3

import os, glob, datetime, sqlite3, re, csv

from argparse import ArgumentParser

import config

parser = ArgumentParser(prog='ITDK-SQLite', description='Turn ITDK files into a local SQLite database')

parser.add_argument('--online', action='store_true')
parser.add_argument('--offline', dest='online', action='store_false')
parser.set_defaults(feature=True)

class Args:
    pass

def parse_nodes_file_to_csv(nodes_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    nodes_csv = csv_directory + itdk_version + "." + os.path.basename(nodes_file) + ".csv"

    with open(nodes_file, "r") as inf:
        with open(nodes_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", "").replace(":", ""))

                node_addrs = fields[2:]

                for addr in node_addrs:
                    outf.write("{},{}\n".format(node_id, addr))


       
def parse_nodes_geo_file_to_csv(nodes_geo_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    nodes_geo_csv = csv_directory + itdk_version + "." + os.path.basename(nodes_geo_file) + ".csv"

    with open(nodes_geo_file, "r") as inf:
        with open(nodes_geo_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", "").replace(":", ""))
                continent = fields[2]
                country = fields[3]

                rest_of_line = " ".join(fields[4:])

                result = re.search("(\-)?[0-9]+\.[0-9]+(\s)+(\-)?[0-9]+\.[0-9]+", rest_of_line)

                if result is not None:
                    coords = result.group().split()

                    lat_index = rest_of_line.index(coords[0])

                    latitude = float(coords[0])
                    longitude = float(re.sub("[A-Za-z]", "", coords[1]))

                    rest_of_line = rest_of_line[:lat_index].replace(",", "")
                else:
                    continue

                result = re.search("([0-9]{1,3}|[A-Z]{2,3})\s", rest_of_line)

                if result is not None:
                    region = result.group().replace(" ", "")

                    if region.isspace() or len(region) == 0:
                        region = None
                    
                    rest_of_line = rest_of_line.replace(region, "")
                else:
                    region = None

                city = rest_of_line.strip().replace(",", "")

                if city.isspace() or len(city) == 0:
                    city = None
                
                outf.write("{},{},{},{},{},{},{}\n".format(node_id, continent, country, region, city, latitude, longitude))



def parse_nodes_as_file_to_csv(nodes_as_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    nodes_as_csv = csv_directory + itdk_version + "." + os.path.basename(nodes_as_file) + ".csv"

    with open(nodes_as_file, "r") as inf:
        with open(nodes_as_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", ""))
                as_num = int(fields[2])

                outf.write("{},{}\n".format(node_id, as_num))



def parse_links_file_to_csv(links_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    links_csv = csv_directory + itdk_version + "." + os.path.basename(links_file) + ".csv"

    with open(links_file, "r") as inf:
        with open(links_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                link_id = int(fields[1].replace("L", "").replace(":", ""))

                first_node = None
                first_node_addr = None

                for tuple in fields[2:]:
                    subfields = tuple.split(':', 1)

                    if len(subfields) > 1:
                        node_id = int(subfields[0].replace("N", ""))
                        ip_addr = subfields[1]

                    else:
                        node_id = int(subfields[0].replace("N", ""))
                        ip_addr = None

                    if first_node is None:
                        first_node = node_id
                        first_node_addr = ip_addr
                    else:
                        outf.write("{},{},{},{},{}\n".format(link_id, first_node, first_node_addr, node_id, ip_addr))



def parse_as2org_file_to_csv(as2org_file, csv_directory):
    dt = os.path.basename(as2org_file).replace(".as-org2info.txt", "")

    year = dt[0:4]
    month = dt[4:6]
    day = dt[6:]

    asn_outfile = csv_directory + "-".join([year, month, day]) + ".as2org.asn.csv"
    org_outfile = csv_directory + "-".join([year, month, day]) + ".as2org.org.csv"

    with open(as2org_file, "r") as inf:
        with open(asn_outfile, "w+") as asn_outf:
            with open(org_outfile, "w+") as org_outf:
                for line in inf:
                    if line.startswith("#"):
                        continue

                    fields = line.strip().replace(",", "").split("|")

                    # organization entry
                    if len(fields) == 5:
                        org_id = fields[0]
                        changed = fields[1]
                        org_name = fields[2]
                        country = fields[3]
                        source = fields[4]

                        org_outf.write("{},{},{},{},{}\n".format(org_id, changed, org_name, country, source))

                    # AS number entry
                    elif len(fields) == 6:
                        as_num = fields[0]
                        changed = fields[1]
                        as_name = fields[2]
                        org_id = fields[3]
                        opaque_id = fields[4]
                        source = fields[5]

                        asn_outf.write("{},{},{},{},{},{}\n".format(as_num, changed, as_name, org_id, opaque_id, source))

    return asn_outfile, org_outfile



def convert_itdk_files_to_csvs(itdk_files, itdk_version, csv_directory):
    nodes_file = None
    nodes_as_file = None
    nodes_geo_file = None
    links_file = None
    ifaces_file = None

    for f in itdk_files:
        fname = os.path.basename(f)

        if fname.endswith(".ifaces"):
            ifaces_file = f
        elif fname.endswith(".links"):
            links_file = f
        elif fname.endswith(".nodes.as"):
            nodes_as_file = f
        elif fname.endswith(".nodes.geo"):
            nodes_geo_file = f
        elif fname.endswith(".nodes"):
            nodes_file = f
        elif fname.endswith(".geo-re.jsonl"):
            continue
        elif fname.endswith(".addrs"):
            continue
        elif fname.endswith("dns-names.txt"):
            continue

    itdk_csvs = glob.glob(csv_directory + "*.csv")

    generate_nodes_csv = True
    generate_nodes_as_csv = True
    generate_nodes_geo_csv = True
    generate_links_csv = True

    csv_files = []

    for f in itdk_csvs:
        if itdk_version not in f:
            continue

        if ".nodes.as" in f:
            generate_nodes_as_csv = False
            csv_files.append(f)
        elif ".nodes.geo" in f:
            generate_nodes_geo_csv = False
            csv_files.append(f)
        elif ".nodes" in f:
            generate_nodes_csv = False
            csv_files.append(f)
        elif ".links" in f:
            generate_links_csv = False
            csv_files.append(f)

    if generate_nodes_csv is True:
        print("{} Processing .nodes file".format(datetime.datetime.now()))
        nodes_csv = parse_nodes_file_to_csv(nodes_file, itdk_version, csv_directory)
        csv_files.append(nodes_csv)

    if generate_nodes_geo_csv is True:
        print("{} Processing .nodes.geo file".format(datetime.datetime.now()))
        nodes_geo_csv = parse_nodes_geo_file_to_csv(nodes_geo_file, itdk_version, csv_directory)
        csv_files.append(nodes_geo_csv)

    if generate_nodes_as_csv is True:
        print("{} Processing .nodes.as file".format(datetime.datetime.now()))
        nodes_as_csv = parse_nodes_as_file_to_csv(nodes_as_file, itdk_version, csv_directory)
        csv_files.append(nodes_as_csv)

    if generate_links_csv is True:
        print("{} Processing .links file".format(datetime.datetime.now()))
        links_csv = parse_links_file_to_csv(links_file, itdk_version, csv_directory)
        csv_files.append(links_csv)

    print("{} CSV files: [{}]".format(datetime.datetime.now(), ", ".join(csv_files) ))

    return csv_files



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

    print("{} Creating nodes_without_geo".format(datetime.datetime.now()))
    cursor.execute("""
    CREATE TABLE nodes_without_geo AS
    SELECT node_id
    FROM map_address_to_node
    WHERE node_id NOT IN (SELECT node_id FROM map_node_to_geo)
    """)

    cnxn.commit()

    print("{} Creating node_outdegrees".format(datetime.datetime.now()))
    cursor.execute("""
    CREATE TABLE node_outdegrees AS
    SELECT node_id, outdegree
    FROM (
        SELECT node_id_1 AS node_id, count(*) AS outdegree
        FROM map_link_to_nodes
        GROUP BY node_id
        ORDER BY outdegree DESC
        );
    """)    

    cnxn.commit()

    cnxn.close()

    print("{} Finished creating database".format(datetime.datetime.now()))


def fetch_top_nodes(db_file, num_to_fetch):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("""SELECT node_id, outdegree, as_number, org_name, latitude, longitude
                   FROM meta_table
                   LIMIT {};""".format(num_to_fetch))

    rows = cursor.fetchall()

    node_ids = [r[0] for r in rows]
    outdegrees = [r[1] for r in rows]
    asns = [r[2] for r in rows]
    org_names = [r[3] for r in rows]
    lats = [r[4] for r in rows]
    longs = [r[5] for r in rows]

    cnxn.close() 

    return node_ids, outdegrees, asns, org_names, lats, longs


def find_num_non_geo_nodes(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("""SELECT count(*)
                   FROM nodes_without_geo;""")

    result = cursor.fetchone()

    cnxn.close() 

    return int(result[0])


def find_num_geo_nodes(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("""SELECT count(*)
                   FROM map_node_to_geo;""")

    result = cursor.fetchone()

    cnxn.close() 

    return int(result[0])


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

    print("{} Finished creating database".format(datetime.datetime.now()))




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


def get_links_for_node(db_file, node_id):
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


def get_asn_for_node_id(node_id, db_file):
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


def create_meta_table(db_file):

    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    print("{} Creating meta table".format(datetime.datetime.now()))
    cursor.execute("""
    CREATE TABLE meta_table AS
    SELECT node_outdegrees.node_id, node_outdegrees.outdegree, map_node_to_asn.as_number, asn_org_names.org_name, map_node_to_geo.latitude, map_node_to_geo.longitude
    FROM node_outdegrees
    INNER JOIN map_node_to_asn ON node_outdegrees.node_id = map_node_to_asn.node_id
    INNER JOIN asn_org_names ON map_node_to_asn.as_number = asn_org_names.as_num
    INNER JOIN map_node_to_geo ON node_outdegrees.node_id = map_node_to_geo.node_id
    """)

    cnxn.commit()

    cnxn.close()


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

    #asn_outfile, org_outfile = parse_as2org_file_to_csv(as2org_file, config.AS2ORG_CSV_DIR)

    #as2org_dt = os.path.basename(as2org_file).split(".")[0]
    #year = as2org_dt[0:4]
    #month = as2org_dt[4:6]
    #day = as2org_dt[6:]
    #as2org_date = year + "-" + month + "-" + day
    #as2org_db = config.AS2ORG_DB_DIR + "as2org." + as2org_date + ".db"
    #populate_as2org_db(asn_outfile, org_outfile, midar_iff_db)

    create_meta_table(midar_iff_db)


    """
    top_nodes_file = config.DB_DIR + "top-outdegree." + "midar-iff-" + itdk_date + ".txt"

    if os.path.isfile(top_nodes_file) is False:
        top_nodes_and_outdegrees = calculate_top_nodes(midar_iff_db)
        top_nodes = [r[0] for r in top_nodes_and_outdegrees]
        top_node_outdegrees = [r[1] for r in top_nodes_and_outdegrees]
    
        with open(top_nodes_file, "w+") as outf:
            for i in range(len(top_nodes)):
                n = top_nodes[i]
                d = top_node_outdegrees[i]

                asn = get_asn_for_node_id(n, midar_iff_db)
                org_name = get_org_name_for_as_number(asn, as2org_db)              

                result = get_node_coords(midar_iff_db, n) 
                if result is not None:
                    lat = result[0]
                    long = result[1]
                else:
                    lat = None
                    long = None

                outf.write("{},{},{},{},{},{}\n".format(n, d, asn, org_name, lat, long))

    else:
        with open(top_nodes_file, "r") as inf:
            lines = inf.readlines()
            top_nodes = [l.strip().split(",")[0] for l in lines]
            top_outdegrees = [l.strip().split(",")[1] for l in lines]
            top_asns = [l.strip().split(",")[2] for l in lines]
            top_org_names =  [l.strip().split(",")[3] for l in lines]
            top_lats = [l.strip().split(",")[4] for l in lines]
            top_longs = [l.strip().split(",")[5] for l in lines]

            for i in range(len(top_nodes)):
                n = top_nodes[i]
                d = top_outdegrees[i]
                asn = top_asns[i]
                org_name = top_org_names[i]      
                lat =top_lats[i]
                long = top_longs[i]

                print("{},{},{},{},{},{}".format(n, d, asn, org_name, lat, long))


    """
    
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