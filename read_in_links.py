#!/usr/bin/python3
import re, properties, parse_util

def sqlite3__read_in_links(cnxn, loc, topo_choice, ipv):
    cursor = cnxn.cursor()

    links_file = open(loc + topo_choice + properties.itdk_file_types[1], "r")

    for line in links_file:
        prefix = parse_util.link_entry_prefix.search(line)

        if prefix is not None:
            link_ID = parse_util.link_id_pattern.search(line).group()[1:]
            n1_id = None
            n1_addr = None

            tokens = re.split("\s", line)

            for token in tokens:
                if parse_util.node_id_pattern.match(token):
                    print()

                elif ipv == 4:
                    if parse_util.ipv4_link_end.match(token):
                        if n1_id is None:
                            print()

                        else:
                            sides = re.split(":", token)
                            n_ID = sides[0]
                            addr = sides[1]
                            print()

                    elif parse_util.ipv4_pattern.match(token):
                        print()

                elif ipv == 6:
                    if parse_util.ipv6_link_end.match(token):
                        if n1_id is None:
                            print()
                        else:
                            # can't split on : because that's part of IPv6 addresses
                            n_ID = parse_util.node_id_pattern.search(token)
                            addr = token[n_ID.end() + 2:]
                            ID = n_ID.group()
                            cursor.execute("INSERT INTO map_link_to_nodes (link_id, node_id_1, address_1, node_id_2, address_2) VALUES (?, );", (link_ID, ))
                            print()

                    elif parse_util.ipv6_pattern.match(token):
                        print()

    links_file.close()
