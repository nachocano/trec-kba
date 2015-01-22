#!/usr/bin/python
from __future__ import division
import argparse
import time
import numpy as np
from collections import defaultdict
from operator import itemgetter
from gensim.models import rpmodel
import sys

def log(msg):
  sys.stdout.write('%s\n' % msg)
  sys.stdout.flush()

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-tr', '--train_tfidf_file', required=True)
  parser.add_argument('-te', '--test_tfidf_file', required=True)
  parser.add_argument('-otr', '--train_random_proj', required=True)
  parser.add_argument('-ote', '--test_random_proj', required=True)
  args = parser.parse_args()

  corpus = []
  train_docs = []
  test_docs = []

  log('reading train')
  read_corpus(corpus, args.train_tfidf_file, train_docs)
  log('reading test')
  read_corpus(corpus, args.test_tfidf_file, test_docs)

  log('loading random projections')
  rp = rpmodel.RpModel(corpus, num_topics=300)
  log('loaded random projections')

  log('saving train')
  to_rp(corpus, args.train_random_proj, train_docs, rp)
  log('saving test')
  to_rp(corpus, args.test_random_proj, test_docs, rp)

def to_rp(corpus, output_file, docs, rp):
  i = 0
  of = open(output_file, 'w')
  for fixed, doc in docs:
    doc_rp = rp[doc]
    doc_rp_as_arr = []
    for w, v in doc_rp:
      doc_rp_as_arr.append('%s,%s' % (w,v))
    doc_rp_as_str = ' '.join(doc_rp_as_arr)
    of.write('%s %s\n' % (fixed, doc_rp_as_str))
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

