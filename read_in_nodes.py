#!/usr/bin/python3
import os, re, subprocess, properties, parse_util

def debian__read_in_nodes(cursor, loc, topo_choice, day, month, year, ipv):

    # ipv = properties.itdk_version__ip_version(itdkv)
    # year = properties.itdk_version__year(itdkv)
    # month = properties.itdk_version__month(itdkv)
    # day = properties.itdk_version__day(itdkv)
    # topo_choice = properties.itdk_version__topo_choice(itdkv)

    # Open nodes file to begin extracting node objects
    nodes_file = open(loc + topo_choice + properties.itdk_file_types[0], "r")

    found = 0

    for line in nodes_file:
        # Read in node objects
        prefix = parse_util.node_entry_prefix.search(line)

        if prefix is not None:
            # Parse node ID
            n_ID = parse_util.node_id_pattern.search(line).group()[1:]

            # Split entry by whitespace
            tokens = re.split("\s", line)

            # Add node aliases
            for token in tokens:
                if ipv == 4 and parse_util.ipv4_pattern.match(token):
                    cursor.execute("INSERT INTO " + day + "-" + month + "-" + year + "_" + "ipv" + ipv + "_topology.map_address_to_node (address, node_id) VALUES (?, ?);", (token, n_ID))

                elif ipv == 6 and parse_util.ipv6_pattern.match(token):
                    cursor.execute("INSERT INTO " + day + "-" + month + "-" + year + "_" + "ipv" + ipv + "_topology.map_address_to_node (address, node_id) VALUES (?, ?);", (token, n_ID))

            # Save all new entries to database from this line
            cursor.commit()

            # Stop parsing after 100 records for development purposes
            found += 1
            if found > 100:
                break

    nodes_file.close()


def sqlite3__read_in_nodes(cnxn, loc, topo_choice, ipv):
    cursor = cnxn.cursor()

    # Open nodes file to begin extracting node objects
    nodes_file = open(loc + topo_choice + properties.itdk_file_types[0], "r")

    found = 0

    for line in nodes_file:
        # Read in node objects
        prefix = parse_util.node_entry_prefix.search(line)

        if prefix is not None:
            # Parse node ID
            n_ID = parse_util.node_id_pattern.search(line).group()[1:]

            # Split entry by whitespace
            tokens = re.split("\s", line)

            # Add node aliases
            for token in tokens:
                if ipv == 4 and parse_util.ipv4_pattern.match(token):
                    cursor.execute("INSERT INTO map_address_to_node (address, node_id) VALUES (?, ?);", (token, n_ID))

                elif ipv == 6 and parse_util.ipv6_pattern.match(token):
                    cursor.execute("INSERT INTO map_address_to_node (address, node_id) VALUES (?, ?);", (token, n_ID))

                cnxn.commit()
                
            # Stop parsing after 100 records for development purposes
            found += 1
            if found > 100:
                break

    nodes_file.close()
