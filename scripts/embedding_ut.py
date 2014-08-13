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
	parser.add_argument('-f', '--filter_amount', required=False, type=int)
	args = parser.parse_args()

	if not args.embeddings_dimension:
	  args.embeddings_dimension = 300

	if not args.filter_amount:
	  args.filter_amount = 10

	start = time.time()
	print 'loading file %s' % args.embeddings_file
	model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
	elapsed = time.time() - start
	print 'loaded in %s' % elapsed
	model.init_sims()

	words = ['launched', 'moving', 'has', 'shows']
	nouns = ['company', 'weekend', 'tour']
	embeddings = []
	for word in words:
		if model.__contains__(word):
			#print 'most similar to %s %s' % (word, model.most_similar(positive=[word], topn=10))
			embeddings.append(matutils.unitvec(model.syn0[model.vocab[word].index]))
		else:
			print 'model does not contain %s' % word

	noun_embeddings = []
	for noun in nouns:
		if model.__contains__(noun):
			#print 'most similar to %s %s' % (word, model.most_similar(positive=[word], topn=10))
			noun_embeddings.append(matutils.unitvec(model.syn0[model.vocab[noun].index]))
		else:
			print 'model does not contain %s' % word


	print 'computing mean...'
	mean = matutils.unitvec(np.array(embeddings).mean(axis=0)).astype(np.float32)
	mean_nouns = matutils.unitvec(np.array(noun_embeddings).mean(axis=0)).astype(np.float32)
	print 'mean computed... now computing dot product'
	d = np.dot(model.syn0norm, mean)
	dist = np.dot(model.syn0norm, mean_nouns)
	print 'dot product computed'
	best = np.argsort(d)[::-1][:10]
	best_nouns = np.argsort(dist)[::-1][:10]
	print 'after best'
	result = [(model.index2word[sim], d[sim]) for sim in best]
	result_nouns = [(model.index2word[sim], dist[sim]) for sim in best_nouns]
	print 'after result'
	print result[:10]
	print result_nouns[:10]

if __name__ == '__main__':
  main()

