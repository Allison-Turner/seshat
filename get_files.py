#! /usr/bin/env python3

import os, shutil, gzip, bz2, glob, math, datetime
import requests
from bs4 import BeautifulSoup


def get_file_by_url(file_url, output_filename):
    raw_resp = requests.get(file_url)

    if raw_resp.status_code != 200:
        raise Exception("requests.get() return code: {}".format(raw_resp.status_code))

    with open(output_filename, "wb+") as outf:
        outf.write(raw_resp.content)



def decompress_file(input_filename, output_filename=None):
    if ".gz" in input_filename:
        if output_filename is None:
            output_filename = input_filename.removesuffix(".gz")

        with gzip.open(input_filename, "rb") as inf:
            with open(output_filename, "wb") as outf:
                shutil.copyfileobj(inf, outf)

        os.remove(input_filename)

    elif ".bz2" in input_filename:
        if output_filename is None:
            output_filename = input_filename.removesuffix(".bz2")

        with bz2.open(input_filename, "rb") as inf:
            with open(output_filename, "wb") as outf:
                shutil.copyfileobj(inf, outf)

        os.remove(input_filename)

    return output_filename



def get_links_from_html_page(web_page_url):
    resp = requests.get(web_page_url)

    page_soup = BeautifulSoup(resp.content, 'html.parser')

    links_on_page = []

    for a_href in page_soup.find_all('a'):
        link = a_href.get('href')
        if '?' in link or link in web_page_url:
            continue
        else:
            links_on_page.append(link.replace("/", ""))

    return links_on_page


def get_contemporary_as2org_release_for_itdk_version(itdk_release_date, as2org_archive_url, download_dir):
    fields = itdk_release_date.split("-")
    itdk_release_year = int(fields[0])
    itdk_release_month = int(fields[1])

    as2org_files = get_links_from_html_page(as2org_archive_url)

    candidate_files = []

    for f in as2org_files:
        if ".as-org2info.txt.gz" in f:
            dt = f.replace(".as-org2info.txt.gz", "")
            year = dt[0:4]
            month = dt[4:6]
            day = dt[6:]

            if math.fabs(itdk_release_year - int(year)) > 1:
                continue

            candidate_files.append("-".join([year, month, day]))

        if ".as-org2info.jsonl.gz" in f:
            continue

    file_name = None
    time_diff_in_months = None

    for f in candidate_files:
        dt = f.split("-")
        year = int(dt[0])
        month = int(dt[1])
        day = int(dt[2])

        if (year == itdk_release_year) and (month == itdk_release_month):
            file_name = "{0}{1:0>2}{2:0>2}".format(year, month, day) + ".as-org2info.txt.gz"
            break

        elif file_name is None:
            file_name = "{0}{1:0>2}{2:0>2}".format(year, month, day) + ".as-org2info.txt.gz"
            time_diff_in_months = math.fabs((itdk_release_year - year) * 12) + (itdk_release_month - month)

        else:
            # if negative, later than ITDK release
            time_diff = math.fabs(((itdk_release_year - year) * 12) + (itdk_release_month - month))
            
            if time_diff < time_diff_in_months:
                file_name = "{0}{1:0>2}{2:0>2}".format(year, month, day) + ".as-org2info.txt.gz"
                time_diff_in_months = time_diff

    get_file_by_url(as2org_archive_url + file_name, download_dir + file_name)
    return decompress_file(download_dir + file_name)



def get_itdk_files(base_archive_url, download_dir):
    itdk_releases = get_links_from_html_page(base_archive_url)

    latest_release = itdk_releases[-1]

    print("{} Downloading ITDK files from {}".format(datetime.datetime.now(), latest_release))

    latest_version_url = base_archive_url + "/" + latest_release

    available_files = get_links_from_html_page(latest_version_url)

    itdk_dir = download_dir + latest_release + "/"

    if not os.path.exists(itdk_dir):
        os.mkdir(itdk_dir)

    local_files = glob.glob(itdk_dir + "*.*")
    
    files_to_get = []
    for af in available_files:
        match_found = False

        for lf in local_files:
            if os.path.basename(lf) in af:
                match_found = True
                break
        if match_found is False:
            files_to_get.append(af)

    for f in files_to_get:
        get_file_by_url(latest_version_url + "/" + f, itdk_dir + f)
        decompress_file(itdk_dir + f)

    print("{} Finished downloading and decompressing latest ITDK edition files".format(datetime.datetime.now()))

    return latest_release, glob.glob(itdk_dir + "*.*")