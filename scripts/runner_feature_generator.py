#!/usr/bin/env python
import os

def main():

  gammas_increase = [(0.1, '01'), (0.5, '05'), (0.9, '09')]
  gammas_decrease = [(0.1, '01'), (0.5, '0.5'), (1, '1'), (10, '10'), (20, '20'), (50, '50'), (100, '100'), (200, '200')]

  for gamma_decrease, gamma_decrease_name in gammas_decrease:
    for gamma_increase, gamma_increase_name in gammas_increase:
      cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr ../data/test_r.tsv \
                -trr ../data/train_r.tsv -ot ../outputs/test_r_clu_dyn_a08_gd%s_gi%s_p.tsv \
                -otr ../outputs/train_r_clu_dyn_a08_gd%s_gi%s_p.tsv \
                -an 0.8 -av 0.8 -gnd %s -gvd %s -gni %s -gvi %s -tn 86400 \
                > ../logs/uw-clu_dyn_a08_gd%s_gi%s_p_feature.log' % (gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease, gamma_decrease, gamma_increase, gamma_increase, gamma_decrease_name, gamma_increase_name)
      print cmd
      os.system(cmd)

if __name__ == '__main__':
  main()