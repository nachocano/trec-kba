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
	args = parser.parse_args()

	if not args.embeddings_dimension:
	  args.embeddings_dimension = 300

	start = time.time()
	print 'loading file %s' % args.embeddings_file
	model = word2vec.Word2Vec.load_word2vec_format(args.embeddings_file, binary=True)
	elapsed = time.time() - start
	print 'loaded in %s' % elapsed
	model.init_sims(replace=True)

	words = ['launched', 'moving', 'company', 'weekend', 'tour', 'has', 'shows']
	embeddings = np.zeros(args.embeddings_dimension)
	count = 0
	for word in words:
		if model.__contains__(word):
			print 'most similar to %s %s' % (word, model.most_similar(positive=[word], topn=10))
			embeddings += matutils.unitvec(model[word])
			count += 1
		else:
			print 'model does not contain %s' % word

	print 'count %d' % count
	mean = matutils.unitvec(np.array(embeddings).mean(axis=0)).astype(np.float32)

	min_distance = 100000.0
	most_similar_words = []
	start = time.time()
	print 'looking for most similar...'
	for word in model.vocab:
		vector = matutils.unitvec(model[word])
		d = euclidean(mean, vector)
		if d < min_distance:
			min_distance = d
			most_similar_word.append(word)
			print 'most similar so far %s with distance %f' % (word, min_distance)
	elapsed = time.time() - start
	print 'search took %s' % elapsed
	print 'most similar to %s' % most_similar_word
	most_similar_words.reverse()

	if len(most_similar_words) > arg.filter_amount:
		most_similar_words = most_similar_words[:args.filter_amount]

	print most_similar_words

if __name__ == '__main__':
  main()

