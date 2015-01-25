#!/usr/bin/env python
import os

def main():

  # change this
  gamma_increase = (0.5, '0.5')
  gamma_decrease = (10, '10')
  alpha = 0.8
  alpha_name = '08'

  normal = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr train_r_lda.txt \
            -t test_r_lda.txt \
            -i lda_normal \
            -nr nr.txt \
            -o outputslda/uw-lda_normal \
            > logs/uw-lda_normal.log'
  print normal
  os.system(normal)

  clu_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr lda/train_r_lda_a%s_gd%s_gi%s.txt \
            -t lda/test_r_lda_a%s_gd%s_gi%s.txt \
            -i clu_dyn_a%s_gd%s_gi%s \
            -nr nr.txt \
            -o outputslda/uw-lda_clu_dyn_a%s_gd%s_gi%s \
            > logs/uw-lda_clu_dyn_a%s_gd%s_gi%s.log' % (alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1])
  print clu_dyn
  os.system(clu_dyn)

  # mean dynamic    
  mean_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr lda/train_r_lda_a1_gd10_gi05.txt \
            -t lda/test_r_lda_a1_gd10_gi05.txt \
            -i mean_dyn_a1_gd10_gi05 \
            -nr nr.txt \
            -o outputslda/uw-lda_mean_dyn_a1_gd10_gi05 \
            > logs/uw-lda_mean_dyn_a1_gd10_gi05.log'
  print mean_dyn
  os.system(mean_dyn)

  clu_stat = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr lda/train_r_lda_a%s_gd0_gi1.txt \
            -t lda/test_r_lda_a%s_gd0_gi1.txt \
            -i clu_stat_a%s_gd0_gi1 \
            -nr nr.txt \
            -o outputslda/uw-lda_clu_stat_a%s_gd0_gi1 \
            > logs/uw-lda_clu_stat_a%s_gd0_gi1.log' % (alpha_name, alpha_name, alpha_name, alpha_name, alpha_name)
  print clu_stat
  os.system(clu_stat)

if __name__ == '__main__':
  main()
