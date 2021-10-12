#!/usr/bin/python3
import os, subprocess, properties, log_util

def bash_wget__download(timestamp, loc, ipv, year, month, day, url, topo_choice, ext):
    if not os.path.exists(loc):
        os.mkdir(loc)

    download_log = open(loc + "download" + timestamp + ".log", "a+")


    if ipv==4:
        # Download all files to listed folder location
        for file in properties.itdk_file_types:
            download_log.write("Downloading " + topo_choice + file + ext + "\n")
            download_cmd = subprocess.Popen(["/usr/bin/wget", "-S", "-P", loc, url + year + "-" + month + "/" + topo_choice + file + ext ])
            download_cmd.communicate()
            log_util.log_cmd_results(download_cmd, download_log)

        download_log.write("Downloading itdk-run-" + year + month + day + "-dns-names.txt" + ext + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-S", "-P", loc, url + year + "-" + month + "/" + "itdk-run-" + year + month + day + "-dns-names.txt" + ext ])
        download_cmd.communicate()
        log_util.log_cmd_results(download_cmd, download_log)

        download_log.write("Downloading itdk-run-" + year + month + day + ".addrs" + ext + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-S", "-P", loc, url + year + "-" + month + "/" + "itdk-run-" + year + month + day + ".addrs" + ext ])
        download_cmd.communicate()
        log_util.log_cmd_results(download_cmd, download_log)


    if ipv==6:
        for file in properties.itdk_file_types:
            if file != ".ifaces":
                download_log.write("Downloading " + topo_choice + file + ext + "\n")
                download_cmd = subprocess.Popen(["/usr/bin/wget", "-S", "-P", loc, url + year + "-" + month + "/" + topo_choice + file + ext ])
                download_cmd.communicate()
                log_util.log_cmd_results(download_cmd, download_log)


    download_log.close()
