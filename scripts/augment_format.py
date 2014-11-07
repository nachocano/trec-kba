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
  parser.add_argument('-json', '--json_file', required=True)
  args = parser.parse_args()


  tmp_file = args.json_file + '.partial'
  with open(args.json_file, 'r') as f:
    with open(tmp_file, 'w') as tmp:
      json_file = json.load(f)
      for e in json_file:
        tmp.write(json.dumps(e))
        tmp.write('\n')
  rename(tmp_file, args.json_file)
  
if __name__ == '__main__':
  main()

