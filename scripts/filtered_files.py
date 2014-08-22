#!/usr/bin/python
from __future__ import division
import argparse
import time
import re
import json
from collections import defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-w', '--whole_file', required=True)
  parser.add_argument('-e', '--entities_file', required=True)
  parser.add_argument('-t', '--train_file', required=True)
  parser.add_argument('-tr', '--test_file', required=True)
  args = parser.parse_args()

  filter_topics = json.load(open(args.entities_file))
  entities = {}
  for e in filter_topics['targets']:
    if e['training_time_range_end']:
      entities[str(e['target_id'])] = str(e['training_time_range_end'])
  
  folder_regex = re.compile(r'/(20\d{2}-\d{2}-\d{2}-\d{2})/')

  train = open(args.train_file, 'w')
  test = open(args.test_file, 'w')

  with open(args.whole_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      if len(l) != 3:
        continue
      streamid = l[0]
      targetid = l[1]
      date_hour = folder_regex.search(l[2]).group(1)
      filename = l[2][l[2].rfind('/')+1:]
      if date_hour < entities[targetid]:
        train.write('%s %s %s %s\n' % (targetid, streamid, date_hour, filename))
      else:
        test.write('%s %s %s %s\n' % (targetid, streamid, date_hour, filename))

  train.close()
  test.close()

if __name__ == '__main__':
  main()

