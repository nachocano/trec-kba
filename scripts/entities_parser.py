import argparse
import yaml

def extract_name(name):
  target_surface_forms = ''
  if type(name) is str:
    target_surface_forms += name.strip().lower()
  elif type(name) is dict:
    target_surface_forms += name.get('value').strip().lower()
  elif type(name) is list:
    aux = []
    for e in name:
      if type(e) is str:
        aux.append(e.strip().lower())
      elif type(e) is dict:
        aux.append(e.get('value').strip().lower())
    target_surface_forms += ",".join(aux)
  return target_surface_forms


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('yaml')
  parser.add_argument('entities_filtered')
  args = parser.parse_args()

  target_entities = {}
  for target_entity in open(args.entities_filtered).read().splitlines():
    target_entities[target_entity] = True

  profiles = yaml.load(open(args.yaml))
  total_canonical = 0
  total_surface = 0

  for label, entity in profiles['entities'].items():
    if target_entities.has_key(label):
      has_surface = False
      canonical = ''
      surface = ''
      for slot_name, slot_value in entity['slots'].items():
        if slot_name == 'canonical_name':
          total_canonical += 1
          canonical = slot_value.strip().lower()
        if slot_name == 'PER_NAME' or slot_name == 'ORG_NAME' or slot_name == 'FAC_NAME':
          total_surface += 1
          has_surface = True
          surface = extract_name(slot_value)
      if has_surface:
        print '%s|%s,%s' % (label, canonical, surface)
      else:
        print '%s|%s' % (label,canonical)

  #print '\nstats: canonical=%d, surface=%d' % (total_canonical, total_surface)

if __name__ == '__main__':
  main()
