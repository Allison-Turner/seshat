#! /usr/bin/env python3

import os

BASE_DIR = "/home/allison/Desktop/interactive-internet-topology/"

ITDK_ARCHIVE_URL = "http://publicdata.caida.org/datasets/topology/ark/ipv4/itdk/"
ITDK_VERSION = "2022-02"
ITDK_BASE_DIR = BASE_DIR + "ITDK/"
ITDK_DOWNLOAD_TO_DIR = ITDK_BASE_DIR + "downloads/"
ITDK_DB_DIR = ITDK_BASE_DIR + "db/"
ITDK_CSV_DIR = ITDK_BASE_DIR + "csv/"

LIST_TABLES_QUERY = """SELECT name FROM sqlite_master
    WHERE type='table';"""
# usage example:
# cursor.execute(config.LIST_TABLES_QUERY)
# print(cursor.fetchall())

#FIG_DIR = "/home/allison/Desktop/ITDK/figures"

AS2ORG_ARCHIVE_URL = "https://publicdata.caida.org/datasets/as-organizations/"
AS2ORG_BASE_DIR = BASE_DIR + "AS2Org/"
AS2ORG_DOWNLOAD_TO_DIR = AS2ORG_BASE_DIR + "downloads/"
AS2ORG_DB_DIR = AS2ORG_BASE_DIR + "db/"
AS2ORG_CSV_DIR = AS2ORG_BASE_DIR + "csv/"

AS_RELATIONSHIPS_ARCHIVE_URL = "https://publicdata.caida.org/datasets/as-organizations/"


def initialize_directories():
    if not os.path.isdir(BASE_DIR):
        raise Exception(BASE_DIR + " does not exist")
    
    if not os.path.isdir(ITDK_BASE_DIR):
        os.mkdir(ITDK_BASE_DIR)
    if not os.path.isdir(ITDK_DOWNLOAD_TO_DIR):
        os.mkdir(ITDK_DOWNLOAD_TO_DIR)
    if not os.path.isdir(ITDK_DB_DIR):
        os.mkdir(ITDK_DB_DIR)
    if not os.path.isdir(ITDK_CSV_DIR):
        os.mkdir(ITDK_CSV_DIR)

    if not os.path.isdir(AS2ORG_BASE_DIR):
        os.mkdir(AS2ORG_BASE_DIR)
    if not os.path.isdir(AS2ORG_DOWNLOAD_TO_DIR):
        os.mkdir(AS2ORG_DOWNLOAD_TO_DIR)
    if not os.path.isdir(AS2ORG_DB_DIR):
        os.mkdir(AS2ORG_DB_DIR)
    if not os.path.isdir(AS2ORG_CSV_DIR):
        os.mkdir(AS2ORG_CSV_DIR)