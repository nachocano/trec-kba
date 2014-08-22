#!/usr/bin/python
import os
import sys
import subprocess
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-p', '--paths', required=True)
    args = parser.parse_args()


    folder_regex = re.compile(r'/(20\d{2}-\d{2}-\d{2}-\d{2})/')
    all_folders = {}
    for line in open(args.paths).read().splitlines():
    	fileurl = line.split()[3]
        fileurl = fileurl.replace('s3://', 'http://s3.amazonaws.com/')
        print fileurl

if __name__ == '__main__':
    main()
