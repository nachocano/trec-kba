#!/usr/bin/env python
import os

def main():

  gamma_increase = (0.1, '01')
  gamma_decrease = (0.1, '01')
  alphas = [(0.6, '06'), (0.8, '08')]

  for alpha, alpha_name in alphas:
    cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr test_r_lsi_dense.txt \
              -trr train_r_lsi_dense.txt -ot lsi/test_r_lsi_a%s_gd%s_gi%s.txt \
              -otr lsi/train_r_lsi_a%s_gd%s_gi%s.txt \
              -an %s -av %s -gnd %s -gvd %s -gni %s -gvi %s -tn 86400 \
              > logs/uw-lsi_clu_dyn_a%s_gd%s_gi%s_feature.log' % (alpha_name, gamma_decrease[1], gamma_increase[1], alpha_name, gamma_decrease[1], gamma_increase[1], alpha, alpha, gamma_decrease[0], gamma_decrease[0], gamma_increase[0], gamma_increase[0],alpha_name, gamma_decrease[1], gamma_increase[1])
    print cmd
    os.system(cmd)

  # mean dyn
  cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr test_r_lsi_dense.txt \
            -trr train_r_lsi_dense.txt -ot lsi/test_r_lsi_a1_gd1_gi01.txt \
            -otr lsi/train_r_lsi_a1_gd1_gi01.txt \
            -an 1 -av 1 -gnd 1 -gvd 1 -gni 0.1 -gvi 0.1 -tn 86400 \
            > logs/uw-lsi_mean_dyn_feature.log'
  print cmd
  os.system(cmd)

  # clust static
  for alpha, alpha_name in alphas:
    cmd = 'nohup java -jar treckba-jar-with-dependencies.jar -tr test_r_lsi_dense.txt \
              -trr train_r_lsi_dense.txt -ot lsi/test_r_lsi_a%s_gd0_gi1.txt \
              -otr lsi/train_r_lsi_a%s_gd0_gi1.txt \
              -an %s -av %s -gnd 0 -gvd 0 -gni 1 -gvi 1 -tn 86400 \
              > logs/uw-lsi_clust_stat_a%s_feature.log' % (alpha_name, alpha_name, alpha, alpha, alpha_name)
    print cmd
    os.system(cmd)  

if __name__ == '__main__':
  main()
