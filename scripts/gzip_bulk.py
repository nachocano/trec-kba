#!/usr/bin/python
import argparse
from os import listdir
from os import system
from os.path import isfile, join
from os import rename

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-r', '--run_folder', required=True)
  args = parser.parse_args()

  for f in listdir(args.run_folder):
    filename = join(args.run_folder, f)
    system('cat %s | gzip > %s.gz' % (filename, filename))

if __name__ == '__main__':
  main()

