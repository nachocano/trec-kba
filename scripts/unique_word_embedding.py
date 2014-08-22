#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from operator import itemgetter


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int)
  parser.add_argument('-t', '--train_or_test_tsv_file', required=True)
  parser.add_argument('-tp', '--topn', required=False, type=int)
  args = parser.parse_args()

  if not args.embeddings_dimension:
    args.embeddings_dimension = 300

  start = time.time()
  #print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  model.init_sims()
  elapsed = time.time() - start
  #print 'loaded in %s' % elapsed

  for line in open(args.train_or_test_tsv_file).read().splitlines():
    delimiter = line.find('[')
    fixed = line[:delimiter-1]
    arrays = line[delimiter:]
    lemmas = arrays[1:arrays.find(']')].split(',')

    lemma_embeddings = []
    for lemma in lemmas:
      lemma = lemma.strip()
      if lemma != '' and model.__contains__(lemma):
        lemma_embeddings.append(matutils.unitvec(model.syn0[model.vocab[lemma].index]))

    if len(lemma_embeddings) > 0:
      lemma_embeddings = matutils.unitvec(np.array(lemma_embeddings).mean(axis=0)).astype(np.float32)
    else:
      lemma_embeddings = np.zeros(args.embeddings_dimension).astype(np.float32)

    lemma_embeddings_as_str = ' '.join(str(e) for e in lemma_embeddings)
    print '%s %s' % (fixed, lemma_embeddings_as_str)

if __name__ == '__main__':
  main()

