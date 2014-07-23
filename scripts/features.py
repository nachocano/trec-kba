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
import time
from math import log, ceil
from cStringIO import StringIO
from collections import defaultdict
from collections import Counter


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

source_map = {'arxiv': 0, 'classified': 1, 'forum': 2, 'linking': 3, 'mainstream_news': 4, 'memetracker': 5, 'news': 6, 'review': 7, 'social': 8, 'weblog': 9}

def get_sources(source):
  sources = [0] * 10
  sources[source_map[source.lower()]] = 1
  return sources

strip_punctuation = dict((ord(char), u" ") for char in string.punctuation)
white_space_re = re.compile("(\s|\n|\r)+")

def strip_string(s):
  return white_space_re.sub(" ", s.translate(strip_punctuation).lower())

# ugly stuff
def get_full_pattern(data):
  data_splitted = data.split()
  if len(data_splitted) > 1:
    result = '\\b' + data_splitted[0].strip()
    for i in xrange(1,len(data_splitted)):
      result += '\\s+' + data_splitted[i].strip()
    result += '\\b'
    return result
  else:
    return '\\b' + data.strip() + '\\b'

def get_partial_pattern(data):
  result = '\\b' + data[0].strip() + '\\b'
  for i in xrange(1,len(data)):
    result += '|\\b' + data[i].strip() + '\\b'
  return result



