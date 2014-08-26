#!/usr/bin/python
from __future__ import division
import argparse
import math
from collections import defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-t', '--train_file_assessed_unassessed_sorted', required=True)
  parser.add_argument('-p', '--split_percentage', required=False, type=float, default=0.2)
  args = parser.parse_args()

  examples_per_entity = defaultdict(list)
  with open(args.train_file_assessed_unassessed_sorted) as f:
    for line in f.read().splitlines():
      l = line.split()
      targetid = l[1]
      examples_per_entity[targetid].append(line)

  count = 0
  for targetid in examples_per_entity:
    count += len(examples_per_entity[targetid])

  first_elements = []
  last_elements = []
  for targetid in examples_per_entity:
    delimiter = int(math.ceil(len(examples_per_entity) * args.split_percentage))
    first_elements.extend(examples_per_entity[targetid][:delimiter])
    last_elements.extend(examples_per_entity[targetid][delimiter:])

  assert count == (len(first_elements) + len(last_elements))

  for e in first_elements:
    print e
  for e in last_elements:
    print e 

if __name__ == '__main__':
  main()

