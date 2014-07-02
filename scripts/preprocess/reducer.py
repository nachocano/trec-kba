#!/usr/bin/python
import sys
from collections import defaultdict

def log_err(msg):
    sys.stderr.write('%s' % msg)
    sys.stderr.flush()
    
def main(argv):
    entity2doc = defaultdict(set)
    for line in sys.stdin:
        kv = line.split('\t')
        if len(kv) == 2 and kv[0] != '' and kv[1] != '':
            entity2doc[kv[0]].add(kv[1])
    for entity in entity2doc:
        print '%s\t%s' % (entity, ','.join(entity2doc[entity]))
        
if __name__ == '__main__':
    main(sys.argv)