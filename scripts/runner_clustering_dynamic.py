#!/usr/bin/env python
import os

def main():

  gammas_increase = [0.1, 0.5, 0.9]
  gammas_decrease = [100, 200, 500]
  gammas_increase_name = ['01', '05', '09']
  gammas_decrease_name = ['100', '200', '500']

  for gamma_decrease, gamma_decrease_name in zip(gammas_decrease, gammas_decrease_name):
    for gamma_increase, gamma_increase_name in zip(gammas_increase, gammas_increase_name):
      clu_dyn = 'nohup ../../../../py_virtual/bin/python -u clustering_uv.py -e ../../../clustering/misc/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                -tr ../../../clustering/outputs/train_r_clu_dyn_a08_gd%s_gi%s_exp_global.tsv \
                -t ../../../clustering/outputs/test_r_clu_dyn_a08_gd%s_gi%s_exp_global.tsv \
                -i clu_dyn_a08_gd%s_gi%s_exp_global -rnrl ../../../clustering/model/rnr.pkl \
                -nr ../../../clustering/misc/nr.txt \
                -o ../../../clustering/outputs/uw-clu_dyn_a08_gd%s_gi%s \
                > ../../../clustering/logs/uw-clu_dyn_a08_gd%s_gi%s_exp_global.log' % (gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name)
      print clu_dyn
      os.system(clu_dyn)

if __name__ == '__main__':
  main()