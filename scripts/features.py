#!/usr/bin/python
from __future__ import division
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


def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-d', '--directory', required=True)
  parser.add_argument('-t', '--truth_file', required=True)
  parser.add_argument('-m', '--mapping_file', required=True)
  parser.add_argument('-k', '--treckba_key_file', required=True)
  parser.add_argument('-e', '--entities_file', required=True)
  args = parser.parse_args()
  key_import(args.treckba_key_file, args.directory)
  
  # read truth data file
  truth = {}
  position = 1
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    annotator = instance[1]
    streamid = instance[2]
    targetid = instance[3]
    relevance = instance[5]
    offsets = instance[10]
    truth[(streamid, targetid, offsets, annotator)] = (relevance, position) 

  # patterns to compute features
  target_entities = defaultdict(list)
  target_regex_entities = {}
  for line in open(args.entities_file).read().splitlines():
    data = line.split('|')
    [target_entities[data[0]].append(get_pattern(e)) for e in data[1].split(',')]
    target_regex_entities = {}
    for target in target_entities:
      as_string = "|".join(target_entities[target])
      target_regex_entities[target] = re.compile(as_string)

  # streamid - filename mapping
  mappings = defaultdict(set)
  for line in open(args.mapping_file).read().splitlines():
    streamid, filename = line.split()
    filename = '%s/%s' % (args.directory, filename.split('/')[1])
    mappings[streamid].add(filename)

  for (streamid, targetid, offsets, annotator), (label, _) in sorted(truth.iteritems(), key=lambda (k,v) : (v[1],k)):
    assert mappings.has_key(streamid)
    filenames = mappings[streamid]
    has_match = False
    for filename in filenames:
      with open(filename) as f:
        data = f.read()
        thrift_data = decrypt_and_uncompress(data, args.directory)
        for stream_item in get_stream_items(thrift_data):
          if stream_item.stream_id == streamid:
            clean_visible = stream_item.body.clean_visible
            text = strip_string(clean_visible.decode('utf8'))

            # doc features
            doc_length = len(text)
            log_doc_length = log(doc_length)
            source = get_source(stream_item.source)
            
            # doc-entity features
            results = list(target_regex_entities[targetid].finditer(text))
            ocurrences = len(results)
            if ocurrences > 0:
              has_match = True
              first_pos = results[0].start()
              first_pos_norm = first_pos / doc_length
              last_pos = results[ocurrences-1].start()
              last_pos_norm = last_pos / doc_length
              spread = last_pos - first_pos
              spread_norm = spread / doc_length
              #for sentence in stream_item.body.sentences['serif']:
              #for token in sentence.tokens:
              #print sentence
              sys.stdout.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (label, log_doc_length, source, ocurrences, first_pos, first_pos_norm, last_pos, last_pos_norm, spread, spread_norm, annotator, streamid, targetid))
        if has_match:
          break
    if not has_match:
      sys.stdout.write('no_match=%s\t%s\t%s\t%s\n' % (annotator, streamid, targetid, str(filenames)))

if __name__ == '__main__':
  main()

