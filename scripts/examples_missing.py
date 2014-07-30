#!/usr/bin/python
import argparse
import fileinput
from collections import defaultdict
from collections import Counter

URL = 'http://s3.amazonaws.com/aws-publicdatasets/trec/kba/kba-streamcorpus-2014-v0_3_0-kba-filtered/'

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-m', '--missings_file', required=True)
  parser.add_argument('-ma', '--mapping_file', required=True)
  args = parser.parse_args()

  missings = defaultdict(list)
  for line in open(args.missings_file).read().splitlines():
    instance = line.split()
    docid = instance[0]
    targetid = instance[1]
    key = docid.split('-')[1][:16]
    missings[key].append((docid, targetid))

  for line in fileinput.input([args.mapping_file]):
    splitted = line.split('#')
    key = splitted[1][:-1]
    if missings.has_key(key):
      for k in missings[key]:
        print '%s\t%s\t%s' % (k[0], k[1], URL + splitted[0])

if __name__ == '__main__':
  main()

