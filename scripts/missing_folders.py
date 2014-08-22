#!/usr/bin/python
import os
import sys
import subprocess
import argparse
import re
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-d', '--downloaded_files_txt', required=True)
    parser.add_argument('-p', '--paths', required=True)
    args = parser.parse_args()

    downloaded = {}
    for line in open(args.downloaded_files_txt).read().splitlines():
    	downloaded[line] = True

    folder_regex = re.compile(r'/(20\d{2}-\d{2}-\d{2}-\d{2})/')
    all_folders = defaultdict(list)
    for line in open(args.paths).read().splitlines():
    	fileurl = line.split()[3]
        folder = folder_regex.search(fileurl).group(1)
        to_download = fileurl.replace('s3://', 'http://s3.amazonaws.com/')
    	all_folders[folder].append(to_download)

    for folder in all_folders:
        all_folders[folder].pop()

    for folder in all_folders:
        if not downloaded.has_key(folder):
    	   for filename in all_folders[folder]:
            print filename

if __name__ == '__main__':
    main()