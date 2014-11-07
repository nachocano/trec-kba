#!/usr/bin/python
from __future__ import division
import argparse
import time
import re
from collections import defaultdict
from collections import Counter

def read_file(train_test, filename, entity_name):
  with open(filename) as f:
    for line in f.read().splitlines():
      delimiter = line.find('[')
      fixed = line[:delimiter-1]
      words = line[delimiter:]
      l = fixed.strip().split()
      targetid = l[1]
      if entity_name in targetid:
        words = words.replace('[', '').replace(']', '')
        wordvec = words.split(',')
        streamid = l[0]
        date_hour = l[2]
        train_test[targetid][streamid] = wordvec


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-c', '--clusters_file', required=True)
  parser.add_argument('-t', '--all_test_file', required=True)
  parser.add_argument('-tr', '--all_train_file', required=True)
  parser.add_argument('-e', '--entity_name', required=True)
  args = parser.parse_args()

  train_test = defaultdict(defaultdict)
  read_file(train_test, args.all_test_file, args.entity_name)
  read_file(train_test, args.all_train_file, args.entity_name)

  entities = defaultdict(lambda : defaultdict(list))
  with open(args.clusters_file) as f:
    for line in f.read().splitlines():
      name, cluster, streamid = line.split()
      if args.entity_name in name:
        entities[name][cluster].append(streamid)

  counters = defaultdict(lambda: defaultdict(Counter))
  for targetid in entities:
    for cluster in entities[targetid]:
      for streamid in entities[targetid][cluster]:
        for word in train_test[targetid][streamid]:
          counters[targetid][cluster][word.strip()] += 1

  for targetid in counters:
    for cluster in counters[targetid]:
      print counters[targetid][cluster].most_common(10)


if __name__ == '__main__':
  main()

