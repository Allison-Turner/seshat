#! /usr/bin/env python3

import os, datetime, re, glob



def parse_nodes_file_to_csv(nodes_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    nodes_csv = csv_directory + itdk_version + "." + os.path.basename(nodes_file) + ".csv"

    with open(nodes_file, "r") as inf:
        with open(nodes_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", "").replace(":", ""))

                node_addrs = fields[2:]

                for addr in node_addrs:
                    outf.write("{},{}\n".format(node_id, addr))


       
def parse_nodes_geo_file_to_csv(nodes_geo_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    nodes_geo_csv = csv_directory + itdk_version + "." + os.path.basename(nodes_geo_file) + ".csv"

    with open(nodes_geo_file, "r") as inf:
        with open(nodes_geo_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", "").replace(":", ""))
                continent = fields[2]
                country = fields[3]

                rest_of_line = " ".join(fields[4:])

                result = re.search("(\-)?[0-9]+\.[0-9]+(\s)+(\-)?[0-9]+\.[0-9]+", rest_of_line)

                if result is not None:
                    coords = result.group().split()

                    lat_index = rest_of_line.index(coords[0])

                    latitude = float(coords[0])
                    longitude = float(re.sub("[A-Za-z]", "", coords[1]))

                    rest_of_line = rest_of_line[:lat_index].replace(",", "")
                else:
                    continue

                result = re.search("([0-9]{1,3}|[A-Z]{2,3})\s", rest_of_line)

                if result is not None:
                    region = result.group().replace(" ", "")

                    if region.isspace() or len(region) == 0:
                        region = None
                    
                    rest_of_line = rest_of_line.replace(region, "")
                else:
                    region = None

                city = rest_of_line.strip().replace(",", "")

                if city.isspace() or len(city) == 0:
                    city = None
                
                outf.write("{},{},{},{},{},{},{}\n".format(node_id, continent, country, region, city, latitude, longitude))



def parse_nodes_as_file_to_csv(nodes_as_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    nodes_as_csv = csv_directory + itdk_version + "." + os.path.basename(nodes_as_file) + ".csv"

    with open(nodes_as_file, "r") as inf:
        with open(nodes_as_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                node_id = int(fields[1].replace("N", ""))
                as_num = int(fields[2])

                outf.write("{},{}\n".format(node_id, as_num))



def parse_links_file_to_csv(links_file, itdk_version, csv_directory):
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)

    links_csv = csv_directory + itdk_version + "." + os.path.basename(links_file) + ".csv"

    with open(links_file, "r") as inf:
        with open(links_csv, "w+") as outf:
            for line in inf:
                if line.startswith("#"):
                    continue

                fields = line.strip().split()

                link_id = int(fields[1].replace("L", "").replace(":", ""))

                first_node = None
                first_node_addr = None

                for tuple in fields[2:]:
                    subfields = tuple.split(':', 1)

                    if len(subfields) > 1:
                        node_id = int(subfields[0].replace("N", ""))
                        ip_addr = subfields[1]

                    else:
                        node_id = int(subfields[0].replace("N", ""))
                        ip_addr = None

                    if first_node is None:
                        first_node = node_id
                        first_node_addr = ip_addr
                    else:
                        outf.write("{},{},{},{},{}\n".format(link_id, first_node, first_node_addr, node_id, ip_addr))



def convert_as2org_file_to_csvs(as2org_file, csv_directory):
    dt = os.path.basename(as2org_file).replace(".as-org2info.txt", "")

    year = dt[0:4]
    month = dt[4:6]
    day = dt[6:]

    asn_outfile = csv_directory + "-".join([year, month, day]) + ".as2org.asn.csv"
    org_outfile = csv_directory + "-".join([year, month, day]) + ".as2org.org.csv"

    with open(as2org_file, "r") as inf:
        with open(asn_outfile, "w+") as asn_outf:
            with open(org_outfile, "w+") as org_outf:
                for line in inf:
                    if line.startswith("#"):
                        continue

                    fields = line.strip().replace(",", "").split("|")

                    # organization entry
                    if len(fields) == 5:
                        org_id = fields[0]
                        changed = fields[1]
                        org_name = fields[2]
                        country = fields[3]
                        source = fields[4]

                        org_outf.write("{},{},{},{},{}\n".format(org_id, changed, org_name, country, source))

                    # AS number entry
                    elif len(fields) == 6:
                        as_num = fields[0]
                        changed = fields[1]
                        as_name = fields[2]
                        org_id = fields[3]
                        opaque_id = fields[4]
                        source = fields[5]

                        asn_outf.write("{},{},{},{},{},{}\n".format(as_num, changed, as_name, org_id, opaque_id, source))

    return asn_outfile, org_outfile



def convert_itdk_files_to_csvs(itdk_files, itdk_version, csv_directory):
    nodes_file = None
    nodes_as_file = None
    nodes_geo_file = None
    links_file = None
    ifaces_file = None

    for f in itdk_files:
        fname = os.path.basename(f)

        if fname.endswith(".ifaces"):
            ifaces_file = f
        elif fname.endswith(".links"):
            links_file = f
        elif fname.endswith(".nodes.as"):
            nodes_as_file = f
        elif fname.endswith(".nodes.geo"):
            nodes_geo_file = f
        elif fname.endswith(".nodes"):
            nodes_file = f
        elif fname.endswith(".geo-re.jsonl"):
            continue
        elif fname.endswith(".addrs"):
            continue
        elif fname.endswith("dns-names.txt"):
            continue

    itdk_csvs = glob.glob(csv_directory + "*.csv")

    generate_nodes_csv = True
    generate_nodes_as_csv = True
    generate_nodes_geo_csv = True
    generate_links_csv = True

    csv_files = []

    for f in itdk_csvs:
        if itdk_version not in f:
            continue

        if ".nodes.as" in f:
            generate_nodes_as_csv = False
            csv_files.append(f)
        elif ".nodes.geo" in f:
            generate_nodes_geo_csv = False
            csv_files.append(f)
        elif ".nodes" in f:
            generate_nodes_csv = False
            csv_files.append(f)
        elif ".links" in f:
            generate_links_csv = False
            csv_files.append(f)

    if generate_nodes_csv is True:
        print("{} Processing .nodes file".format(datetime.datetime.now()))
        nodes_csv = parse_nodes_file_to_csv(nodes_file, itdk_version, csv_directory)
        csv_files.append(nodes_csv)

    if generate_nodes_geo_csv is True:
        print("{} Processing .nodes.geo file".format(datetime.datetime.now()))
        nodes_geo_csv = parse_nodes_geo_file_to_csv(nodes_geo_file, itdk_version, csv_directory)
        csv_files.append(nodes_geo_csv)

    if generate_nodes_as_csv is True:
        print("{} Processing .nodes.as file".format(datetime.datetime.now()))
        nodes_as_csv = parse_nodes_as_file_to_csv(nodes_as_file, itdk_version, csv_directory)
        csv_files.append(nodes_as_csv)

    if generate_links_csv is True:
        print("{} Processing .links file".format(datetime.datetime.now()))
        links_csv = parse_links_file_to_csv(links_file, itdk_version, csv_directory)
        csv_files.append(links_csv)

    print("{} CSV files: [{}]".format(datetime.datetime.now(), ", ".join(csv_files) ))

    return csv_files