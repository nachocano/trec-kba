#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict
from collections import Counter


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-c', '--current_entities_file', required=True)
  parser.add_argument('-t', '--total_entities_file', required=True)
  args = parser.parse_args()

  current = {}
  for line in open(args.current_entities_file).read().splitlines():
    line = line.replace('.bin', '').strip()
    current[line] = True

  for line in open(args.total_entities_file).read().splitlines():
    key = line[line.rfind('/')+1:]
    if not current.has_key(key.strip()):
      print key

if __name__ == '__main__':
  main()

