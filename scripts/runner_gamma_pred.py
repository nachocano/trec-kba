#!/usr/bin/env python
import os

def main():

  gammas_increase = [(0.1, '01'),(0.5, '05')]
  gammas_decrease = [(10, '10'), (100, '100')]
  alphas = [(0.8, '08'), (0.9, '09')]

  for alpha, alpha_name in alphas:
    for gammai, gammai_name in gammas_increase:
      for gammad, gammad_name in gammas_decrease:
        clu_dyn = 'nohup ~/py_virtual/bin/python -u repo/trec-kba/scripts/clustering_uv.py -e trec-kba-2014-07-11-ccr-and-ssf-query-topics.json \
              -tr lsigamma/train_r_lsi_a%s_gd%s_gi%s.txt \
              -t lsigamma/test_r_lsi_a%s_gd%s_gi%s.txt \
              -i clu_dyn_a%s_gd%s_gi%s \
              -nr nr.txt \
              -o outputsgamma/uw-lsi_clu_dyn_a%s_gd%s_gi%s \
              > logs/uw-lsi_clu_dyn_a%s_gd%s_gi%s.log' % (alpha_name, gammad_name, gammai_name, alpha_name, 
                gammad_name, gammad_name, alpha_name, gammad_name, gammai_name, alpha_name, gammad_name, gammai_name,
                alpha_name, gammad_name, gammai_name)
        print clu_dyn
        os.system(clu_dyn)

if __name__ == '__main__':
  main()    