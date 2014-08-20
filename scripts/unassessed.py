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
      test_or_train_assessed[(targetid, streamid)] = True

  with open(args.test_or_train_filtered_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      targetid = l[0]
      streamid = l[1]
      date_hour = l[2]
      filename = l[3]
      key = (targetid, streamid)
      if not test_or_train_assessed.has_key(key):
        print '%s\t%s\t%s' % (targetid, streamid, '%s/%s' % (date_hour, filename))


if __name__ == '__main__':
  main()

