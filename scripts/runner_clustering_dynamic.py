#!/usr/bin/env python
import os

def main():
  
  alphas = [0.2,0.6]
  alphas_name = ['02', '06']
  gammas = [0.4,0.8]
  gammas_name = ['04', '08']
  
  for alpha, alpha_name in zip(alphas, alphas_name):
    for gamma, gamma_name in zip(gammas, gammas_name):
      clustering_dynamic = 'nohup ../../../../py_virtual/bin/python -u gbt_clustering.py -e ../../../clustering/data/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                  -o ../../../clustering/data/outputs/uw-clustering_dynamic_a%s_g%s.txt -tr ../../../clustering/data/train_sorted.tsv -t ../../../clustering/data/test_sorted.tsv \
                  -i uw-clustering_dynamic_a%s_g%s -av %s -an %s -gvi %s -gvd %s -gni %s -gnd %s -s 0 -c ../../../clustering/ -rnrl ../../../clustering/model/rnr.pkl \
                  > ../../../clustering/logs/uw-clustering_dynamic_a%s_g%s.log' % (alpha_name, gamma_name, alpha_name, gamma_name, alpha, alpha, gamma, gamma, gamma, gamma, alpha_name, gamma_name)
      print clustering_dynamic
      os.system(clustering_dynamic)

if __name__ == '__main__':
  main()