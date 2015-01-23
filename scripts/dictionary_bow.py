#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-tr', '--train_tsv_file', required=True)
  parser.add_argument('-te', '--test_tsv_file', required=True)

  args = parser.parse_args()

  dictionary = {}
  index = 0
  index = fill_dict(dictionary, args.train_tsv_file, index)
  fill_dict(dictionary, args.test_tsv_file, index)

  for w in sorted(dictionary, key=dictionary.get):
    print w, dictionary[w]

def fill_dict(dictionary, f, index):
  for line in open(f).read().splitlines():
    delimiter = line.find('[')
    fixed = line[:delimiter-1]
    arrays = line[delimiter:]
    lemmas = arrays[1:arrays.find(']')].split(',')
    lemmas = filter(lambda x: x != '', lemmas)
    lemmas = [lemma.strip() for lemma in lemmas]
    for lemma in lemmas:
      if not dictionary.has_key(lemma):
        dictionary[lemma] = index
        index += 1
  return index

if __name__ == '__main__':
  main()

