#!/usr/bin/python3

import properties, log_util, parse_util
import download, decompress, initialize_db, read_in_nodes, read_in_links

def convert_itdk_edition():
  os_env = properties.deserialize_os_env()
  itdkv = properties.deserialize_itdk_version()
  db = properties.deserialize_db()

  # Download

  # Decompress

  # Initialize database

  # Read in nodes

  # Read in links


def main():
    # eventually make this a loop so you can do multiple editions
    convert_itdk_edition()

main()
