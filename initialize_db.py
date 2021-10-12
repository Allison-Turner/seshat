#!/usr/bin/python3
import os, subprocess, pyodbc, properties, log_util, sqlite3

def sqlite__connect(loc, day, month, year, ipv, driver, server, name, user, pwd):

    db_name = "ITDK_" + day + "_" + month + "_" + year + "_ipv" + str(ipv)
    db_file = loc + db_name + ".db"

    print("DB File: " + db_file)

    # Connect to database
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()

    return cnxn



def sqlite__create_schema(cursor, user, day, month, year, ipv):

    # Create tables
    cursor.execute("CREATE TABLE IF NOT EXISTS map_address_to_node(" +
    """
    address inet,
    node_id integer
    );
    """);

    cursor.execute("CREATE TABLE IF NOT EXISTS map_link_to_nodes(" +
    """
    link_id integer,
    node_id_1 integer,
    address_1 inet, -- optional
    node_id_2 integer,
    address_2 inet, -- optional
    relationship text
    );
    """);

    cursor.execute("CREATE TABLE IF NOT EXISTS map_node_to_asn(" +
    """
    node_id integer,
    as_number integer
    );
    """);



def create_schema(cursor, user, day, month, year, ipv):

    # Create schemas and tables
    cursor.execute("CREATE SCHEMA IF NOT EXISTS ipv" + str(ipv) + "_topology" +
    """
      CREATE TABLE map_address_to_node(
        address inet,
        node_id integer
      )
      CREATE TABLE map_link_to_nodes(
        link_id integer,
        node_id_1 integer,
        address_1 inet, -- optional
        node_id_2 integer,
        address_2 inet, -- optional
        relationship text
      )
      CREATE TABLE map_node_to_asn(
        node_id integer,
        as_number integer
      );
    """);