def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--input_dir', required=True)
  parser.add_argument('-t', '--truth_file', required=True)
  parser.add_argument('-e', '--entities_file', required=True)
  parser.add_argument('-fe', '--full_entities_file', required=True)
  parser.add_argument('-sp', '--split_percentage', required=True, type=float)
  parser.add_argument('-o', '--output_dir', required=True)
  args = parser.parse_args()

  truth_counts = defaultdict(list)
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    relevance = instance[5]
    key = (streamid, targetid)
    truth_counts[key].append(relevance)

  majority_relevance = {}
  for key in truth_counts:
    counter = Counter(truth_counts[key])
    majority_relevance[key] = counter.most_common()[0][0]

  # truth data file, keeping the truth relevance as the majority element or the minimum one, in case of match
  truth = {}
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    date = instance[7]
    key = (streamid, targetid)
    truth[key] = (majority_relevance[key], date)

  # target entities
  targetids = []
  for line in open(args.entities_file).read().splitlines():
    targetids.append(line.strip())

  # target entities, with surface form names, to compute features
  target_full_str_entities = defaultdict(list)
  target_partial_str_entities = defaultdict(list)
  target_full_regex_entities = {}
  target_partial_regex_entities = {}
  for line in open(args.full_entities_file).read().splitlines():
    data = line.split('|')
    for e in data[1].split(','):
      full = get_full_pattern(e)
      target_full_str_entities[data[0]].append(full)
      s = e.split()
      if len(s) > 1:
        partial = get_partial_pattern(s)
        target_partial_str_entities[data[0]].append(partial)
  for target in target_full_str_entities:
    full_as_string = "|".join(target_full_str_entities[target])
    target_full_regex_entities[target] = re.compile(full_as_string)
  for target in target_partial_str_entities:
    partial_as_string = "|".join(target_partial_str_entities[target])
    target_partial_regex_entities[target] = re.compile(partial_as_string)

  train_out = open(os.path.join(args.output_dir, "train.tsv"), 'w')
  test_out = open(os.path.join(args.output_dir, "test.tsv"), 'w')
  total_ids = len(targetids)
  total_time = 0
  for targetid in targetids:
    total_ids -=1
    start = time.time()
    print 'processing targetid %s. remaining %d' % (targetid, total_ids)
    info = defaultdict(dict)
    filename = '%s.bin' % targetid[targetid.rfind('/')+1:]
    filepath = os.path.join(args.input_dir, filename)
    if not os.path.isfile(filepath):
      print 'missing file %s. continue with next one' % filepath
      continue
    count = 0
    with open(filepath) as f:
      thrift_data = f.read()
      for stream_item in get_stream_items(thrift_data):
        key = (stream_item.stream_id, targetid)
        if truth.has_key(key):
          relevance, date_hour = truth[key]

          clean_visible = stream_item.body.clean_visible.lower()

          # doc features
          doc_length = len(clean_visible)
          log_doc_length = log(doc_length)
          sources = get_sources(stream_item.source)
          
          # doc-entity features
          results_full = list(target_full_regex_entities[targetid].finditer(clean_visible))
          ocurrences_full = len(results_full)
          first_pos_full = -1
          first_pos_norm_full = -1
          last_pos_full = -1
          last_pos_norm_full = -1
          spread_full = -1
          spread_norm_full = -1
          if ocurrences_full > 0:
            first_pos_full = results_full[0].start()
            first_pos_norm_full = first_pos_full / doc_length
            last_pos_full = results_full[ocurrences_full-1].start()
            last_pos_norm_full = last_pos_full / doc_length
            spread_full = last_pos_full - first_pos_full
            spread_norm_full = spread_full / doc_length

          # partial stuff
          first_pos_partial = -1
          first_pos_norm_partial = -1
          last_pos_partial = -1
          last_pos_norm_partial = -1
          spread_partial = -1
          spread_norm_partial = -1
          if target_partial_regex_entities.has_key(targetid):
            results_partial = list(target_partial_regex_entities[targetid].finditer(clean_visible))
            ocurrences_partial = len(results_partial)
            if ocurrences_partial > 0:
              first_pos_partial = results_partial[0].start()
              first_pos_norm_partial = first_pos_partial / doc_length
              last_pos_partial = results_partial[ocurrences_partial-1].start()
              last_pos_norm_partial = last_pos_partial / doc_length
              spread_partial = last_pos_partial - first_pos_partial
              spread_norm_partial = spread_partial / doc_length

          # TODO add serif features
          #for sentence in stream_item.body.sentences['serif']:
          #for token in sentence.tokens:
          #print sentence


          count += 1

          newkey = (stream_item.stream_id, targetid, date_hour)
          info[newkey]['features'] = []
          info[newkey]['features'].append(sources)
          info[newkey]['features'].append(log_doc_length)

          info[newkey]['features'].append(ocurrences_full)
          info[newkey]['features'].append(first_pos_full)
          info[newkey]['features'].append(first_pos_norm_full)
          info[newkey]['features'].append(last_pos_full)
          info[newkey]['features'].append(last_pos_norm_full)
          info[newkey]['features'].append(spread_full)
          info[newkey]['features'].append(spread_norm_full)

          info[newkey]['features'].append(ocurrences_partial)
          info[newkey]['features'].append(first_pos_partial)
          info[newkey]['features'].append(first_pos_norm_partial)
          info[newkey]['features'].append(last_pos_partial)
          info[newkey]['features'].append(last_pos_norm_partial)
          info[newkey]['features'].append(spread_partial)
          info[newkey]['features'].append(spread_norm_partial)

          info[newkey]['label'] = relevance

    left = int(args.split_percentage * count)
    for key, value in sorted(info.iteritems(), key=lambda (k,v) : (k[2],v)):
      sources = ' '.join(str(s) for s in value['features'][0])
      rest = ' '.join(str(f) for f in value['features'][1:15])
      label = value['label']
      if left:
        train_out.write('%s %s %s %s %s %s\n' % (key[0], key[1], key[2], label, sources, rest))
        left -= 1
      else:
        test_out.write('%s %s %s %s %s %s\n' % (key[0], key[1], key[2], label, sources, rest))

    elapsed = time.time() - start
    print 'finished processing targetid %s, elapsed time %s' % (targetid, elapsed)
    total_time += elapsed
  print 'total time %s' % total_time


if __name__ == '__main__':
  main()

