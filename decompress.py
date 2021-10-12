#!/usr/bin/python3
import os, subprocess, properties, log_util

def bzip2__decompress(timestamp, loc, ipv, topo_choice):
    # Prep log file
    decompress_log = open(loc + "decompression"+ timestamp + ".log", "a")

    #decompress archive files
    if ipv==4:
        # Decompress IPv4 archives
        decompress_log.write("IPv4 Archives\n")

        for file in properties.itdk_file_types:
            decompress_log.write("Decompressing " + loc + topo_choice + file + ".bz2\n")
            decompress_cmd = subprocess.Popen(["/usr/bin/bzip2", "-d", loc + topo_choice + file + ".bz2"])
            decompress_cmd.communicate()
            log_util.log_cmd_results(decompress_cmd, decompress_log)


    if ipv==6:
        # Decompress IPv6 archives (no ifaces file for this topology)
        decompress_log.write("IPv6 Archives\n")

        for file in properties.itdk_file_types:
            if file != ".ifaces":
                decompress_log.write("Decompressing " + loc + topo_choice + file + ".bz2\n")
                decompress_cmd = subprocess.Popen(["/usr/bin/bzip2", "-d", loc + topo_choice + file + ".bz2"])
                decompress_cmd.communicate()
                log_util.log_cmd_results(decompress_cmd, decompress_log)


    decompress_log.close()
