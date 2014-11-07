#!/usr/bin/python
import argparse
import matplotlib.pyplot as plt

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-o', '--overview_file', required=True)
  args = parser.parse_args()

  runs = {}
  with open(args.overview_file) as f:
    for line in f.read().splitlines():
      if line.startswith("#"):
        continue
      line = line.split(",")
      print '%s,%s,%s,%s' % (line[1], line[6], line[7], line[8])
      #runs[line[1]] = (float(line[6]), float(line[7]), float(line[8])

if __name__ == '__main__':
  main()