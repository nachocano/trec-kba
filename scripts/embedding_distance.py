#!/usr/bin/python
from __future__ import division
import argparse
import numpy as np
from scipy.spatial.distance import euclidean

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-t', '--train_with_vectors_tsv_file', required=True)
  parser.add_argument('-a', '--aggregate_vector_file', required=False)
  args = parser.parse_args()

  aggregates = {}
  for line in open(args.aggregate_vector_file).read().splitlines():
    targetid, aggregate = line.split(',')
    aggregate = np.array(aggregate.split()).astype(float)
    aggregates[targetid] = aggregate

  for line in open(args.train_with_vectors_tsv_file).read().splitlines():
    line = line.split()
    targetid = line[1]
    embeddings = np.array(line[29:]).astype(float)
    distance = euclidean(aggregates[targetid], embeddings)
    first_part = ' '.join(str(e) for e in line[:29])
    print '%s %s' % (first_part, distance)

if __name__ == '__main__':
  main()

