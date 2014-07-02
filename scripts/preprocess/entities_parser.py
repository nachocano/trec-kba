import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

profiles = yaml.load(open(args.input))
total_entities = 0
entities_with_canonical = 0
entities_with_name = 0
for entity in profiles['entities']:
	total_entities += 1
	slots = entity.get('slots', [])
	target_canonical_name = ''
	target_surface_forms = ''
	has_name = False
	has_canonical = False
	for slot in slots:
		if (slot.get('canonical_name')):
			entities_with_canonical +=1
			has_canonical = True
			canonical_name = slot.get('canonical_name')
			if type(canonical_name) is str:
				target_canonical_name = canonical_name.strip().lower()
			elif type(canonical_name) is dict:
				target_canonical_name = canonical_name.get('value').strip().lower()
		elif (slot.get('NAME')):
			entities_with_name += 1
			has_name = True
			name = slot.get('NAME')
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
	if has_canonical and has_name:
		print '%s|%s' % (target_canonical_name, target_surface_forms)
	elif has_canonical:
		print '%s' % target_canonical_name

#print '\nstats: total=%d, canonical=%d, name=%d' % (total_entities, entities_with_canonical, entities_with_name) 