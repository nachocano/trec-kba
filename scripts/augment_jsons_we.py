#!/usr/bin/python
import argparse
import time
from collections import defaultdict
from os import listdir
from os.path import isfile, join
from os import rename
import json
from gensim.models import word2vec
from utils import similar_words
import numpy as np


def build_object(e):
  prob = round(e[1]*1000)
  return {'t': e[0].encode("utf-8"), 'p': prob}

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-json', '--json_folder', required=True)
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-tp', '--topn', required=False, type=int)
  args = parser.parse_args()

  if not args.topn:
    args.topn = 20

  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
  model.init_sims()

  onlyfiles = [ join(args.json_folder,f) for f in listdir(args.json_folder) if isfile(join(args.json_folder,f)) ]

  for filename in onlyfiles:
    with open(filename, 'r') as f:
      json_file = json.load(f)
      for d in json_file:
        vector = np.array(d['di']).astype(np.float32)
        similars = similar_words(model, vector, args.topn)
        asJson = map(build_object, similars)
        d['di'] = asJson
        for elem in d['clusters']:
          vec = np.array(elem['cj_emb']).astype(np.float32)
          sim = similar_words(model, vec, args.topn)
          asJs = map(build_object, sim)
          elem['cj_emb'] = asJs
    
    tmp_file = filename + '.partial'
    with open(tmp_file, 'w') as f:
      f.write(json.dumps(json_file))
    rename(tmp_file, filename)
  
if __name__ == '__main__':
  main()

