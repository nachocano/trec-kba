#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--entity_text_file', required=True)
    parser.add_argument('-at', '--all_test_file', required=True)
    parser.add_argument('-et', '--test_file', required=True)
    args = parser.parse_args()

    target = 'https://kb.diffeo.com/' + args.entity_text_file[args.entity_text_file.rfind('/')+6:]
    print target

    streamid_text = {}
    with open(args.entity_text_file) as f:
        for line in f.read().splitlines():
            splitted = line.split('\t')
            streamid = splitted[0]
            text = splitted[1]
            streamid_text[streamid] = text

    streamid_pos = {}
    streamid_pos['nouns'] = {}
    streamid_pos['verbs'] = {}
    with open(args.all_test_file) as f:
        for line in f.read().splitlines():
            delimiter = line.find('[')
            fixed = line[:delimiter-1]
            splitted_fixed = fixed.split()
            streamid = splitted_fixed[0]
            targetid = splitted_fixed[1]
            if targetid == target and streamid_text.has_key(streamid):
                two_arrays = line[delimiter:]
                nouns = two_arrays[1:two_arrays.find(']')].split(',')
                verbs = two_arrays[two_arrays.rfind('[')+1:-1].split(',')
                streamid_pos['nouns'][streamid] = nouns
                streamid_pos['verbs'][streamid] = verbs

    features = {}
    with open(args.test_file) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            if targetid == target and streamid_text.has_key(streamid):
                date_hour = instance[2]
                label = instance[3]
                fixed_features = instance[4:29]
                nouns_embeddings = instance[29:329]
                verbs_embeddings = instance[329:629]
                clustering_nouns = instance[629:633]
                clustering_verbs = instance[633:637]
                entity_timeliness = instance[637]
                features[streamid] = (fixed_features, nouns_embeddings, verbs_embeddings, clustering_nouns, clustering_verbs, entity_timeliness)

    for streamid in streamid_text:
        print 'streamid %s' % streamid
        feat = features[streamid]
        nouns = streamid_pos['nouns'][streamid]
        verbs = streamid_pos['verbs'][streamid]
        print 'entity_timeliness %s' % feat[5]
        print 'clustering_nouns %s' % feat[3]
        print 'clustering_verbs %s' % feat[4]
        print 'fixed_features %s' % feat[0]
        print 'nouns %s' % nouns
        print 'verbs %s' % verbs
        print 'text %s' % streamid_text[streamid]
        print ''


if __name__ == '__main__':
  main()
