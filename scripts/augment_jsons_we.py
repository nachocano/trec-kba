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
  return {'t': e[0].encode("utf-8"), 'p': prob}

def get_embedding_matrix(model, lemmas):
  lemmas_embeddings = []
  for lemma in lemmas:
    lemmas_embeddings.append(matutils.unitvec(model.syn0[model.vocab[lemma].index]))
  return np.array(lemmas_embeddings).astype(np.float32)

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-json', '--json_folder', required=True)
  parser.add_argument('-a', '--all_file', required=True)
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
  for line in open(args.all_file).read().splitlines():
    delimiter = line.find('[')
    fixed = line[:delimiter-1]
    arrays = line[delimiter:]
    lemmas = arrays[1:arrays.find(']')].split(',')
    lemmas = filter(lambda x: x != '', lemmas)
    lemmas_array = []
    for lemma in lemmas:
      lemma = lemma.strip()
      if lemma != '' and model.__contains__(lemma):
        lemmas_array.append(lemma)
    if len(lemmas_array) > 0:
      fixed_splitted = fixed.split(' ')
      streamid = fixed_splitted[0]
      targetid = fixed_splitted[1][fixed_splitted[1].rfind('/')+1:]
      words[targetid][streamid] = lemmas_array

  onlyfiles = [ join(args.json_folder,f) for f in listdir(args.json_folder) if isfile(join(args.json_folder,f)) ]
  count = len(onlyfiles)

  for filename in onlyfiles:
    count -= 1
    start = time.time()
    print 'processing %s, left %d' % (filename, count)
    with open(filename, 'r') as f:
      json_file = json.load(f)
      targetid = filename[filename.rfind('/')+1:].replace('.json', '')
      for d in json_file:
        vector = np.array(d['di']).astype(np.float32)
        lemmas_array = words[targetid][d['streamid']]
        matrix = get_embedding_matrix(model, lemmas_array)
        similars = similar_words(model, matrix, vector, args.topn)
        asJson = map(build_object, similars)
        d['di'] = asJson
        full_array = []
        for sid in d['streamIds']:
          full_array.extend(words[targetid][sid])
        full_matrix = get_embedding_matrix(model, full_array)
        for elem in d['clusters']:
          vec = np.array(elem['cj_emb']).astype(np.float32)
          sim = similar_words(model, full_matrix, vec, args.topn)
          asJs = map(build_object, sim)
          elem['cj_emb'] = asJs
    
    tmp_file = filename + '.partial'
    with open(tmp_file, 'w') as f:
      f.write(json.dumps(json_file))
    rename(tmp_file, filename)
    elapsed = time.time() - start
    print 'processed %s in %s' % (filename, elapsed)
  
if __name__ == '__main__':
  main()

