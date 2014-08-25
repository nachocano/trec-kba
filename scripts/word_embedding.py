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
    two_arrays = line[delimiter:]
    nouns = two_arrays[1:two_arrays.find(']')-1].split(',')
    nouns = filter(lambda x: x != '', nouns)
    verbs = two_arrays[two_arrays.rfind('[')+1:-1].split(',')
    verbs = filter(lambda x: x != '', verbs)
    fixed = line[:delimiter-1]
    targetid = fixed.split()[1]
    
    noun_embeddings = []
    for noun in nouns:
      noun_lemma = noun.strip()
      if model.__contains__(noun_lemma):
        noun_embeddings.append(matutils.unitvec(model.syn0[model.vocab[noun_lemma].index]))

    verb_embeddings = []
    for verb in verbs:
      verb_lemma = verb.strip()
      if model.__contains__(verb_lemma):
        verb_embeddings.append(matutils.unitvec(model.syn0[model.vocab[verb_lemma].index]))

    if len(noun_embeddings) > 0:
      noun_embeddings = matutils.unitvec(np.array(noun_embeddings).mean(axis=0)).astype(np.float32)
    else:
      noun_embeddings = np.zeros(args.embeddings_dimension).astype(np.float32)

    if len(verb_embeddings) > 0:
      verb_embeddings = matutils.unitvec(np.array(verb_embeddings).mean(axis=0)).astype(np.float32)
    else:
      verb_embeddings = np.zeros(args.embeddings_dimension).astype(np.float32)
    
    noun_embeddings_as_str = ' '.join(str(e) for e in noun_embeddings)
    verb_embeddings_as_str = ' '.join(str(e) for e in verb_embeddings)
    print '%s %s %s' % (fixed, noun_embeddings_as_str, verb_embeddings_as_str)

if __name__ == '__main__':
  main()

