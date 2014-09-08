#!/usr/bin/env python
import os

def main():

  gammas_increase = ['01', '05', '09']
  gammas_decrease = ['100', '200', '500']

  for gamma_decrease in gammas_decrease:
    for gamma_increase in gammas_increase:
      debugging = 'nohup ../../../../py_virtual/bin/python -u debugging.py \
                  -tr ../../../clustering/outputs/train_r_clu_dyn_a08_gd%s_gi%s_exp_global.tsv \
                  -t ../../../clustering/outputs/test_r_clu_dyn_a08_gd%s_gi%s_exp_global.tsv \
                  -r ../../../clustering/outputs/uw-clu_dyn_a08_gd%s_gi%s \
                  -o ../../../clustering/plots/uw-clu_dyn_a08_gd%s_gi%s' % (gamma_decrease, gamma_increase, gamma_decrease, gamma_increase, gamma_decrease, gamma_increase, gamma_decrease, gamma_increase)
      print debugging
      os.system(debugging)

if __name__ == '__main__':
  main()