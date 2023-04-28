#! /usr/bin/env python3

BASE_ARCHIVE_URL = "http://publicdata.caida.org/datasets/topology/ark/ipv4/itdk/"

DOWNLOAD_TO_DIR = "/home/allison/Desktop/ITDK/"

DB_DIR = "/home/allison/Desktop/ITDK/"

LIST_TABLES_QUERY = """SELECT name FROM sqlite_master
    WHERE type='table';"""
# usage example:
# cursor.execute(config.LIST_TABLES_QUERY)
# print(cursor.fetchall())