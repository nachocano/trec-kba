#!/usr/bin/python
from __future__ import division
import os
import sys
import argparse

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--directory', required=True)
    parser.add_argument('-s', '--change_output_script', required=True)
    parser.add_argument('-od', '--output_directory', required=True)

    args = parser.parse_args()

    for f in os.listdir(args.directory):
        filename = os.path.join(args.directory,f)
        outputfilename = os.path.join(args.output_directory,f)
        if os.path.isfile(filename) and '.gz' not in filename:
            cmd = 'python %s -r %s > %s' % (args.change_output_script, filename, outputfilename)
            print cmd
            os.system(cmd)
            cmd = 'cat %s | gzip > %s.gz' % (outputfilename, outputfilename)
            print cmd
            os.system(cmd)
  
if __name__ == '__main__':
  main()
