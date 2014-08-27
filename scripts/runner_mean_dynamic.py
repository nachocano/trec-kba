#!/usr/bin/env python
import os

def main():
  gammas = [0.2,0.4,0.6,0.8]
  gammas_name = ['02','04','06','08']
  for gamma, name in zip(gammas, gammas_name):
    mean_dynamic = 'nohup ../../../../py_virtual/bin/python -u gbt_clustering.py -e ../../../clustering/data/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                  -o ../../../clustering/outputs/uw-mean_dynamic_g%s.txt -tr ../../../clustering/data/train_sorted.tsv -t ../../../clustering/data/test_sorted.tsv \
                  -i uw-mean_dynamic_g%s -av 1 -an 1 -gvi %s -gvd %s -gni %s -gnd %s -s 0 -c ../../../clustering/ -rnrl ../../../clustering/model/rnr.pkl \
                  > ../../../clustering/logs/uw-mean_dynamic_g%s.log' % (name, name, gamma, gamma, gamma, gamma, name)
    print mean_dynamic
    os.system(mean_dynamic)

if __name__ == '__main__':
  main()