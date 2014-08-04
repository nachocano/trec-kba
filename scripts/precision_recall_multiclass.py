#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict


def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--pr_txt_file', required=True)
    parser.add_argument('-m', '--mode', required=True)
    args = parser.parse_args()

    assert(args.mode == 'uv' or args.mode == 'rnr')

    with open(args.pr_txt_file) as f:
        for line in f.read().splitlines():
            s = line.strip().split()
            prob_garbage = float(s[0])
            prob_neutral = float(s[1])
            prob_useful = float(s[2])
            prob_vital = float(s[3])
            pred = int(s[4])
            truth = int(s[5])
            relevance = None
            probability = None
            if args.mode == 'rnr':
                relevance = 1 if (truth == 1 or truth == 2) else 0
                probability = prob_useful + prob_vital
            else:
                relevance = 1 if truth == 2 else 0
                probability = prob_vital
            print '%s %s' % (probability, relevance)

if __name__ == '__main__':
  main()
