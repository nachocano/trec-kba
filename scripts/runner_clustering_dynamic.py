#!/usr/bin/env python
import os

def main():

  gammas_name = ['02', '04', '06','08','1','2','5','10','20']
  
  for gamma_name in gammas_name:
    clu_dyn = 'nohup ../../../../py_virtual/bin/python -u clustering_uv.py -e ../../../clustering/misc/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                -tr ../../../clustering/outputs/train_r_clu_dyn_a08_gd%s_gi04_exp_global.tsv \
                -t ../../../clustering/outputs/test_r_clu_dyn_a08_gd%s_gi04_exp_global.tsv \
                -i clu_dyn_a08_gd%s_gi04_exp_global -rnrl ../../../clustering/model/rnr.pkl \
                -nr ../../../clustering/misc/nr.txt \
                -o ../../../clustering/outputs/uw-clu_dyn_a08_gd%s_gi04 \
                > ../../../clustering/logs/uw-clu_dyn_a08_gd%s_gi04_exp_global.log' % (gamma_name, gamma_name, gamma_name, gamma_name, gamma_name)
    print clu_dyn
    os.system(clu_dyn)

if __name__ == '__main__':
  main()