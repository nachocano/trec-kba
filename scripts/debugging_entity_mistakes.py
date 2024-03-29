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
    #print target

    streamid_text = {}
    with open(args.entity_text_file) as f:
        for line in f.read().splitlines():
            splitted = line.split('\t')
            streamid = splitted[0]
            res = splitted[1]
            text = splitted[2]
            streamid_text[streamid] = (res, text)

    streamid_pos = {}
    streamid_pos['nouns'] = {}
    streamid_pos['verbs'] = {}
    streamid_pos['proper_nouns'] = {}
    with open(args.all_test_file) as f:
        for line in f.read().splitlines():
            delimiter = line.find('[')
            fixed = line[:delimiter-1]
            splitted_fixed = fixed.split()
            streamid = splitted_fixed[0]
            targetid = splitted_fixed[1]
            if targetid == target and streamid_text.has_key(streamid):
                three_arrays = line[delimiter:]
                nouns_delimiter = three_arrays.find(']')
                nouns = three_arrays[1:nouns_delimiter].split(',')
                nouns = filter(lambda x: x != '', nouns)
                two_arrays = three_arrays[nouns_delimiter+2:]
                verbs = two_arrays[1:two_arrays.find(']')].split(',')
                verbs = filter(lambda x: x != '', verbs)
                proper_nouns = two_arrays[two_arrays.rfind('[')+1:-1].split(',')
                proper_nouns = filter(lambda x: x != '', proper_nouns)
                streamid_pos['nouns'][streamid] = nouns
                streamid_pos['verbs'][streamid] = verbs
                streamid_pos['proper_nouns'][streamid] = proper_nouns

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
                proper_nouns_embeddings = instance[629:929]
                clustering_nouns = instance[929:933]
                clustering_verbs = instance[933:937]
                entity_timeliness = instance[937]
                features[streamid] = (fixed_features, nouns_embeddings, verbs_embeddings, proper_nouns_embeddings, clustering_nouns, clustering_verbs, entity_timeliness)

    #sorted(streamid_text, key=lambda key: streamid_text[key])
    for streamid, val in sorted(streamid_text.iteritems(), key=lambda k : k):
        res = val[0]
        text = val[1]
        print 'streamid %s - %s' % (streamid, res)
        feat = features[streamid]
        nouns = streamid_pos['nouns'][streamid]
        verbs = streamid_pos['verbs'][streamid]
        proper_nouns = streamid_pos['proper_nouns'][streamid]
        print 'entity_timeliness %s' % feat[6]
        print 'clustering_nouns %s' % feat[4]
        print 'clustering_verbs %s' % feat[5]
        print 'fixed_features %s' % feat[0]
        print 'nouns %s' % nouns
        print 'verbs %s' % verbs
        print 'proper n %s' % proper_nouns
        print 'text %s' % text
        print ''


if __name__ == '__main__':
  main()
