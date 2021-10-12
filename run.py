#!/usr/bin/python3

import properties, log_util, parse_util
import download, decompress, initialize_db, read_in_nodes, read_in_links
from argparse import ArgumentParser

def convert_itdk_edition(timestamp, os_env_json, itdkv_json, db_json):
    print("OS env JSON file: " + os_env_json + "\n")
    print("ITDK version JSON file: " + itdkv_json + "\n")
    print("DB properties JSON file: " + db_json + "\n")



    os_env = properties.deserialize_os_env(os_env_json)

    os_type = properties.os_env__os(os_env)
    username = properties.os_env__username(os_env)
    home_dir = properties.os_env__home(os_env)

    print("OS Type: " + os_type + "\nUsername: " + username + "\nHome Directory: " + home_dir + "\n")



    itdkv = properties.deserialize_itdk_version(itdkv_json)

    ipv = properties.itdk_version__ip_version(itdkv)
    year = str(properties.itdk_version__year(itdkv))
    m = properties.itdk_version__month(itdkv)
    if m < 10:
        month = "0" + str(m)
    else:
        month = str(m)
    d = properties.itdk_version__day(itdkv)
    if d < 10:
        day = "0" + str(d)
    else:
        day = str(d)
    url = properties.itdk_version__url(itdkv)
    topo_choice = properties.itdk_version__topo_choice(itdkv)
    ext = properties.itdk_version__compression_extension(itdkv)
    file_loc = properties.itdk_version__file_location(itdkv)
    loc = home_dir + file_loc
    download_new = properties.itdk_version__download(itdkv)
    decompress_new = properties.itdk_version__decompress(itdkv)

    print("IP Version: " + str(ipv) + "\nYear: " + year + "\nMonth: " + month + "\nDay: " + day + "\nURL: " + url + "\nTopology Choice: " + topo_choice + "\nExtension: " + ext + "\nFile Path: " + loc + "\nDownload?: " + str(download_new) + "\nDecompress?: " + str(decompress_new) + "\n")



    db = properties.deserialize_db(db_json)

    driver = properties.db__driver(db)
    server = properties.db__server(db)
    name = properties.db__name(db)
    user = properties.db__user(db)
    pwd = properties.db__pwd(db)

    print("Driver: " + driver + "\nServer: " + server + "\nName: " + name + "\nUser: " + user + "\nPassword: " + pwd + "\n")



    if os_type == "Ubuntu":
        # Download
        if download_new:
            print("Downloading dataset files")
            download.ubuntu__download(timestamp, loc, ipv, year, month, day, url, topo_choice, ext)

        # Decompress
        if decompress_new or download_new:
            print("Decompressing dataset files")
            decompress.ubuntu__decompress(timestamp, loc, ipv, topo_choice, ext)

        # Initialize database
        cnxn = initialize_db.sqlite__connect(driver, server, name, user, pwd)
        # initialize_db.create_schema(cnxn.cursor(), user, day, month, year, ipv)
        initialize_db.sqlite__create_schema(cnxn.cursor(), user, day, month, year, ipv)

        # Read in nodes

        # Read in links


def main():
    args = parser.parse_args()

    timestamp = log_util.get_timestamp()
    # eventually make this a loop so you can do multiple editions
    convert_itdk_edition(timestamp, args.os_env_json, args.itdk_json, args.db_json)



# Set up command line argument parser
parser = ArgumentParser(description="A program to parse CAIDA ITDK files into useful topology data structures")

parser.add_argument('-v','--itdk_version_jsons', dest="itdk_json", help="JSON file(s) describing the ITDK edition that you want to download/decompress/parse", required=False, default="properties/itdk_version.json")
parser.add_argument('-d','--db_json', dest="db_json", help="JSON file describing the database to use for the topology", required=False, default="properties/db.json")
parser.add_argument('-o','--os_env', dest="os_env_json", help="JSON file describing the OS and user in which this script is operating", required=False, default="properties/os_env.json")

main()
