import re
import argparse
import fileinput
from collections import defaultdict

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-s', '--stream_file', required=True)
  parser.add_argument('-m', '--mapping_file', required=True)
  args = parser.parse_args()

  folder_regex = re.compile(r'/(20\d{2}-\d{2}-\d{2}-\d{2})/')
  docids = defaultdict(lambda: [])
  
  for line in open(args.stream_file).read().splitlines():
    splitted = line.split('-')[1]
    docids[splitted[:16]].append(line)

  for line in fileinput.input([args.mapping_file]):
    splitted = line.split('#')
    key = splitted[1][:-1]
    if docids.has_key(key):
      for docid in docids[key]:
        print '%s\t%s' % (docid, splitted[0])

if __name__ == '__main__':
  main()

