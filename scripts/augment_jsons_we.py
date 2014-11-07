#!/usr/bin/python
import argparse
import time
from collections import defaultdict
from os import listdir
from os.path import isfile, join
from os import rename
import json
from gensim.models import word2vec
from gensim import matutils
import numpy as np

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

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-json', '--json_file', required=True)
  parser.add_argument('-i', '--in_file', required=True)
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-tp', '--topn', required=False, type=int)
  args = parser.parse_args()

  if not args.topn:
    args.topn = 10

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
  model.init_sims()

  words = defaultdict(lambda: defaultdict(list))
  for line in open(args.in_file).read().splitlines():
    doc_id, entity_id, tokens, timestamp = line.split("\t")
    lemmas = tokens.split("|")
    lemmas_array = []
    for lemma in lemmas:
      lemma = lemma.strip()
      if lemma != '' and model.__contains__(lemma):
        lemmas_array.append(lemma)
    if len(lemmas_array) > 0:
      words[entity_id][doc_id] = lemmas_array

  start = time.time()
  with open(args.json_file, 'r') as f:
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
  
  tmp_file = args.json_file + '.partial'
  with open(tmp_file, 'w') as f:
    f.write(json.dumps(json_file))
  rename(tmp_file, args.json_file)
  elapsed = time.time() - start
  print 'processed %s in %s' % (args.json_file, elapsed)
  
if __name__ == '__main__':
  main()

