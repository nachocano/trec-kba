import os
import argparse
from collections import defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-f', '--file', required=True)
  parser.add_argument('-o', '--output', required=True)
  args = parser.parse_args()

  docids = defaultdict(lambda: [])
  
  targetids = defaultdict(list)
  for line in open(args.file).read().splitlines():
    splitted = line.split()
    targetid = splitted[3]
    key = targetid[targetid.rfind('/')+1:]
    targetids[key].append(line)

  files = {}
  for key in targetids:
    files[key] = open(os.path.join(args.output, key), 'w')

  for key, l in targetids.iteritems():
    for value in l:
      files[key].write('%s\n' % value)

  for f in files:
    files[f].close()


if __name__ == '__main__':
  main()

