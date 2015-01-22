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
  parser.add_argument('-tr', '--train_bow_file', required=True)
  parser.add_argument('-te', '--test_bow_file', required=True)
  parser.add_argument('-otr', '--train_tfidf', required=True)
  parser.add_argument('-ote', '--test_tfidf', required=True)
  args = parser.parse_args()

  corpus = []
  to_tfidf(corpus, args.train_bow_file, args.train_tfidf)
  to_tfidf(corpus, args.test_bow_file, args.test_tfidf)

def to_tfidf(corpus, input_file, output_file):
  of = open(output_file, 'w')
  for line in open(input_file).read().splitlines():
    tokens = line.split()
    fixed = ' '.join(tokens[:29])
    bows = tokens[29:]
    doc = []
    for bow in bows:
      w, wc = bow.split(',')
      tup = (int(w), float(wc))
      doc.append(tup)
    corpus.append(doc)

    tfidf = tfidfmodel.TfidfModel(corpus)
    doc_tfidf = tfidf[doc]
    doc_tfidf_as_arr = []
    for w, v in doc_tfidf:
      doc_tfidf_as_arr.append('%s,%s' % (w,v))
    doc_tfidf_as_str = ' '.join(doc_tfidf_as_arr)
    of.write('%s %s\n' % (fixed, doc_tfidf_as_str))
  of.close()
      
if __name__ == '__main__':
  main()

