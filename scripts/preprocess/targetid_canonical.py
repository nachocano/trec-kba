import argparse
import yaml

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('input')
	args = parser.parse_args()

	profiles = yaml.load(open(args.input))
	for label, entity in profiles['entities'].items():
		for slot_name, slot_value in entity['slots'].items():
			if slot_name == 'canonical_name':
				print '%s\t%s' % (label, slot_value)
				break	

if __name__ == '__main__':
	main()