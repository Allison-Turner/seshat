#!/usr/bin/python3
import re, properties, parse_util

def sqlite3__read_in_links(cnxn, loc, topo_choice, ipv):
    cursor = cnxn.cursor()

    links_file = open(loc + topo_choice + properties.itdk_file_types[1], "r")

    found = 0

    for line in links_file:
        print("\nLine: " + line)
        prefix = parse_util.link_entry_prefix.search(line)

        if prefix is not None:
                link_ID = parse_util.link_id_pattern.search(line).group()[1:]
                n1_id = None
                n1_addr = None

                # split file line into token array, using whitespace as delimiter
                tokens = re.split("\s", line)

                for token in tokens:
                    print("\nToken: " + token)
                    if ipv == 4:

                        if parse_util.ipv4_link_end.match(token):
                            # extract node ID and interface address
                            sides = re.split(":", token)
                            n_ID = sides[0]
                            addr = sides[1]

                            if n1_id is None:
                                # assign node ID just identified to be source node
                                n1_id = n_ID
                                n1_addr = addr

                            else:
                                # HYPERLINKS AND PLACEHOLDER NODES!!!
                                # assign node ID & interface address to new dest node, insert into table
                                cursor.execute("INSERT INTO map_link_to_nodes(link_id, node_id_1, address_1, node_id_2, address_2) VALUES (?, ?, ?, ?, ?);", (link_ID, n1_id, n1_addr, n_ID, addr))

                        # no interface address given for this node
                        elif parse_util.node_id_pattern.match(token):

                            if n1_id is None:
                                n1_id = token

                            else:
                                cursor.execute("INSERT INTO map_link_to_nodes(link_id, node_id_1, address_1, node_id_2, address_2) VALUES (?, ?, ?, ?, ?);", (link_ID, n1_id, n1_addr, token, None))

                    if ipv == 6:
                        # extract node ID and interface address
                        if parse_util.ipv6_link_end.match(token):

                            if n1_id is None:
                                # assign node ID just identified to be source node
                                # can't split on : because that's part of IPv6 addresses
                                n_ID = parse_util.node_id_pattern.search(token)
                                addr = token[n_ID.end() + 2:]
                                ID = n_ID.group()

                            else:
                                print("assign node ID & interface address to new dest node, insert into table")

                        elif parse_util.node_id_pattern.match(token):

                            if n1_id is None:
                                print("assign identified node ID to be source")

                            else:
                                print("assign identified node ID to be dest, insert into table")

        # limit reads to 100 for development purposes
        found +=1
        if found > 10000:
            break

    links_file.close()
