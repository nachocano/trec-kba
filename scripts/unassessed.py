#!/usr/bin/python
from __future__ import division
import argparse
import time
import re
import json
from collections import defaultdict
from collections import Counter

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-ff', '--test_or_train_filtered_file', required=True)
  parser.add_argument('-t', '--test_or_train_assessed_file', required=True)
  parser.add_argument('-mt', '--modified_before_after_truth_file', required=True)
  args = parser.parse_args()

  ground_truth = defaultdict(list)
  with open(args.modified_before_after_truth_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split('\t')
      targetid = l[3]
      streamid = l[2]
      date_hour = l[7]
      candidate_relevance = int(l[5])
      ground_truth[(targetid, streamid, date_hour)].append(candidate_relevance)

  test_or_train_assessed = {}
  with open(args.test_or_train_assessed_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      test_or_train_assessed[(targetid, streamid, date_hour)] = line

  count = 0
  count_missing = 0
  missing_assessed = []
  with open(args.test_or_train_filtered_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      key = (targetid, streamid, date_hour)
      if test_or_train_assessed.has_key(key):
        #print test_or_train_assessed[key]
        count += 1
      else:
        # there were few entries missing in the assessed test and train, we may got them now
        if ground_truth.has_key(key):
          relevances = ground_truth[key]
          relevance = relevances[0]
          if len(relevances) > 1:
            counts = defaultdict(int)
            for r in relevances:
              counts[r] += 1
            most_frequent_value = 0
            most_frequent_rel = 0
            for key, value in sorted(counts.iteritems(), key=lambda (k,v) : (k,v))[::-1]:
              # most frequent or max in case of a tie
              if value > most_frequent_value:
                most_frequent_value = value
                most_frequent_rel = key
            relevance = most_frequent_rel
          missing_assessed.append((relevance, line))
          count_missing += 1
        else:
          print line

  print '%d assessed that are included in all' % count
  print '%d assessed that were missing' % count_missing

  if count_missing > 0:
    print 'missing'
    for l in missing_assessed:
      print l[0], l[1]

if __name__ == '__main__':
  main()

