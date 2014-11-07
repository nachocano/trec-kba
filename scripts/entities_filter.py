import json
import argparse
from pprint import pprint

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-e', '--entities_file', required=True)
  args = parser.parse_args()

  json_data=open(args.entities_file)
  targets = json.load(json_data)['targets']
  for target in targets:
    if target['training_time_range_end']:
      targetid = target['target_id']
      targetid = targetid[targetid.rfind("/")+1:]
      name = target['canonical_name']
      print "%s\t%s" % (targetid, name)

if __name__ == '__main__':
  main()

