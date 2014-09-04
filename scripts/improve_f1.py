#!/usr/bin/python
from __future__ import division
import argparse
from utils import create_relevant_global_data
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import Counter
import time
import numpy as np

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--run', required=True)
    args = parser.parse_args()
    with open(args.run) as f:
        for line in f.read().splitlines():
            l = line.strip()
            if l.startswith('#'):
                print line
                continue
            l = l.split('\t')
            teamid = l[0]
            runid = l[1]
            streamid = l[2]
            targetid = l[3]
            confidence = int(l[4])
            relevance = int(l[5])
            contains_mention = l[6]
            date_hour = l[7]
            null = l[8]
            minus_one = l[9]
            slots = l[10]
            if relevance == 1:
                if confidence <= 600:
                    relevance = 2
            #elif relevance == 2:
            #    if confidence < 300:
            #        relevance = 1

            print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (teamid, runid, streamid, targetid, confidence, relevance, contains_mention, date_hour, null, minus_one, slots)

if __name__ == '__main__':
  main()
