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
  parser.add_argument('-json', '--json_folder', required=True)
  args = parser.parse_args()

  run = defaultdict(defaultdict)
  with open(args.run_file) as f:
    for line in f.read().splitlines():
      l = line.strip()
      if l.startswith('#'):
          continue
      l = l.split('\t')
      streamid = l[2]
      entity = l[3][l[3].rfind('/')+1:]
      score = int(l[4])
      relevance = int(l[5])
      run[entity][streamid] = (relevance, score)

  onlyfiles = [ join(args.json_folder,f) for f in listdir(args.json_folder) if isfile(join(args.json_folder,f)) ]
  
  for filename in onlyfiles:
    with open(filename, 'r') as f:
      entity = filename[filename.rfind('/')+1:filename.rfind('.')]
      json_file = json.load(f)
      for d in json_file:
        if d['relevance'] == -10:
          d['relevance'] = run[entity][d['streamid']][0]
          d['score'] = run[entity][d['streamid']][1]

    tmp_file = filename + '.partial'
    with open(tmp_file, 'w') as f:
      f.write(json.dumps(json_file))
    rename(tmp_file, filename)
  
if __name__ == '__main__':
  main()

