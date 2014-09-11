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
    three_arrays = line[delimiter:]
    nouns_delimiter = three_arrays.find(']')
    nouns = three_arrays[1:nouns_delimiter].split(',')
    nouns = filter(lambda x: x != '', nouns)
    two_arrays = three_arrays[nouns_delimiter+2:]
    verbs = two_arrays[1:two_arrays.find(']')].split(',')
    verbs = filter(lambda x: x != '', verbs)
    proper_nouns = two_arrays[two_arrays.rfind('[')+1:-1].split(',')
    proper_nouns = filter(lambda x: x != '', proper_nouns)
    fixed = line[:delimiter-1]
    nouns.extend(verbs)
    nouns.extend(proper_nouns)
    print '%s %s' % (fixed, ('[' + ', '.join(nouns) + ']'))
    
if __name__ == '__main__':
  main()

