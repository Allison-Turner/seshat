#!/usr/bin/python3
import os, subprocess, pyodbc, properties, log_util, sqlite3

def sqlite__connect(loc, day, month, year, ipv, driver, server, name, user, pwd):
    # driver = properties.db__driver(db)
    # server = properties.db__server(db)
    # name = properties.db__name(db)
    # user = properties.db__user(db)
    # pwd = properties.db__pwd(db)

    db_name = "ITDK_" + day + "_" + month + "_" + year + "_ipv" + str(ipv)
    db_file = loc + db_name + ".db"

    print("DB File: " + db_file)

    # Connect to database
    # cnxn = sqlite3.connect("DRIVER={" + driver + "};SERVER=" + server + ";DATABASE=" + db_file + ";UID=" + user + ";PWD=" + pwd)
    #cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    #cnxn.setencoding(encoding='utf-8')
    cnxn = sqlite3.connect(db_file)
    cursor = cnxn.cursor()
    # cursor.execute("ATTACH DATABASE \'" + db_file + "\' AS " + db_name + ";")

    return cnxn



def sqlite__create_schema1(cursor, user, day, month, year, ipv):

    # Create schemas and tables
    cursor.execute("CREATE TABLE map_address_to_node(" +
    """(
    address inet,
    node_id integer
    );
    """);
    cursor.execute("CREATE TABLE map_link_to_nodes(" +
    """
    link_id integer,
    node_id_1 integer,
    address_1 inet, -- optional
    node_id_2 integer,
    address_2 inet, -- optional
    relationship text
    );
    """);

    cursor.execute("CREATE TABLE map_node_to_asn(" +
    """
    node_id integer,
    as_number integer
    );
    """);
    cursor.commit()

def sqlite__create_schema(cursor, user, day, month, year, ipv):

    # Create schemas and tables
    cursor.execute("CREATE TABLE ITDK_" + day + "_" + month + "_" + year + "_ipv" + str(ipv) + ".map_address_to_node(" +
    """(
    address inet,
    node_id integer
    );
    """);
    cursor.execute("CREATE TABLE ITDK_" + day + "_" + month + "_" + year + "_ipv" + str(ipv) + ".map_link_to_nodes(" +
    """
    link_id integer,
    node_id_1 integer,
    address_1 inet, -- optional
    node_id_2 integer,
    address_2 inet, -- optional
    relationship text
    );
    """);

    cursor.execute("CREATE TABLE ITDK_" + day + "_" + month + "_" + year + "_ipv" + str(ipv) + ".map_node_to_asn(" +
    """
    node_id integer,
    as_number integer
    );
    """);
    cursor.commit()


def create_schema(cursor, user, day, month, year, ipv):
    # user = properties.db__user(db)

    # ipv = properties.itdk_version__ip_version(itdkv)
    # year = properties.itdk_version__year(itdkv)
    # month = properties.itdk_version__month(itdkv)
    # day = properties.itdk_version__day(itdkv)

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
