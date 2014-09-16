#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
from gensim import matutils
import time
import numpy as np
import re
from collections import defaultdict
from scipy.spatial.distance import euclidean
import random
from utils import similar_words

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  args = parser.parse_args()

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
 
  print model.most_similar(positive=['paris', 'germany'], negative=['france'], topn=5)
  print model.most_similar(positive=['woman', 'king'], negative=['man'], topn=5)
  print model.most_similar(positive=['woman', 'king'], negative=['man'], topn=5)
  print model.most_similar(positive=['argentina', 'pele'], negative=['brasil'], topn=5)


if __name__ == '__main__':
  main()

