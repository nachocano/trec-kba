#!/usr/bin/python
from __future__ import division
import argparse
import numpy as np
from gensim import matutils

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_file', required=True)
  args = parser.parse_args()

  for line in open(args.input_file).read().splitlines():
    tokens = line.split()
    fixed = ' '.join(tokens[:29])
    dense = np.zeros(300)
    rest = tokens[29:] 
    for value in rest:
      index, v = value.split(',')
      dense[int(index)] = float(v)
    dense = matutils.unitvec(dense).astype(np.float32)
    dense = ' '.join(str(v) for v in list(dense))  
    print '%s %s' % (fixed, dense)

if __name__ == '__main__':
  main()

