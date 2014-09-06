#!/usr/bin/env python
import os

def main():

  gamma_increase = 0.4
  gammas_decrease = [0.2,0.4,0.6,0.8,1,2,5,10,20]
  gammas_name = ['02', '04', '06','08','1','2','5','10','20']
  
  for gamma_decrease, gamma_name in zip(gammas_decrease, gammas_name):
    cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr ../data/test_r.tsv \
                -trr ../data/train_r.tsv -ot ../outputs/test_r_clu_dyn_a08_gd%s_gi04_exp_global.tsv \
                -otr ../outputs/train_r_clu_dyn_a08_gd%s_gi04_exp_global.tsv \
                -an 0.8 -av 0.8 -gnd %s -gvd %s -gni 0.4 -gvi 0.4 -tn 86400 \
                > ../logs/uw-clu_dyn_a08_gd%s_gi04_exp_global.log' % (gamma_name, gamma_name, gammas_decrease, gammas_decrease, gamma_name)
    print cmd
    os.system(cmd)

if __name__ == '__main__':
  main()