#!/usr/bin/env python
import os

def main():

  mean_static = 'nohup ../../../../py_virtual/bin/python -u gbt_clustering.py -e ../../../clustering/data/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                  -o ../../../clustering/outputs/uw-mean_static.txt -tr ../../../clustering/data/train_sorted.tsv -t ../../../clustering/data/test_sorted.tsv \
                  -i uw-mean_static -av 1 -an 1 -gvi 1 -gvd 1 -gni 1 -gnd 1 -s 0 -c ../../../clustering/ -rnrl ../../../clustering/model/rnr.pkl > ../../../clustering/logs/uw-mean_static.log'
  print mean_static
  os.system(mean_static)

  alphas = [0.2,0.4,0.6,0.8]
  alphas_name = ['02','04','06','08']
  for alpha, name in zip(alphas, alphas_name):
    clustering_static = 'nohup ../../../../py_virtual/bin/python -u gbt_clustering.py -e ../../../clustering/data/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                  -o ../../../clustering/outputs/uw-clustering_static_a%s.txt -tr ../../../clustering/data/train_sorted.tsv -t ../../../clustering/data/test_sorted.tsv \
                  -i uw-clustering_static_a%s -av %s -an %s -gvi 1 -gvd 1 -gni 1 -gnd 1 -s 0 -c ../../../clustering/ -rnrl ../../../clustering/model/rnr.pkl \
                  > ../../../clustering/logs/uw-clustering_static_a%s.log' % (name, name, alpha, alpha, name)
    print clustering_static
    os.system(clustering_static)

if __name__ == '__main__':
  main()