#!/usr/bin/python
from __future__ import division
import argparse
import time
import re
import json
from collections import defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-ff', '--test_or_train_filtered_file', required=True)
  parser.add_argument('-t', '--test_or_train_assessed_file', required=True)
  args = parser.parse_args()

  test_or_train_assessed = {}
  with open(args.test_or_train_assessed_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      test_or_train_assessed[(targetid, streamid, date_hour)] = line

  count = 0
  with open(args.test_or_train_filtered_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      key = (targetid, streamid, date_hour)
      if test_or_train_assessed.has_key(key):
        print test_or_train_assessed[key]
        count += 1
      else:
        print line

  print '%d assessed part of all' % count


if __name__ == '__main__':
  main()

