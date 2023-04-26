#! /usr/bin/env python3

import config
import requests, os, glob, shutil, gzip, bz2
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



def get_links_from_html_page(web_page_url):
    resp = requests.get(web_page_url)

    page_soup = BeautifulSoup(resp.content, 'html.parser')

    itdk_releases = []

    for a_href in page_soup.find_all('a'):
        link = a_href.get('href')
        if '?' in link or link in web_page_url:
            continue
        else:
            itdk_releases.append(link.replace("/", ""))

    return itdk_releases




def __main__():
    itdk_releases = get_links_from_html_page(config.BASE_ARCHIVE_URL)

    latest_version_url = config.BASE_ARCHIVE_URL + "/" + itdk_releases[-1]

    available_files = get_links_from_html_page(latest_version_url)

    itdk_dir = config.DOWNLOAD_TO_DIR + itdk_releases[-1] + "/"

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




if __name__ == '__main__':
    __main__()