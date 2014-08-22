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
  parser.add_argument('-t', '--train_or_test_tsv_file', required=True)
  args = parser.parse_args()

  for line in open(args.train_or_test_tsv_file).read().splitlines():
    delimiter = line.find('[')
    two_arrays = line[delimiter:]
    nouns = two_arrays[1:two_arrays.find(']')-1].split(',')
    nouns = filter(lambda x: x != '', nouns)
    verbs = two_arrays[two_arrays.rfind('[')+1:-1].split(',')
    verbs = filter(lambda x: x != '', verbs)
    fixed = line[:delimiter-1]
    targetid = fixed.split()[1]
    nouns.extend(verbs)
    print '%s %s' % (fixed, ('[' + ', '.join(nouns) + ']'))
    

if __name__ == '__main__':
  main()

