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
    if errors:
      print 'errors %s' % errors
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
            pass

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-i', '--input_dir', required=True)
  parser.add_argument('-o', '--output_dir', required=True)
  parser.add_argument('-tc', '--to_complete_file', required=True)
  parser.add_argument('-k', '--treckba_key_file', required=True)
  args = parser.parse_args()

  key_import(args.treckba_key_file, args.input_dir)
  
  
  targetids = set()
  filenames = defaultdict(list)
  for line in open(args.to_complete_file).read().splitlines():
    streamid, targetid, fileurl = line.split()
    filename = fileurl[fileurl.rfind('/')+1:]
    targetids.add(targetid)
    filenames[filename].append((streamid, targetid))

  
  transports = {}
  protocols = {}
  for targetid in targetids:
    transports[targetid] = StringIO()
    protocols[targetid] = TBinaryProtocol.TBinaryProtocol(transports[targetid])
  
  left = len(filenames)
  for filename in filenames:
    values = filenames[filename]
    left -= 1
    print 'processing %s. %d remaining' % (filename, left)
    path = os.path.join(args.input_dir, filename)
    if not os.path.isfile(path):
      print 'not a valid path %s' % path
      continue
    with open(path) as f:
      data = f.read()
      thrift_data = decrypt_and_uncompress(data, args.input_dir)
      if not thrift_data:
        print 'cannot decrypt and uncompress %s' % filename
        continue
      has_matched = False
      for stream_item in get_stream_items(thrift_data):
        for streamid, targetid in values:
          if stream_item.stream_id == streamid:
            print 'matched streamitem %s for targetid %s' % (streamid, targetid) 
            stream_item.write(protocols[targetid])
            has_matched = True
        if has_matched:
          break

  for targetid in targetids:
    transports[targetid].seek(0)
    thrift_data = transports[targetid].getvalue()
    ofname = '%s.bin' % targetid[targetid.rfind('/')+1:]
    ofpath = os.path.join(args.output_dir, ofname)
    tmp_ofpath = ofpath + '.partial'
    fh = open(tmp_ofpath, 'wb')
    fh.write(thrift_data)
    fh.close()
    os.rename(tmp_ofpath, ofpath)
    transports[targetid].close()

if __name__ == '__main__':
  main()

