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
  parser.add_argument('-d', '--input_dir', required=True)
  parser.add_argument('-t', '--truth_file', required=True)
  parser.add_argument('-e', '--entities_file', required=True)
  parser.add_argument('-fe', '--full_entities_file', required=True)
  args = parser.parse_args()

  # truth data file
  truth = {}
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    relevance = instance[5]
    date = instance[7]
    # the entry may be repeated, keep the one with highest relevance
    key = (streamid, targetid)
    if truth.has_key(key):
      if truth[key][0] < relevance:
        truth[key] = (relevance, date)
    else:
        truth[key] = (relevance, date)

  # target entities
  targetids = []
  for line in open(args.entities_file).read().splitlines():
    targetids.append(line.strip())

  # full target entities, with surface form names, to compute features
  target_entities = defaultdict(list)
  target_regex_entities = {}
  for line in open(args.full_entities_file).read().splitlines():
    data = line.split('|')
    [target_entities[data[0]].append(get_pattern(e)) for e in data[1].split(',')]
    target_regex_entities = {}
    for target in target_entities:
      as_string = "|".join(target_entities[target])
      target_regex_entities[target] = re.compile(as_string)

  assert(len(target_regex_entities) == len(targetids))

  targetids = [targetids[0]]
  for targetid in targetids:
    filename = '%s.bin' % targetid[targetid.rfind('/')+1:]
    filepath = os.path.join(args.input_dir, filename)
    with open(filepath) as f:
      thrift_data = f.read()
      for stream_item in get_stream_items(thrift_data):
        print stream_item
        #clean_visible = stream_item.body.clean_visible
        #print clean_visible
        # doc features
        #doc_length = len(text)
        #log_doc_length = log(doc_length)
        #source = get_source(stream_item.source)
        
        # doc-entity features
        #results = list(target_regex_entities[targetid].finditer(text))
        #ocurrences = len(results)
        #if ocurrences > 0:
        #  has_match = True
        #  first_pos = results[0].start()
        #  first_pos_norm = first_pos / doc_length
        #  last_pos = results[ocurrences-1].start()
        #  last_pos_norm = last_pos / doc_length
        #  spread = last_pos - first_pos
        #  spread_norm = spread / doc_length




          #if stream_item.stream_id == streamid:
            
            #text = strip_string(clean_visible.decode('utf8'))

              #for sentence in stream_item.body.sentences['serif']:
              #for token in sentence.tokens:
              #print sentence
              #sys.stdout.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (label, log_doc_length, source, ocurrences, first_pos, first_pos_norm, last_pos, last_pos_norm, spread, spread_norm, annotator, streamid, targetid))
        #if has_match:
        #  break


if __name__ == '__main__':
  main()

