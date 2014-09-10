#!/usr/bin/env python
import os

def main():

  gammas_increase = [(0.1, '01'), (0.5, '05'), (0.9, '09')]
  gammas_decrease = [(0.1, '01'), (0.5, '0.5'), (1, '1'), (10, '10'), (20, '20'), (50, '50'), (100, '100'), (200, '200')]

  for gamma_decrease, gamma_decrease_name in gammas_decrease:
    for gamma_increase, gamma_increase_name in gammas_increase:
      clu_dyn = 'nohup ../../../../py_virtual/bin/python -u clustering_uv.py -e ../../../last_clustering/misc/trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
                -tr ../../../last_clustering/outputs/train_r_clu_dyn_a08_gd%s_gi%s_p.tsv \
                -t ../../../last_clustering/outputs/test_r_clu_dyn_a08_gd%s_gi%s_p.tsv \
                -i clu_dyn_a08_gd%s_gi%s_p -rnrl ../../../last_clustering/model/rnr.pkl \
                -nr ../../../last_clustering/misc/nr.txt \
                -o ../../../last_clustering/outputs/uw-clu_dyn_a08_gd%s_gi%s_p \
                > ../../../last_clustering/logs/uw-clu_dyn_a08_gd%s_gi%s_p.log' % (gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name)
      print clu_dyn
      os.system(clu_dyn)

if __name__ == '__main__':
  main()