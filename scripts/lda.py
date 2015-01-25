#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter
from gensim.models import ldamodel
import sys

def log(msg):
  sys.stdout.write('%s\n' % msg)
  sys.stdout.flush()

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-tr', '--train_tfidf_file', required=True)
  parser.add_argument('-te', '--test_tfidf_file', required=True)
  parser.add_argument('-otr', '--train_lda', required=True)
  parser.add_argument('-ote', '--test_lda', required=True)
  args = parser.parse_args()

  corpus = []
  train_docs = []
  test_docs = []
  log('reading train')
  read_corpus(corpus, args.train_tfidf_file, train_docs)
  log('reading test')
  read_corpus(corpus, args.test_tfidf_file, test_docs)

  log('corpus size %d' % len(corpus))
  log('loading lda')
  lda = ldamodel.LdaModel(corpus, num_topics=300)
  log('loaded lda')
  log('converting train to lda')
  to_lda(corpus, args.train_lda, train_docs, lda)
  log('converting test to lda')
  to_lda(corpus, args.test_lda, test_docs, lda)

def to_lda(corpus, output_file, docs, lda):
  i = 0
  of = open(output_file, 'w')
  for fixed, doc in docs:
    doc_lda = lda[doc]
    doc_lda_as_arr = []
    for w, v in doc_lda:
      doc_lda_as_arr.append('%s,%s' % (w,v))
    doc_lda_as_str = ' '.join(doc_lda_as_arr)
    of.write('%s %s\n' % (fixed, doc_lda_as_str))
    print i
    i+=1
  of.close()

def read_corpus(corpus, input_file, docs):
  for line in open(input_file).read().splitlines():
    tokens = line.split()
    fixed = ' '.join(tokens[:29])
    tfidfs = tokens[29:]
    doc = []
    for elem in tfidfs:
      w, value = elem.split(',')
      tup = (int(w), float(value))
      doc.append(tup)
    docs.append((fixed, doc))
    corpus.append(doc)

if __name__ == '__main__':
  main()

