#!/usr/bin/python
import argparse
import fileinput
from collections import defaultdict
from collections import Counter


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-tm', '--truth_modified_file', required=True)
  parser.add_argument('-x', '--examples_file', required=True)
  parser.add_argument('-e', '--entities_ccr_file', required=True)
  parser.add_argument('-m', '--mapping_file', required=True)
  args = parser.parse_args()

  entities_ccr = {}
  for line in open(args.entities_ccr_file).read().splitlines():
    entities_ccr[line.strip()] = True

  #print len(entities_ccr)

  truth = {}
  for line in open(args.truth_modified_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    key = (streamid, targetid)
    if entities_ccr.has_key(targetid):
      truth[key] = line

  #print len(truth)

  examples = {}
  for line in open(args.examples_file).read().splitlines():
    instance = line.split()
    streamid = instance[0]
    targetid = instance[1]
    key = (streamid, targetid)
    examples[key] = True

  #print len(examples)

  docids = defaultdict(list)
  for key in truth:
    if not examples.has_key(key):
      docid = key[0].split('-')[1]
      docids[docid[:16]].append(key)

  #amount = 0
  #for k in docids:
  #  amount += len(docids[k])
  #print len(docids)
  #print amount
  #exit()

  for line in fileinput.input([args.mapping_file]):
    splitted = line.split('#')
    key = splitted[1][:-1]
    if docids.has_key(key):
      for k in docids[key]:
        print '%s\t%s\t%s' % (k[0], k[1], splitted[0])

if __name__ == '__main__':
  main()

