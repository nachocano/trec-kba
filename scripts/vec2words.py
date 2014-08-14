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

def complete_truth(train_test, filename):
  with open(filename) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      relevance = int(l[3])
      train_test[targetid][(streamid, date_hour)] = relevance


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--embeddings_file', required=True)
  parser.add_argument('-c', '--clusters_file', required=True)
  parser.add_argument('-r', '--run_file', required=True)
  parser.add_argument('-t', '--truth_test_file', required=True)
  parser.add_argument('-tr', '--truth_train_file', required=True)
  parser.add_argument('-ft', '--filter_targetid', required=True)
  parser.add_argument('-fc', '--filter_clusters', required=True, type=int)
  parser.add_argument('-fe', '--filter_elements', required=True, type=int)
  parser.add_argument('-d', '--embeddings_dimension', required=False, type=int)
  parser.add_argument('-tp', '--topn', required=False, type=int)
  args = parser.parse_args()

  if not args.embeddings_dimension:
    args.embeddings_dimension = 300

  if not args.topn:
    args.topn = 10


  element_regex = re.compile(r'\(([^()]+)\)')


  run = defaultdict(defaultdict)
  with open(args.run_file) as f:
    for line in f.read().splitlines():
      l = line.strip()
      if l.startswith('#'):
          continue
      l = l.split('\t')
      streamid = l[2]
      targetid = l[3]
      relevance = int(l[5])
      date_hour = l[7]
      run[targetid][(streamid, date_hour)] = relevance

  train_test_truth = defaultdict(defaultdict)
  complete_truth(train_test_truth, args.truth_test_file)
  complete_truth(train_test_truth, args.truth_train_file)

  centroids = defaultdict(defaultdict)
  cluster_elements = defaultdict(lambda: defaultdict(list))
  with open(args.clusters_file) as f:
    for line in f.read().splitlines():
      line = line.split('\t')
      targetid = line[0]
      clusterid = int(line[1])
      # removes starting [ and ending ]
      centroid_as_str = line[2][1:-1]
      centroid = np.array(centroid_as_str.split(',')).astype(np.float32)
      centroids[targetid][clusterid] = centroid
      elements = line[3][1:-1]
      for element in element_regex.findall(elements):
        # parse the triple
        values = element.replace('[', '').replace(']', '').replace("'", "").split(',')
        streamid = values[0].strip()
        date_hour = values[1].strip()
        vector = np.array(values[2:]).astype(np.float32)
        key = (streamid, date_hour)
        truth_relevance = train_test_truth[targetid][key]
        # it may have no prediction, it's part of the training files
        predicted_relevance = None
        if run[targetid].has_key(key):
          predicted_relevance = run[targetid][key]
        cluster_elements[targetid][clusterid].append({'streamid' : streamid, 'date_hour' : date_hour, 'vector' : vector, 'truth' : truth_relevance, 'prediction' : predicted_relevance})
      
  start = time.time()
  print 'loading file %s' % args.embeddings_file
  model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
  elapsed = time.time() - start
  print 'loaded in %s' % elapsed
  model.init_sims()
  
  
  for targetid in centroids:
    if args.filter_targetid not in targetid:
      continue
    condition_matched = False
    while not condition_matched:
      print 'condition not matched yet...'
      clusterids = random.sample(centroids[targetid].keys(), args.filter_clusters)
      stop = True
      for clusterid in clusterids:
        if len(cluster_elements[targetid][clusterid]) <= args.filter_elements:
          stop = False
          break
      condition_matched = stop
    print 'condition matched'
    print 'checking only these clusters %s' % clusterids
    for clusterid in centroids[targetid]:
      if clusterid not in clusterids:
        continue
      closest = similar_words(model, centroids[targetid][clusterid], args.topn)
      print '######### TARGETID: %s - CLUSTER ID: %d ##########' % (targetid, clusterid)
      print 'centroid:\n%s' % closest
      print '\n'
      for i in xrange(args.filter_elements):
        element = cluster_elements[targetid][clusterid][i]
        print 'element: %s -> prediction=%s, truth=%s' % (element['streamid'], element['prediction'], element['truth'])
        closest_to_element = similar_words(model, element['vector'], args.topn)
        print '\n%s\n' % closest_to_element

      pred_usefuls = 0
      pred_vitals = 0
      truth_usefuls = 0
      truth_vitals = 0
      for element in cluster_elements[targetid][clusterid]:
        if element['prediction'] == 1: 
          pred_usefuls += 1
        else:
          pred_vitals += 1
        if element['truth'] == 1:
          truth_usefuls += 1
        else:
          truth_vitals += 1

      print 'Predictions: Usefuls=%d, Vitals=%d' % (pred_usefuls, pred_vitals)
      print 'Truth:       Usefuls=%d, Vitals=%d' % (truth_usefuls, truth_vitals)
      print '#################################################'



if __name__ == '__main__':
  main()

