#!/usr/bin/python3
import re, properties, parse_util

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
