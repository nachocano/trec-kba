#!/usr/bin/python
import argparse
import time
from collections import defaultdict
from os import listdir
from os.path import isfile, join
from os import rename
import json
import numpy as np


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-json', '--json_folder', required=True)
  args = parser.parse_args()


  onlyfiles = [ join(args.json_folder,f) for f in listdir(args.json_folder) if isfile(join(args.json_folder,f)) ]

  for filename in onlyfiles:
    tmp_file = filename + '.partial'
    with open(filename, 'r') as f:
      with open(tmp_file, 'w') as tmp:
        json_file = json.load(f)
        for d in json_file:
          tmp.write(json.dumps(d))
          tmp.write('\n')
    rename(tmp_file, filename)
  
if __name__ == '__main__':
  main()

