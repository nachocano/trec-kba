#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter
from gensim.models import tfidfmodel

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-b', '--bow_file', required=True)

  args = parser.parse_args()

  corpus = []
  for line in open(args.bow_file).read().splitlines():
    tokens = line.split()
    fixed = ' '.join(tokens[:29])
    bows = tokens[29:]
    doc = []
    for bow in bows:
      w, wc = bow.split(',')
      tup = (w, float(wc))
      doc.append(tup)
    corpus.append(doc)

    tfidf = tfidfmodel.TfidfModel(corpus)
    print tfidf[doc]
  
  #print '%s %s' % (fixed, tfidf_as_str)
      
if __name__ == '__main__':
  main()

