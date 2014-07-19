#!/usr/bin/python
import os
import sys
import subprocess
import traceback
import zipimport
import re
import argparse
import fileinput
import string
from math import log
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

def key_import(gpg_private=None, gpg_dir='gnupg-dir'):
    if gpg_private is not None:
        if not os.path.exists(gpg_dir):
            os.makedirs(gpg_dir)
        gpg_child = subprocess.Popen(
            ['/usr/local/bin/gpg', '--no-permission-warning', '--homedir', gpg_dir,
             '--import', gpg_private],
            stderr=subprocess.PIPE)
        gpg_child.communicate()
        
def decrypt_and_uncompress(data, gpg_dir='gnupg-dir'):
    gpg_child = subprocess.Popen(
        ['/usr/local/bin/gpg',   '--no-permission-warning', '--homedir', gpg_dir,
         '--trust-model', 'always', '--output', '-', '--decrypt', '-'],
        stdin =subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    data, _ = gpg_child.communicate(data)

    xz_child = subprocess.Popen(
        ['/usr/local/bin/xz', '--decompress'],
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
            pass

source_map = defaultdict(int)
source_map['arxiv'] = 1
source_map['classified'] = 2
source_map['forum'] = 3
source_map['linking'] = 4
source_map['mainstream_news'] = 5
source_map['memetracker'] = 6
source_map['news'] = 7
source_map['review'] = 8
source_map['social'] = 9
source_map['weblog'] = 10

def get_source(source):
  return source_map[source.lower()]

strip_punctuation = dict((ord(char), u" ") for char in string.punctuation)
white_space_re = re.compile("(\s|\n|\r)+")

def strip_string(s):
  return white_space_re.sub(" ", s.translate(strip_punctuation).lower())

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-d', '--directory', required=True)
  parser.add_argument('-t', '--truth_file', required=True)
  parser.add_argument('-m', '--mapping_file', required=True)
  parser.add_argument('-k', '--treckba_key_file', required=True)
  args = parser.parse_args()
  key_import(args.treckba_key_file, args.directory)
  truth = {}
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    annotator = instance[1]
    streamid = instance[2]
    targetid = instance[3]
    relevance = instance[5]
    offsets = instance[10]
    truth[(streamid, targetid, offsets, annotator)] = relevance

  mappings = defaultdict(set)
  for line in open(args.mapping_file).read().splitlines():
    streamid, filename = line.split()
    filename = '%s/%s' % (args.directory, filename.split('/')[1])
    mappings[streamid].add(filename)

  for (streamid, targetid, offsets, _), label in truth.iteritems():
    assert mappings.has_key(streamid)
    filenames = mappings[streamid]
    for filename in filenames:
      if "news-9-53162abdb5a96e7b4df6be63293b9381-95e71c51e81de0a369716b1832728004-7fb816409c5925f7ad125c72a17a70da-7385982fc6e63052fba2d32eeec244c5.sc.xz.gpg" in filename:
        data = open(filename).read()
        thrift_data = decrypt_and_uncompress(data, args.directory)
        for stream_item in get_stream_items(thrift_data):
          if stream_item.stream_id == streamid:
            text = strip_string(stream_item.body.clean_visible.decode('utf8'))
            # doc features
            doc_length = log(len(text))
            source = get_source(stream_item.source)
            
            # doc-entity features

            for sentence in stream_item.body.sentences['serif']:
              print sentence


            print doc_length, source

if __name__ == '__main__':
  main()

