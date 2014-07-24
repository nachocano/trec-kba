#!/usr/bin/python
from __future__ import division
import os
import sys
import subprocess
import traceback
import zipimport
import re
import argparse
import fileinput
import string
import time
from math import log, ceil
from cStringIO import StringIO
from collections import defaultdict
from collections import Counter


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-t', '--truth_file', required=True)
  args = parser.parse_args()

  truth_counts = defaultdict(list)
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    relevance = instance[5]
    key = (streamid, targetid)
    truth_counts[key].append(relevance)

  majority_relevance = {}
  for key in truth_counts:
    counter = Counter(truth_counts[key])
    majority_relevance[key] = counter.most_common()[0][0]

  truth = {}
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    date = instance[7]
    key = (streamid, targetid)
    truth[key] = (majority_relevance[key], date)

  counts = defaultdict(int)
  for key in truth:
    counts[truth[key][0]] += 1

  print counts

if __name__ == '__main__':
  main()

