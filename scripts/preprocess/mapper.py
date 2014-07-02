#!/usr/bin/python
import os
import sys
import subprocess
import urllib
import traceback
import zipimport
from cStringIO import StringIO
from collections import defaultdict


# hack to import thrift and streamcorpus
thrift_importer = zipimport.zipimporter('thrift.mod')
thrift = thrift_importer.load_module('thrift')
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
streamcorpus_importer = zipimport.zipimporter('streamcorpus.mod')
streamcorpus = streamcorpus_importer.load_module('streamcorpus')
from streamcorpus.ttypes import StreamItem

PATH = "http://s3.amazonaws.com/aws-publicdatasets/trec/kba/kba-streamcorpus-2014-v0_3_0-serif-only/"

def log_err(msg):
    sys.stderr.write('%s' % msg)
    sys.stderr.flush()
    
def read_entities(filename):
    target_entities = defaultdict(list)
    with open(filename,'r') as f:
        for line in f.read().splitlines():
            data = line.split('|')
            target_entities[data[0]].append(data[0])
            if len(data) == 2:
                [target_entities[data[0]].append(e) for e in data[1].split(',')]    
    return target_entities

def key_import(gpg_private=None, gpg_dir='gnupg-dir'):
    if gpg_private is not None:
        if not os.path.exists(gpg_dir):
            os.makedirs(gpg_dir)
        gpg_child = subprocess.Popen(
            ['/usr/bin/gpg', '--no-permission-warning', '--homedir', gpg_dir,
             '--import', gpg_private],
            stderr=subprocess.PIPE)
        gpg_child.communicate()
        
def decrypt_and_uncompress(data, gpg_dir='gnupg-dir'):
    gpg_child = subprocess.Popen(
        ['/usr/bin/gpg',   '--no-permission-warning', '--homedir', gpg_dir,
         '--trust-model', 'always', '--output', '-', '--decrypt', '-'],
        stdin =subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    data, _ = gpg_child.communicate(data)

    xz_child = subprocess.Popen(
        ['/usr/bin/xz', '--decompress'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    data, errors = xz_child.communicate(data)
    assert not errors, errors
    return data

def get_stream_items(thrift_data):
    transport = StringIO(thrift_data)        
    transport.seek(0)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    while 1:
        try:
            doc = StreamItem()
            doc.read(protocol)
            yield doc
        except EOFError:
            break
        except:
            log_err("unexpected exception %s" % traceback.format_exc())
            pass

def mapper(argv):
    key_import('trec-kba-rsa.txt')
    target_entities = read_entities('entities.txt')
    for filename in sys.stdin:
        file_url = PATH + filename
        try:
            data = urllib.urlopen(file_url.strip()).read()
            thrift_data = decrypt_and_uncompress(data)
            for stream_item in get_stream_items(thrift_data):
                has_match = False
                if stream_item.body.clean_visible:
                    scv = stream_item.body.clean_visible.strip().lower()
                    for key in target_entities:
                        for target_value in target_entities[key]:
                            if scv.find(target_value) != -1:
                                has_match = True
                                print '%s\t%s' % (key, filename)
                                break
                if has_match:
                    break    
        except:
            log_err("file: %s" % filename)
            log_err(traceback.format_exc())
            
if __name__ == '__main__':
    mapper(sys.argv)
