#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from os import system
from os import rename
import json

def similar_words(model, matrix, target_vector, topn=10):
    dists = np.dot(matrix, target_vector)
    best = np.argsort(dists)[::-1][:topn]
    result = [(model.index2word[sim], dists[sim]) for sim in best]
    return result[:topn]

def build_object(e):
  prob = round(e[1]*1000)
  return {'w': e[0].encode("utf-8"), 'c': prob}

def get_embedding_matrix(model, lemmas):
  lemmas_embeddings = []
  for lemma in lemmas:
    lemmas_embeddings.append(matutils.unitvec(model.syn0[model.vocab[lemma].index]))
  return np.array(lemmas_embeddings).astype(np.float32)


def load_model(embedding_file):
  start = time.time()
  print 'loading file %s' % embedding_file
  model = word2vec.Word2Vec.load_word2vec_format(embedding_file, binary=True)
  model.init_sims()
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
  return model


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-ri', '--raw_input', required=True)
  parser.add_argument('-ei', '--embedding_input', required=False)
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-o', '--output_file', required=True)

  parser.add_argument('-j', '--jar_path', required=True)
  parser.add_argument('-a', '--alpha', required=True)
  parser.add_argument('-gd', '--gamma_decrease', required=True)
  parser.add_argument('-gi', '--gamma_increase', required=True)
  parser.add_argument('-c', '--time_constant', required=False)
  args = parser.parse_args()

  embeddings_dimension = 300
  model = None

  if not args.time_constant:
    args.time_constant = 86400 #seconds in a day


  if not args.embedding_input:
    args.embedding_input = args.raw_input + '.emb'
    model = load_model(args.embeddings_file)

    print 'computing embeddings from words...'
    start = time.time()
    with open(args.embedding_input, 'w') as f:
      for line in open(args.raw_input).read().splitlines():
        doc_id, entity_id, tokens, timestamp = line.split("\t")
        lemmas = tokens.split("|")
        lemma_embeddings = []
        for lemma in lemmas:
          lemma = lemma.strip()
          if lemma != '' and model.__contains__(lemma):
            lemma_embeddings.append(matutils.unitvec(model.syn0[model.vocab[lemma].index]))

        if len(lemma_embeddings) > 0:
          lemma_embeddings = matutils.unitvec(np.array(lemma_embeddings).mean(axis=0)).astype(np.float32)
        else:
          lemma_embeddings = np.zeros(embeddings_dimension).astype(np.float32)

        lemma_embeddings_as_str = ' '.join(str(e) for e in lemma_embeddings)
        f.write('%s|%s|%s|%s\n' % (doc_id, entity_id, timestamp, lemma_embeddings_as_str))
    elapsed = time.time() - start
    print 'embeddings computed in %s' % elapsed

    print 'computing staleness features...'
    java_cmd = 'java -jar %s -i %s -o %s -a %s -gi %s -gd %s -tn %s -ip 10' % (args.jar_path, args.embedding_input, args.output_file, args.alpha, args.gamma_increase, args.gamma_decrease, args.time_constant)
    os.system(java_cmd)
    print 'staleness features computed'

    if not model:
      model = load_model(args.embeddings_file)

    start = time.time()
    print 'computing word clouds...'
    words = defaultdict(lambda: defaultdict(list))
    # inefficient, done before, I don't care
    for line in open(args.raw_input).read().splitlines():
      doc_id, entity_id, tokens, timestamp = line.split("\t")
      lemmas = tokens.split("|")
      lemmas_array = []
      for lemma in lemmas:
        lemma = lemma.strip()
        if lemma != '' and model.__contains__(lemma):
          lemmas_array.append(lemma)
      if len(lemmas_array) > 0:
        words[entity_id][doc_id] = lemmas_array

    tmp_file = args.output_file + '.partial'
    with open(args.args.output_file, 'r') as f:
      with open(tmp_file, 'w') as tmp:
        json_file = json.load(f)
        for e in json_file:
          entityid = e['id']
          full_array = []
          for d in e['docs']:
            full_array.extend(words[entityid][d['id']])
          full_matrix = get_embedding_matrix(model, full_array)
          for elem in e['clusters']:
            vec = np.array(elem['emb']).astype(np.float32)
            sim = similar_words(model, full_matrix, vec, args.topn)
            asJs = map(build_object, sim)
            elem['emb'] = asJs
        tmp.write(json.dumps(e))
        tmp.write('\n')
    rename(tmp_file, args.output_file)
    elapsed = time.time() - start
    print 'computed word clouds in %s' % elapsed

if __name__ == '__main__':
  main()

