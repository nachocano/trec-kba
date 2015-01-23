#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--train_or_test_file', required=True)
    parser.add_argument('-nr', '--non_relevant_file', required=True)
    parser.add_argument('-ot', '--output_train_or_test_relevant', required=True)

    args = parser.parse_args()

    non_relevant = {}
    with open(args.non_relevant_file) as f:
        for line in f.read().splitlines():
            line = line.split('\t')
            streamid = line[0]
            targetid = line[1]
            non_relevant[(streamid, targetid)] = True

    out = open(args.output_train_or_test_relevant, 'w')
    filtered = 0
    with open(args.train_or_test_file) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            label = int(instance[3])
            if not non_relevant.has_key((streamid, targetid)) and label != 0 and label != -1:
                out.write('%s\n' % line)
            else:
                filtered +=1
    print 'filtered %d' % filtered
    out.close()

if __name__ == '__main__':
  main()
