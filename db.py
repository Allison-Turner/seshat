#! /usr/bin/env python3

import os, glob, datetime, sqlite3, re, csv

import config

from get_files import get_file_by_url, decompress_file, get_links_from_html_page



def get_itdk_files():
    itdk_releases = get_links_from_html_page(config.BASE_ARCHIVE_URL)

    latest_release = itdk_releases[-1]

    latest_version_url = config.BASE_ARCHIVE_URL + "/" + latest_release

    available_files = get_links_from_html_page(latest_version_url)

    itdk_dir = config.DOWNLOAD_TO_DIR + latest_release + "/"

    if not os.path.exists(itdk_dir):
        os.mkdir(itdk_dir)

    local_files = glob.glob(itdk_dir + "*.*")
    
    files_to_get = []
    for af in available_files:
        match_found = False

        for lf in local_files:
            if os.path.basename(lf) in af:
                match_found = True
                break
        if match_found is False:
            files_to_get.append(af)

    for f in files_to_get:
        get_file_by_url(latest_version_url + "/" + f, itdk_dir + f)
        decompress_file(itdk_dir + f)

    return latest_release, glob.glob(itdk_dir + "*.*")



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

                two_part_city = False

                if "," in line:
                    two_part_city = True

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", "").replace(":", ""))
                continent = fields[2]
                country = fields[3]

                if two_part_city is True:
                    region = fields[4]
                    rest_of_line = " ".join(fields[5:])
                    result = re.search("(\-)?[0-9]+\.[0-9]+(\s)+(\-)?[0-9]+\.[0-9]+", rest_of_line)
                    if result is not None:
                        coords = result.group().split()

                        lat_index = rest_of_line.index(coords[0])

                        latitude = float(coords[0])
                        longitude = float(re.sub("[A-Za-z]", "", coords[1]))

                        city = rest_of_line[:lat_index].replace(",", " ")

                if len(fields) == 8:
                    region = None
                    city = fields[4]
                    latitude = float(fields[5])
                    longitude = float(re.sub("[A-Za-z]", "", fields[6]))

                elif len(fields) == 9:
                    region = fields[4]
                    city = fields[5]
                    latitude = float(fields[6])
                    longitude = float(re.sub("[A-Za-z]", "", fields[7]))

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



def convert_files_to_csvs(itdk_files, itdk_version, csv_directory):
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

    return csv_files



def populate_db(db_file, itdk_csvs):

    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    schema_files = glob.glob(os.getcwd() + "/schemas/*.schema")

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

    cnxn.commit()

    cnxn.close()


def get_all_node_coords(db_file):
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

    return node_ids, latitudes, longitudes


def get_node_coords(db_file, node_id):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    cursor.execute("SELECT latitude, longitude FROM map_node_to_geo WHERE node_id = ?", (node_id,))
    result = cursor.fetchone()

    cnxn.close()

    return result


def get_links(db_file):
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    link_ids = []
    node_ids_1 = []
    addrs_1 = []
    node_ids_2 = []
    addrs_2 = []
    

    cursor.execute("SELECT link_id, node_id_1, address_1, node_id_2, address_2 FROM map_link_to_nodes")
    rows = cursor.fetchall()

    for r in rows:
        link_ids.append("L" + str(r[0]))
        node_ids_1.append("N" + str(r[1]))
        addrs_1.append(str(r[2]))
        node_ids_2.append("N" + str(r[3]))
        addrs_2.append(str(r[4]))

    cnxn.close()

    return (link_ids, node_ids_1, addrs_1, node_ids_2, addrs_2)



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

    midar_iff_csvs = convert_files_to_csvs(midar_iff_files, itdk_date, config.CSV_DIR)

    populate_db(midar_iff_db, midar_iff_csvs)



if __name__ == '__main__':
    __main__()