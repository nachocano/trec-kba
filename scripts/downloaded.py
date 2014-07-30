#!/usr/bin/python
import argparse
import os
from collections import defaultdict

URL = 'http://s3.amazonaws.com/aws-publicdatasets/trec/kba/kba-streamcorpus-2014-v0_3_0-kba-filtered/'

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-m', '--missing_entries_file', required=True)
  parser.add_argument('-i', '--input_dir', required=True)
  args = parser.parse_args()

  missings = defaultdict(list)
  for line in open(args.missing_entries_file).read().splitlines():
    instance = line.split()
    docid = instance[0]
    targetid = instance[1]
    fileurl = instance[2]
    filename = fileurl[fileurl.rfind('/')+1:]
    missings[filename].append((docid, targetid))

  downloaded = {}
  for root, directories, files in os.walk(args.input_dir):
    for f in files:
      downloaded[f] = True

  for key in missings:
    if downloaded.has_key(key):
      for l in missings[key]:
        print "%s\t%s\t%s" % (l[0], l[1], key)

if __name__ == '__main__':
  main()

