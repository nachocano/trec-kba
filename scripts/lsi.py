#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter
from gensim.models import lsimodel

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-tr', '--train_tfidf_file', required=True)
  parser.add_argument('-te', '--test_tfidf_file', required=True)
  parser.add_argument('-otr', '--train_lsi', required=True)
  parser.add_argument('-ote', '--test_lsi', required=True)
  args = parser.parse_args()

  corpus = []
  train_docs = []
  test_docs = []
  print 'reading train'
  read_corpus(corpus, args.train_tfidf_file, train_docs)
  print 'reading test'
  read_corpus(corpus, args.test_tfidf_file, test_docs)

  print 'corpus size %d' % len(corpus)
  print 'loading lsi'
  lsi = lsimodel.LsiModel(corpus)
  print 'loaded lsi'
  print 'converting train to lsi'
  to_lsi(corpus, args.train_lsi, train_docs, lsi)
  print 'converting test to lsi'
  to_lsi(corpus, args.test_lsi, test_docs, lsi)

def to_lsi(corpus, output_file, docs, lsi):
  i = 0
  of = open(output_file, 'w')
  for fixed, doc in docs:
    doc_lsi = lsi[doc]
    doc_lsi_as_arr = []
    for w, v in doc_lsi:
      doc_lsi_as_arr.append('%s,%s' % (w,v))
    doc_lsi_as_str = ' '.join(doc_lsi_as_arr)
    of.write('%s %s\n' % (fixed, doc_lsi_as_str))
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

