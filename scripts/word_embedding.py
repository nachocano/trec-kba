#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
import time
import numpy as np
from collections import defaultdict


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int)
  parser.add_argument('-t', '--train_or_test_tsv_file', required=True)
  parser.add_argument('-a', '--aggregate_vector_file', required=False)
  args = parser.parse_args()

  if not args.embeddings_dimension:
    args.embeddings_dimension = 300

  start = time.time()
  #print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  #print 'loaded in %s' % elapsed

  if args.aggregate_vector_file:
    aggregates = defaultdict(lambda: np.zeros(args.embeddings_dimension))
    counts = defaultdict(int)

  for line in open(args.train_or_test_tsv_file).read().splitlines():
    delimiter = line.rfind('[')
    lemmas = line[delimiter+1:-1].split(',')
    fixed = line[:delimiter-1]
    targetid = fixed.split()[1]
    embeddings = np.zeros(args.embeddings_dimension)
    count = 0
    for lemma in lemmas:
      lemma = lemma.strip()
      if model.__contains__(lemma):
        embeddings += model[lemma]
        count += 1

    if count > 0:
      embeddings = embeddings/count
    embeddings_as_str = ' '.join(str(e) for e in embeddings)
    print '%s %s' % (fixed, embeddings_as_str)

    if args.aggregate_vector_file:
      aggregates[targetid] += embeddings
      counts[targetid] += 1

  if args.aggregate_vector_file:
    with open(args.aggregate_vector_file, 'w') as f:
      for targetid in aggregates:
        aggregates[targetid] = aggregates[targetid] / counts[targetid]
        aggregate_as_str = ' '.join(str(e) for e in aggregates[targetid])
        f.write('%s,%s\n' % (targetid, aggregate_as_str))

if __name__ == '__main__':
  main()

