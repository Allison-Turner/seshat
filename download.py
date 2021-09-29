#!/usr/bin/python3
import os, subprocess, properties, log_util

def ubuntu__download(timestamp, itdkv, loc):
    if not os.path.exists(loc):
        os.mkdir(loc)

    download_log = open(loc + "download" + timestamp + ".log", "a+")


    ipv = properties.itdk_version__ip_version(itdkv)
    year = properties.itdk_version__year(itdkv)
    month = properties.itdk_version__month(itdkv)
    day = properties.itdk_version__day(itdkv)
    url = properties.itdk_version__url(itdkv)
    topo_choice = properties.itdk_version__topo_choice(itdkv)
    ext = properties.itdk_version__compression_extension(itdkv)


    if ipv==4:
        # Download all files to listed folder location
        for file in properties.itdk_file_types:
            download_log.write("Downloading " + topo_choice + file + ext + "\n")
            download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", loc, url + year + "-" + month + "/" + topo_choice + file + ext ])
            download_cmd.communicate()
            log_util.log_cmd_results(download_cmd, download_log)

        download_log.write("Downloading itdk-run-" + year + month + day + "-dns-names.txt" + ext + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", loc, url + year + "-" + month + "/" + "itdk-run-" + year + month + day + "-dns-names.txt" + ext ])
        download_cmd.communicate()
        log_util.log_cmd_results(download_cmd, download_log)

        download_log.write("Downloading itdk-run-" + year + month + day + ".addrs" + extension + "\n")
        download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", loc, url + year + "-" + month + "/" + "itdk-run-" + year + month + day + ".addrs" + ext ])
        download_cmd.communicate()
        log_util.log_cmd_results(download_cmd, download_log)


    if ipv==6:
        for file in properties.itdk_file_types:
            if file != ".ifaces":
                download_log.write("Downloading " + topo_choice + file + ext + "\n")
                download_cmd = subprocess.Popen(["/usr/bin/wget", "-a", "download" + timestamp + ".log", "-S", "-P", loc, url + year + "-" + month + "/" + topo_choice + file + ext ])
                download_cmd.communicate()
                log_util.log_cmd_results(download_cmd, download_log)


    download_log.close()
