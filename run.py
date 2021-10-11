#!/usr/bin/python3

import properties, log_util, parse_util
import download, decompress, initialize_db, read_in_nodes, read_in_links
from argparse import ArgumentParser

def convert_itdk_edition(timestamp, os_env_json, itdkv_json, db_json):
  os_env = properties.deserialize_os_env(os_env_json)

  os_type = properties.os_env__os(os_env)
  username = properties.os_env__username(os_env)
  home_dir = properties.os_env__home(os_env)
  print("OS Type: " + os_type + "\nUsername: " + username + "\nHome Directory: " + home_dir + "\n")



  print("ITDK version JSON file: " + itdkv_json + "\n")
  itdkv = properties.deserialize_itdk_version(itdkv_json)

  ipv = properties.itdk_version__ip_version(itdkv)
  year = properties.itdk_version__year(itdkv)
  month = properties.itdk_version__month(itdkv)
  day = properties.itdk_version__day(itdkv)
  url = properties.itdk_version__url(itdkv)
  topo_choice = properties.itdk_version__topo_choice(itdkv)
  ext = properties.itdk_version__compression_extension(itdkv)
  file_loc = properties.itdk_version__file_location(itdkv)
  download = properties.itdk_version__download(itdkv)
  decompress = properties.itdk_version__decompress(itdkv)

  loc = home_dir + file_loc


  db = properties.deserialize_db(db_json)

  driver = properties.db__driver(db)
  server = properties.db__server(db)
  name = properties.db__name(db)
  user = properties.db__user(db)
  pwd = properties.db__pwd(db)



  if os_type == "Ubuntu":
      # Download
      download.ubuntu__download(timestamp, loc, ipv, year, month, day, url, topo_choice, ext)

      # Decompress
      decompress.ubuntu__decompress(timestamp, loc, ipv, topo_choice, ext)

      # Initialize database
      cnxn = initialize_db.sqlite__connect()

      # Read in nodes

      # Read in links


def main():
    args = parser.parse_args()

    timestamp = log_util.get_timestamp()
    # eventually make this a loop so you can do multiple editions
    for file in args.itdk_jsons:
        convert_itdk_edition(timestamp, args.os_env_json, file, args.db_json)



# Set up command line argument parser
parser = ArgumentParser(description="A program to parse CAIDA ITDK files into useful topology data structures")
# parser.add_argument("-l", "--location", dest="folder_loc", default=cim_util.itdk_folder_loc, help="location of ITDK data archive folder, up to and including the folder name")
# parser.add_argument("-m", "--month", dest="month", default=cim_util.itdk_month, help="month of ITDK version")
# parser.add_argument("-d", "--day", dest="day", default=cim_util.itdk_day, help="day of ITDK version")
# parser.add_argument("-e", "--compression_ext", dest="compression_ext", default=cim_util.compression_extension, help="compression file extension for ITDK data archive files")
# parser.add_argument("-x", "--extract_files", dest="extract_files", default=False, help="Whether the data archive files need to be decompressed")
# parser.add_argument("-w", "--download_files", dest="download_files", default=False, help="Whether to download the data files from CAIDA's data server")
parser.add_argument('-v','--itdk_version_jsons', dest="itdk_jsons", help="JSON file(s) describing the ITDK edition that you want to download/decompress/parse", required=False, default="properties/itdk_version.json")
parser.add_argument('-d','--db_json', dest="db_json", help="JSON file describing the database to use for the topology", required=False, default="properties/db.json")
parser.add_argument('-o','--os_env', dest="os_env_json", help="JSON file describing the OS and user in which this script is operating", required=False, default="properties/os_env.json")

main()
