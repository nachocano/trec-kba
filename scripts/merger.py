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

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-f', '--first_dir', required=True)
  parser.add_argument('-s', '--second_dir', required=True)
  parser.add_argument('-o', '--output_dir', required=True)
  parser.add_argument('-e', '--entities_to_merge', required=True)
  args = parser.parse_args()

  # target entities
  targetids = []
  for line in open(args.entities_to_merge).read().splitlines():
    targetids.append(line.strip())

  total_ids = len(targetids)
  total_time = 0
  for targetid in targetids:
    total_ids -=1
    start = time.time()
    print 'processing targetid %s. remaining %d' % (targetid, total_ids)
    filename = '%s.bin' % targetid[targetid.rfind('/')+1:]
    filepath1 = os.path.join(args.first_dir, filename)
    if not os.path.isfile(filepath1):
      print 'missing file %s. continue with next one' % filepath1
      continue
    filepath2 = os.path.join(args.second_dir, filename)
    if not os.path.isfile(filepath2):
      print 'missing file %s. continue with next one' % filepath2
      continue

    transport = StringIO()
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    targetid_streamids = {}
    items = 0
    with open(filepath1) as f:
      thrift_data = f.read()
      for stream_item in get_stream_items(thrift_data):
        if targetid_streamids.has_key(stream_item.stream_id):
          print 'duplicate %s for targetid %s' % (stream_item.stream_id, targetid)
          continue
        stream_item.write(protocol)
        targetid_streamids[stream_item.stream_id] = True
        items += 1
      print 'items from first file %d' % items

    with open(filepath2) as f:
      thrift_data = f.read()
      for stream_item in get_stream_items(thrift_data):
        if targetid_streamids.has_key(stream_item.stream_id):
          print 'duplicate %s for targetid %s' % (stream_item.stream_id, targetid)
          continue
        stream_item.write(protocol)
        targetid_streamids[stream_item.stream_id] = True
        items += 1
      print 'total items %d' % items
     
    transport.seek(0)
    thrift_data = transport.getvalue()
    ofname = '%s.bin' % targetid[targetid.rfind('/')+1:]
    ofpath = os.path.join(args.output_dir, ofname)
    tmp_ofpath = ofpath + '.partial'
    fh = open(tmp_ofpath, 'wb')
    fh.write(thrift_data)
    fh.close()
    os.rename(tmp_ofpath, ofpath)
    
    elapsed = time.time() - start
    print 'finished processing targetid %s, elapsed time %s' % (targetid, elapsed)
    total_time += elapsed
  
  print 'total time %s' % total_time


if __name__ == '__main__':
  main()

