#!/usr/bin/env python
import os

def main():

  # change this
  gamma_increase = (0.5, '05')
  gamma_decrease = (10, '10')
  alpha = 0.8
  alpha_name = '08'

  clu_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr bow/train_r_bow_a%s_gd%s_gi%s.txt \
            -t bow/test_r_bow_a%s_gd%s_gi%s.txt \
            -i clu_dyn_a%s_gd%s_gi%s \
            -nr nr.txt \
            -o outputsbow/uw-bow_clu_dyn_a%s_gd%s_gi%s \
            > logs/uw-bow_clu_dyn_a%s_gd%s_gi%s.log' % (alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1])
  print clu_dyn
  os.system(clu_dyn)

  # mean dynamic    
  mean_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr bow/train_r_bow_a1_gd10_gi05.txt \
            -t bow/test_r_bow_a1_gd10_gi05.txt \
            -i mean_dyn_a1_gd10_gi05 \
            -nr nr.txt \
            -o outputsbow/uw-bow_mean_dyn_a1_gd10_gi05 \
            > logs/uw-bow_mean_dyn_a1_gd10_gi05.log'
  print mean_dyn
  os.system(mean_dyn)

  clu_stat = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr bow/train_r_bow_a%s_gd0_gi1.txt \
            -t bow/test_r_bow_a%s_gd0_gi1.txt \
            -i clu_stat_a%s_gd0_gi1 \
            -nr nr.txt \
            -o outputsbow/uw-bow_clu_stat_a%s_gd0_gi1 \
            > logs/uw-bow_clu_stat_a%s_gd0_gi1.log' % (alpha_name, alpha_name, alpha_name, alpha_name, alpha_name)
  print clu_stat
  os.system(clu_stat)

if __name__ == '__main__':
  main()
