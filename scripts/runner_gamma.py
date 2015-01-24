#!/usr/bin/env python
import os

def main():

  gammas_increase = [(0.1, '01'),(0.5, '05')]
  gammas_decrease = [(10, '10'), (100, '100')]
  alphas = [(0.8, '08'), (0.9, '09')]

  for alpha, alpha_name in alphas:
    for gammai, gammai_name in gammas_increase:
      for gammad, gammad_name in gammas_decrease:
        print 'here'
        cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr test_r_lsi_dense.txt \
              -trr train_r_lsi_dense.txt -ot lsigamma/test_r_lsi_a%s_gd%s_gi%s.txt \
              -otr lsigamma/train_r_lsi_a%s_gd%s_gi%s.txt \
              -an %s -av %s -gnd %s -gvd %s -gni %s -gvi %s -tn 86400 \
              > logs/uw-lsi_clu_dyn_a%s_gd%s_gi%s_feature.log' % (alpha_name, gammad_name, gammai_name, alpha_name, gammad_name, gammai_name, alpha, alpha, gammad, gammad, gammai, gammai,alpha_name, gammad_name, gammai)
        print cmd
        os.system(cmd)

if __name__ == '__main__':
  main()
