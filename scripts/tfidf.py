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
  train_docs = []
  test_docs = []
  read_corpus(corpus, args.train_bow_file, train_docs)
  read_corpus(corpus, args.test_bow_file, test_docs)

  tfidf = tfidfmodel.TfidfModel(corpus)

  to_tfidf(corpus, args.train_tfidf, train_docs)
  to_tfidf(corpus, args.test_tfidf, test_docs)

def to_tfidf(corpus, output_file, docs):
  of = open(output_file, 'w')
  for doc in docs:
    doc_tfidf = tfidf[doc]
    doc_tfidf_as_arr = []
    for w, v in doc_tfidf:
      doc_tfidf_as_arr.append('%s,%s' % (w,v))
    doc_tfidf_as_str = ' '.join(doc_tfidf_as_arr)
    of.write('%s %s\n' % (fixed, doc_tfidf_as_str))
  of.close()

def read_corpus(corpus, input_file, docs):
  for line in open(input_file).read().splitlines():
    tokens = line.split()
    fixed = ' '.join(tokens[:29])
    bows = tokens[29:]
    doc = []
    for bow in bows:
      w, wc = bow.split(',')
      tup = (int(w), float(wc))
      doc.append(tup)
    docs.append(doc)
    corpus.append(doc)

if __name__ == '__main__':
  main()

