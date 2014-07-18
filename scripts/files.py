import re
import argparse

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-f', '--folders_file', required=True)
  parser.add_argument('-p', '--paths_file', required=True)
  args = parser.parse_args()

  folder_regex = re.compile(r'/(20\d{2}-\d{2}-\d{2}-\d{2})/')
  folders = {}
  for line in open(args.folders_file).read().splitlines():
    folders[line] = True

  for line in open(args.paths_file).read().splitlines():
    if folders.has_key(re.search(folder_regex, line).group(1)):
      print line
 
if __name__ == '__main__':
  main()

