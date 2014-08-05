#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict


def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--run_file', required=True)
    parser.add_argument('-gt', '--ground_truth_file', required=True)
    parser.add_argument('-e', '--entities_ccr', required=True)
    parser.add_argument('-m', '--mode', required=True)
    args = parser.parse_args()

    assert(args.mode == 'uv' or args.mode == 'rnr')

    targetids = {}
    for line in open(args.entities_ccr).read().splitlines():
        targetids[line.strip()] = True

    ground_truth = {}
    with open(args.ground_truth_file) as f:
        for line in f.read().splitlines():
            l = line.strip()
            if l.startswith('#'):
                continue
            l = l.split('\t')
            targetid = l[3]
            if targetids.has_key(targetid):
                streamid = l[2]
                date_hour = l[7]
                candidate_relevance = int(l[5])
                if args.mode == 'rnr':
                    relevance = 1 if (candidate_relevance == 1 or candidate_relevance == 2) else 0
                else:
                    #if candidate_relevance == 0 or candidate_relevance == -1:
                    #    continue
                    relevance = 1 if candidate_relevance == 2 else 0
                ground_truth[(streamid, targetid, date_hour)] = relevance

    run = {}
    with open(args.run_file) as f:
        for line in f.read().splitlines():
            l = line.strip()
            if l.startswith('#'):
                continue
            l = l.split('\t')
            streamid = l[2]
            targetid = l[3]
            candidate_relevance = int(l[5])
            date_hour = l[7]
            probability = int(l[4]) / 1000
            if args.mode == 'rnr':
                relevance = 1 if (candidate_relevance == 1 or candidate_relevance == 2) else 0
            else:
                #if candidate_relevance == 0 or candidate_relevance == -1:
                #    continue
                relevance = 1 if candidate_relevance == 2 else 0
            run[(streamid, targetid, date_hour)] = (relevance, probability)

    for key in ground_truth:
        targetid = key[1]
        if run.has_key(key):
            probability = run[key][1]
            if ground_truth[key] != run[key][0]:
                probability = 1 - probability
            print '%s %s' % (probability, ground_truth[key])


if __name__ == '__main__':
  main()
