#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-t', '--train_or_test_tsv_file', required=True)
  parser.add_argument('-d', '--dictionary_file', required=True)

  args = parser.parse_args()

  dictionary = {}
  for line in open(args.dictionary_file).read().splitlines():
    word, wid = line.split()
    dictionary[word] = wid

  for line in open(args.train_or_test_tsv_file).read().splitlines():
    delimiter = line.find('[')
    fixed = line[:delimiter-1]
    arrays = line[delimiter:]
    lemmas = arrays[1:arrays.find(']')].split(',')
    lemmas = filter(lambda x: x != '', lemmas)
    lemmas = [lemma.strip() for lemma in lemmas]
    bow = []
    counts = defaultdict(int)
    for lemma in lemmas:
      counts[lemma] += 1
    for k in counts:
      value = counts[k]
      bow.append('%s,%s' % (dictionary[k],value))
    bow_as_str = ' '.join(str(e) for e in bow) 
    print '%s %s' % (fixed, bow_as_str)
      
if __name__ == '__main__':
  main()

