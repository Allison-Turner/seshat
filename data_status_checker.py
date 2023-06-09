#! /usr/bin/env python3

from glob import glob
from get_files import get_available_dataset_releases, check_for_files_to_download

def check_download_status_for_each_itdk_version(itdk_archive_url, itdk_download_dir):
    itdk_releases = get_available_dataset_releases(itdk_archive_url)

    download_status = {}

    for archive_date in itdk_releases:
        missing_files = check_for_files_to_download(itdk_archive_url, archive_date, itdk_download_dir)

        if len(missing_files) > 0:
            download_status[archive_date] = False
        else:
            download_status[archive_date] = True

    return download_status

def check_for_itdk_release_csv_files(itdk_versions, itdk_csv_dir):
    itdk_csvs = glob(itdk_csv_dir + "*.csv")