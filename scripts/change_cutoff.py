#!/usr/bin/python
import argparse
import time
from collections import defaultdict
from os import listdir
from os.path import isfile, join
from os import rename
import json


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-r', '--run_file', required=True)
  args = parser.parse_args()

  run = defaultdict(defaultdict)
  with open(args.run_file) as f:
    for line in f.read().splitlines():
      l = line.strip()
      if l.startswith('#'):
          print line
          continue
      l = l.split('\t')
      score = int(l[4])
      relevance = int(l[5])
      if relevance == 1:
        score = 1000 - score
        if score == 0:
          score = 1
        assert score > 0 and score <= 1000
        relevance = 2
        print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (l[0],l[1],l[2],l[3],score,relevance,l[6],l[7],l[8],l[9],l[10])
      else:
        print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (l[0],l[1],l[2],l[3],score,relevance,l[6],l[7],l[8],l[9],l[10])

  
if __name__ == '__main__':
  main()


#UW  mean_dyn_a1_gd1_gi01  1322091960-7581d43dded078be851aa7b6963ded31 https://kb.diffeo.com/Brodie_Clowes 646 0 1 2011-11-23-23 NULL  -1  0-0
# No newline at end of file
