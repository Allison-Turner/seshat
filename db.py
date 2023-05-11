#! /usr/bin/env python3

import os, glob, datetime, sqlite3, re

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



def parse_nodes_file(cnxn, cursor, nodes_file):
    with open(nodes_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")

            node_id = fields[1].replace("N", "")

            for addr in fields[2:]:
                cursor.execute("INSERT INTO map_address_to_node (address, node_id) VALUES (?, ?);", (addr, node_id))

            cnxn.commit()



def parse_links_file(cnxn, cursor, links_file):
    with open(links_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")
            link_id = fields[1].replace("L", "")

            for tuple in fields[2:]:
                subfields = tuple.split(':', 1)

                if len(subfields) > 1:
                    node_id = subfields[0].replace("N", "")
                    ip_addr = subfields[1]

                else:
                    node_id = subfields[0]
                    ip_addr = None

                cursor.execute("INSERT INTO map_link_to_node(link_id, node_id, address) VALUES (?, ?, ?);", (link_id, node_id, ip_addr))

            cnxn.commit()



def parse_ifaces_file(cnxn, cursor, ifaces_file):
    with open(ifaces_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")
            addr = fields[0]

            node_id = None
            link_id = None
            transit_hop = False
            dest_hop = False

            for field_n in fields[1:]:
                if "N" in field_n:
                    node_id = field_n
                elif "L" in field_n:
                    link_id = field_n
                elif "T" in field_n:
                    transit_hop = True
                elif "D" in field_n:
                    dest_hop = True

            cursor.execute("INSERT INTO map_interface_to_node ()")



def parse_nodes_as_file(cnxn, cursor, nodes_as_file):
    with open(nodes_as_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")

            node_id = fields[1].replace("N", "")
            as_num = fields[2]
            heur = fields[3]

            cursor.execute("INSERT INTO map_node_to_asn (node_id, as_number) VALUES (?, ?);", (node_id, as_num))

            cnxn.commit()



def parse_nodes_geo_file(cnxn, cursor, nodes_geo_file):
    with open(nodes_geo_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")

            node_id = fields[1].replace("N", "")
            continent = fields[2]
            country = fields[3]
            region = fields[4]
            city = fields[5]
            latitude = fields[6]
            longitude = re.sub("[A-Za-z]", "", fields[7])

            cursor.execute("INSERT INTO map_node_to_geo (node_id, continent, country, region, city, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)", (node_id, continent, country, region, city, latitude, longitude))

            cnxn.commit()



def populate_db(db_file, itdk_files):

    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    schema_files = glob.glob(os.getcwd() + "/schemas/*.schema")

    for schema in schema_files:
        with open(schema, "r") as inf:
            cmd = inf.read()

        cursor.execute(cmd)
        cnxn.commit()

    for f in itdk_files:
        fname = os.path.basename(f)

        print("{} {}".format(datetime.datetime.now(), f))

        if fname.endswith(".ifaces"):
            continue
            #parse_ifaces_file(cnxn, cursor, f)

        elif fname.endswith(".links"):
            parse_links_file(cnxn, cursor, f)

        elif fname.endswith(".nodes.as"):
            parse_nodes_as_file(cnxn, cursor, f)

        elif fname.endswith(".nodes.geo"):
            parse_nodes_geo_file(cnxn, cursor, f)

        elif fname.endswith(".nodes"):
            parse_nodes_file(cnxn, cursor, f)

        elif fname.endswith(".geo-re.jsonl"):
            continue

        elif fname.endswith(".addrs"):
            continue

        elif fname.endswith("dns-names.txt"):
            continue

    cnxn.close()


def get_node_coords(db_file):
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

    return list(zip(node_ids, latitudes, longitudes))


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


if __name__ == '__main__':
    __main__()