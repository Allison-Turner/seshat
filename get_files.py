#! /usr/bin/env python3

import os, shutil, gzip, bz2
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