#!/usr/bin/python
from __future__ import division
import argparse

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-if', '--input_file', required=True)
  args = parser.parse_args()

  for line in open(args.input_file).read().splitlines():
    tokens = line.split()
    assert len(tokens) == 329
    fixed = ' '.join(tokens[:29])
    rest = tokens[29:]
    assert len(rest) == 300
    new = []
    for value in rest:
      new.append(value.split(',')[1])
    transformed = ' '.join(new)
    print '%s %s' % (fixed, transformed)

if __name__ == '__main__':
  main()

