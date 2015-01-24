#!/usr/bin/env python
import os

def main():

  gamma_increase = (0.1, '01')
  gamma_decrease = (0.1, '01')
  alphas = [(0.6, '06'), (0.8, '08')]

  for alpha, alpha_name in alphas:
    clu_dyn = 'nohup ~/py_virtual/bin/python -u repo/treckba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
              -tr lsi/train_r_lsi_a%s_gd%s_gi%s.txt \
              -t lsi/test_r_lsi_a%s_gd%s_gi%s.txt \
              -i clu_dyn_a%s_gd%s_gi%s \
              -nr nr.txt \
              -o outputs/uw-lsi_clu_dyn_a%s_gd%s_gi%s \
              > logs/uw-lsi_clu_dyn_a%s_gd%s_gi%s.log' % (alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1])
    print clu_dyn
    os.system(clu_dyn)

  # mean dynamic    
  mean_dyn = 'nohup ~/py_virtual/bin/python -u repo/treckba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr lsi/train_r_lsi_a1_gd1_gi01.txt \
            -t lsi/test_r_lsi_a1_gd1_gi01.txt \
            -i mean_dyn_a1_gd1_gi01 \
            -nr nr.txt \
            -o outputs/uw-lsi_mean_dyn_a1_gd1_gi01 \
            > logs/uw-lsi_mean_dyn_a1_gd1_gi01.log'
  print mean_dyn
  os.system(mean_dyn)

  # clust static
  for alpha, alpha_name in alphas:
    clu_stat = 'nohup ~/py_virtual/bin/python -u repo/treckba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
              -tr lsi/train_r_lsi_a%s_gd0_gi1.txt \
              -t lsi/test_r_lsi_a%s_gd0_gi1.txt \
              -i clu_dyn_a%s_gd0_gi1 \
              -nr nr.txt \
              -o outputs/uw-lsi_clu_dyn_a%s_gd0_gi1 \
              > logs/uw-lsi_clu_dyn_a%s_gd0_gi1.log' % (alpha_name, alpha_name, alpha_name, alpha_name)
    print clu_stat
    os.system(clu_stat)

if __name__ == '__main__':
  main()