#!/usr/bin/python
import os
import sys
import subprocess
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('-i', '--input_dir', required=True)
    args = parser.parse_args()

    date_hour_list = os.listdir(args.input_dir)
    for date_hour in date_hour_list:
        print '%s' % date_hour

if __name__ == '__main__':
    main()
