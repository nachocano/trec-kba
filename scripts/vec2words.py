#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
from gensim import matutils
import time
import numpy as np
from collections import defaultdict
from scipy.spatial.distance import euclidean


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int)
  parser.add_argument('-v', '--vector_file', required=True)
  args = parser.parse_args()

  if not args.embeddings_dimension:
    args.embeddings_dimension = 300


  target_vector = None
  for line in open(args.vector_file).read().splitlines():
    line = line.split()
    targetid = line[0]
    target_vector = np.array(line[1:]).astype(float)

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
  model.init_sims(replace=True)
  
  min_distance = 100000.0
  most_similar_word = None
  vocab_size = left = len(model.vocab)
  print 'vocab size %d' % vocab_size
  start = time.time()
  print 'looking for most similar...'
  for word in model.vocab:
    left -= 1 
    vector = model.syn0[model.vocab[word].index]
    d = euclidean(target_vector, vector)
    if d < min_distance:
      min_distance = d
      most_similar_word = word
      print 'most similar so far %s with distance %f' % (most_similar_word, min_distance)
      print '%d left to check' % left
  elapsed = time.time() - start
  print 'search took %s' % elapsed
  print 'most similar to %s' % most_similar_word
  print model.most_similar(positive=[most_similar_word])


if __name__ == '__main__':
  main()

