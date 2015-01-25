#!/usr/bin/env python
import os

def main():

  # change this
  gamma_increase = (0.5, '05')
  gamma_decrease = (10, '10')
  alpha = 0.8
  alpha_name = '08'

  normal = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr train_r_wordemb.txt \
            -t test_r_wordemb.txt \
            -i emb_normal \
            -nr nr.txt \
            -o outputsemb/uw-emb_normal \
            > logs/uw-emb_normal.log'
  print normal
  os.system(normal)

  clu_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr emb/train_r_emb_a%s_gd%s_gi%s.txt \
            -t emb/test_r_emb_a%s_gd%s_gi%s.txt \
            -i clu_dyn_a%s_gd%s_gi%s \
            -nr nr.txt \
            -o outputsemb/uw-emb_clu_dyn_a%s_gd%s_gi%s \
            > logs/uw-emb_clu_dyn_a%s_gd%s_gi%s.log' % (alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1])
  print clu_dyn
  os.system(clu_dyn)

  # mean dynamic    
  mean_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr emb/train_r_emb_a1_gd10_gi05.txt \
            -t emb/test_r_emb_a1_gd10_gi05.txt \
            -i mean_dyn_a1_gd10_gi05 \
            -nr nr.txt \
            -o outputsemb/uw-emb_mean_dyn_a1_gd10_gi05 \
            > logs/uw-emb_mean_dyn_a1_gd10_gi05.log'
  print mean_dyn
  os.system(mean_dyn)

  clu_stat = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
            -tr emb/train_r_emb_a%s_gd0_gi1.txt \
            -t emb/test_r_emb_a%s_gd0_gi1.txt \
            -i clu_stat_a%s_gd0_gi1 \
            -nr nr.txt \
            -o outputsemb/uw-emb_clu_stat_a%s_gd0_gi1 \
            > logs/uw-emb_clu_stat_a%s_gd0_gi1.log' % (alpha_name, alpha_name, alpha_name, alpha_name, alpha_name)
  print clu_stat
  os.system(clu_stat)

if __name__ == '__main__':
  main()
