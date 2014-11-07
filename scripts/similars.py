#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
from gensim import matutils
import time
from utils import similar_words
import sys


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  args = parser.parse_args()

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
  model.init_sims()
  
  line = sys.stdin.readline()
  while line:
    line = line.rstrip('\n')
    line = line.split(" ")
    positives = line[:2]
    negatives = line[2:]
    try:
      most_sim = model.most_similar(positive=positives, negative=negatives)
      print '##########'
      print 'positives %s, negatives %s' % (positives, negatives)
      print most_sim
      print '##########'
    except:
      "no words for %s" % line
    line = sys.stdin.readline()

if __name__ == '__main__':
  main()

