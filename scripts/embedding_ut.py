#!/usr/bin/python
from __future__ import division
import argparse
from gensim.models import word2vec
from gensim import utils, matutils
import time
import numpy as np
import re
from collections import defaultdict
from scipy.spatial.distance import euclidean


def main():
	parser = argparse.ArgumentParser(description='TODO')
	parser.add_argument('-e', '--embeddings_file', required=True)
	parser.add_argument('-d', '--embeddings_dimension', required=False, type=int)
	parser.add_argument('-f', '--topn', required=False, type=int)
	args = parser.parse_args()

	if not args.embeddings_dimension:
	  args.embeddings_dimension = 300

	if not args.topn:
	  args.topn = 10

	start = time.time()
	print 'loading file %s' % args.embeddings_file
	model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
	elapsed = time.time() - start
	print 'loaded in %s' % elapsed
	model.init_sims()

	nouns = ['terrorism', 'trade', 'similarities', 'earthquake', 'firstnation', 'visit', 'type', 'people', 'mass', 'delegation', 'time', 'province',\
	 'reset', 'protests', 'nations', 'exchange', 'sorrowful', 'thousands', 'office', 'site', 'mark', 'miles', 'ceremony', 'highlights', 'comparison',\
	  'expressions', 'relationship', 'gaps', 'devastation', 'committee', 'peoples', 'mission', 'interview', 'grain', 'decry', 'opening', 'lives', 'weeklong',\
	  'management', 'telephone']
	print 'nouns len %d' % len(nouns)
	nouns = [noun for noun in nouns if noun in model.vocab]
	print 'nouns len now %d' % len(nouns)
	print 'nouns %s' % nouns

	#verbs = ['impressed', 'participated', 'said', 'attended', 'appears', 'was', 'visited', 'picking', 'leads', 'were', 'are', 'see', 'saw', 'melted', 'spent']
	#print 'verbs len %d' % len(verbs)
	#verbs = [verb for verb in verbs if verb in model.vocab]
	#print 'verbs len now %d' % len(verbs)

	vectors = np.vstack(matutils.unitvec(model.syn0[model.vocab[word].index]) for word in nouns).astype(np.float32)
	mean_nouns = matutils.unitvec(vectors.mean(axis=0)).astype(np.float32)
	distances = np.dot(vectors, mean_nouns)
	values_filtered = sorted(zip(distances, nouns))
	filtered_nouns = [n for d, n in values_filtered if d > 0.4]
	print 'filtered %s' % filtered_nouns

	#print 'nouns not matched %s' % model.doesnt_match(newnouns)
	#print 'verbs not matched %s' % model.doesnt_match(verbs)
	#exit()
	#words = ['launched', 'moving', 'has', 'shows']
	#nouns = ['company', 'weekend', 'tour']
	filtered_embeddings = []
	for word in filtered_nouns:
			filtered_embeddings.append(matutils.unitvec(model.syn0[model.vocab[word].index]))

	noun_embeddings = []
	for noun in nouns:
			noun_embeddings.append(matutils.unitvec(model.syn0[model.vocab[noun].index]))

	print 'computing mean...'
	mean_filtered = matutils.unitvec(np.array(filtered_embeddings).mean(axis=0)).astype(np.float32)
	mean_nouns = matutils.unitvec(np.array(noun_embeddings).mean(axis=0)).astype(np.float32)
	print 'mean computed... now computing dot product'
	distance_filtered = np.dot(model.syn0norm, mean_filtered)
	distance_nouns = np.dot(model.syn0norm, mean_nouns)
	print 'dot product computed'
	best_filtered = np.argsort(distance_filtered)[::-1][:args.topn]
	print best_filtered
	best_nouns = np.argsort(distance_nouns)[::-1][:args.topn]
	print best_nouns
	result_filtered = [(model.index2word[sim], distance_filtered[sim]) for sim in best_filtered]
	result_nouns = [(model.index2word[sim], distance_nouns[sim]) for sim in best_nouns]
	print 'closest to filtered %s' % result_filtered[:args.topn]
	print 'closest to nouns %s' % result_nouns[:args.topn]

if __name__ == '__main__':
  main()

