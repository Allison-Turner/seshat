#!/usr/bin/python3
import os, subprocess, pyodbc, properties, log_util, sqlite3

def sqlite__connect(driver, server, name, user, pwd):
    # driver = properties.db__driver(db)
    # server = properties.db__server(db)
    # name = properties.db__name(db)
    # user = properties.db__user(db)
    # pwd = properties.db__pwd(db)

    # Connect to database
    cnxn = sqlite3.connect("DRIVER={" + driver + "};SERVER=" + server + ";DATABASE=" + name + ";UID=" + user + ";PWD=" + pwd)
    #cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    #cnxn.setencoding(encoding='utf-8')

    return cnxn


def create_schema(cursor, user, day, month, year, ipv):
    # user = properties.db__user(db)

    # ipv = properties.itdk_version__ip_version(itdkv)
    # year = properties.itdk_version__year(itdkv)
    # month = properties.itdk_version__month(itdkv)
    # day = properties.itdk_version__day(itdkv)

    # Create schemas and tables
    cursor.execute("CREATE SCHEMA IF NOT EXISTS " + day + "-" + month + "-" + year + "_" + "ipv" + str(ipv) + "_topology AUTHORIZATION " + user +
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
