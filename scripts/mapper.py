#!/usr/bin/python
import os
import sys
import subprocess
import urllib
import traceback
import zipimport
import re
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

def log_err(msg):
    sys.stderr.write('%s\n' % msg)
    sys.stderr.flush()

def report_status(msg):
    sys.stderr.write('reporter:status:%s\n' % msg)
    sys.stderr.flush()

def report_counter(group, counter, amount):
    sys.stderr.write('reporter:counter:%s,%s,%s\n' % (group, counter, amount))
    sys.stderr.flush()

def log(msg):
    sys.stdout.write('%s\n' % msg)
    sys.stdout.flush()

def get_pattern(data):
  data_splitted = data.split()
  if len(data_splitted) > 1:
    result = '\\b' + data_splitted[0].strip()
    for i in xrange(1,len(data_splitted)):
      result += '\\s+' + data_splitted[i].strip()
    result += '\\b'
    return result
  else:
    return '\\b' + data.strip() + '\\b'

def read_entities(filename):
  target_entities = defaultdict(list)
  with open(filename,'r') as f:
    for line in f.read().splitlines():
      data = line.split('|')
      [target_entities[data[0]].append(get_pattern(e)) for e in data[1].split(',')]
    target_regex_entities = {}
    for target in target_entities:
      as_string = "|".join(target_entities[target])
      target_regex_entities[target] = re.compile(as_string)
    return target_regex_entities

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
    if errors:
        log_err('err %s' % errors)
        return None
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
            #log_err("err: %s" % traceback.format_exc())
            pass

#folder_regex = re.compile(r'/(20\d{2}-\d{2}-\d{2}-\d{2})/')

def mapper(argv):
    key_import('trec-kba-rsa.txt')
    report_status('key imported')
    target_regex_entities = read_entities('entities.txt')
    report_status('regex computed')
    files_processed = 0
    matches = 0
    for file_url in sys.stdin:
        files_processed += 1
        report_counter('Files', 'PROCESSED', files_processed)
        try:
            report_status('downloading %s' % file_url)
            data = urllib.urlopen(file_url.strip()).read()
            report_status('decrypt and uncompressing %s' % file_url)
            thrift_data = decrypt_and_uncompress(data)
            if not thrift_data:
                report_status('invalid thrift data %s, continue' % file_url)
                continue
            for stream_item in get_stream_items(thrift_data):
                report_status('looking at %s' % stream_item.stream_id)
                if stream_item.body.clean_visible:
                    scv = stream_item.body.clean_visible.strip().lower()
                    for key in target_regex_entities:
                        match = target_regex_entities[key].search(scv)
                        if match:
                            matches += 1
                            report_counter('Files', 'MATCHES', matches)
                            log('%s\t%s\t%s' % (stream_item.stream_id, key, file_url))
        except:
            log_err("err: %s, %s" % (file_url, traceback.format_exc()))
            
if __name__ == '__main__':
    mapper(sys.argv)
