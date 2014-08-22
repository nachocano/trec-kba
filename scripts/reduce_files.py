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
import time


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
  parser.add_argument('-i', '--input_dir', required=True)
  parser.add_argument('-o', '--output_dir', required=True)
  parser.add_argument('-e', '--entities_ccr', required=True)
  args = parser.parse_args()
  

  targetids = []
  for line in open(args.entities_ccr).read().splitlines():
    targetids.append(line.strip())

  duplicates = 0
  for targetid in targetids:
    print 'processing %s' % targetid
    transport = StringIO()
    streamitems_per_targetid = {}
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    filename = '%s.bin' % targetid[targetid.rfind('/')+1:]
    filepath = os.path.join(args.input_dir, filename)
    if not os.path.isfile(filepath):
      print 'missing file %s. continue with next one' % filepath
      continue
    with open(filepath) as f:
      data = f.read()
      stream_items = get_stream_items(data)
      for stream_item in stream_items:
        if streamitems_per_targetid.has_key(stream_item.stream_id):
          print 'duplicate %s' % stream_item.stream_id
          duplicates += 1
          continue
        else:
          stream_item.write(protocol)
          streamitems_per_targetid[stream_item.stream_id] = True

    transport.seek(0)
    thrift_data = transport.getvalue()
    ofpath = os.path.join(args.output_dir, filename)
    tmp_ofpath = ofpath + '.partial'
    fh = open(tmp_ofpath, 'wb')
    fh.write(thrift_data)
    fh.close()
    os.rename(tmp_ofpath, ofpath)  
    
  print 'duplicates removed %s' % duplicates

if __name__ == '__main__':
  main()

