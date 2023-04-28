#! /usr/bin/env python3

import config
import requests, os, glob, shutil, gzip, bz2, sqlite3
from bs4 import BeautifulSoup


def get_file_by_url(file_url, output_filename):
    raw_resp = requests.get(file_url)

    if raw_resp.status_code != 200:
        raise Exception("requests.get() return code: {}".format(raw_resp.status_code))

    with open(output_filename, "wb+") as outf:
        outf.write(raw_resp.content)



def decompress_file(input_filename, output_filename=None):
    if ".gz" in input_filename:
        if output_filename is None:
            output_filename = input_filename.removesuffix(".gz")

        with gzip.open(input_filename, "rb") as inf:
            with open(output_filename, "wb") as outf:
                shutil.copyfileobj(inf, outf)

        os.remove(input_filename)

    elif ".bz2" in input_filename:
        if output_filename is None:
            output_filename = input_filename.removesuffix(".bz2")

        with bz2.open(input_filename, "rb") as inf:
            with open(output_filename, "wb") as outf:
                shutil.copyfileobj(inf, outf)

        os.remove(input_filename)



def get_links_from_html_page(web_page_url):
    resp = requests.get(web_page_url)

    page_soup = BeautifulSoup(resp.content, 'html.parser')

    itdk_releases = []

    for a_href in page_soup.find_all('a'):
        link = a_href.get('href')
        if '?' in link or link in web_page_url:
            continue
        else:
            itdk_releases.append(link.replace("/", ""))

    return itdk_releases



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

            node_id = fields[1]

            for addr in fields[2:]:
                cursor.execute("INSERT INTO map_address_to_node (address, node_id) VALUES (?, ?);", (addr, node_id))

            cnxn.commit()



def parse_links_file(cnxn, cursor, links_file):
    with open(links_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")
            link_id = fields[1]

            for tuple in fields[2:]:
                subfields = tuple.split(':', 1)

                if len(subfields) > 1:
                    node_id = subfields[0]
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



def parse_nodes_as_file(cnxn, cursor, nodes_as_file):
    with open(nodes_as_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")



def parse_nodes_geo_file(cnxn, cursor, nodes_geo_file):
    with open(nodes_geo_file, "r") as inf:
        for line in inf:
            if line.startswith("#"):
                continue

            fields = line.strip().split(" ")



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

        if fname.endswith(".ifaces"):
            parse_ifaces_file(cnxn, cursor, f)

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