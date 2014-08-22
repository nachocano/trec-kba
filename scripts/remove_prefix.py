#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from operator import itemgetter


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-c', '--corpus', required=True)
  args = parser.parse_args()

  for line in open(args.corpus).read().splitlines():
    line = line.replace('http://s3.amazonaws.com/aws-publicdatasets/trec/kba/kba-streamcorpus-2014-v0_3_0-kba-filtered/', '')    
    print line

if __name__ == '__main__':
  main()

