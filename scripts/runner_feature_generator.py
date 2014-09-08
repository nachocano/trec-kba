#!/usr/bin/env python
import os

def main():

  gammas_increase = [0.1, 0.5, 0.9]
  gammas_decrease = [100, 200, 500]
  gammas_increase_name = ['01', '05', '09']
  gammas_decrease_name = ['100', '200', '500']

  for gamma_decrease, gamma_decrease_name in zip(gammas_decrease, gammas_decrease_name):
    for gamma_increase, gamma_increase_name in zip(gammas_increase, gammas_increase_name):
      cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr ../data/test_r.tsv \
                -trr ../data/train_r.tsv -ot ../outputs/test_r_clu_dyn_a08_gd%s_gi%s_exp_global.tsv \
                -otr ../outputs/train_r_clu_dyn_a08_gd%s_gi%s_exp_global.tsv \
                -an 0.8 -av 0.8 -gnd %s -gvd %s -gni %s -gvi %s -tn 86400 \
                > ../logs/uw-clu_dyn_a08_gd%s_gi%s_exp_global.log' % (gamma_decrease_name, gamma_increase_name, gamma_decrease_name, gamma_increase_name, gamma_decrease, gamma_decrease, gamma_increase, gamma_increase, gamma_decrease_name, gamma_increase_name)
      print cmd
      os.system(cmd)

if __name__ == '__main__':
  main()