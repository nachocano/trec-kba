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

def main():
  parser = argparse.ArgumentParser(description='TODO')
  parser.add_argument('-d', '--directory', required=True)
  parser.add_argument('-t', '--truth_file', required=True)
  parser.add_argument('-m', '--mapping_file', required=True)
  parser.add_argument('-k', '--treckba_key_file', required=True)
  parser.add_argument('-e', '--entities_file', required=True)
  parser.add_argument('-o', '--output_dir', required=True)
  args = parser.parse_args()
  key_import(args.treckba_key_file, args.directory)
  
  # read truth data file
  truth = defaultdict(set)
  for line in open(args.truth_file).read().splitlines():
    instance = line.split()
    streamid = instance[2]
    targetid = instance[3]
    truth[targetid].add(streamid)

  # target entities
  targetids = []
  for line in open(args.entities_file).read().splitlines():
    targetids.append(line.strip())
  targetids = [targetids[0]]

  # streamid - filename mapping
  mappings = defaultdict(set)
  for line in open(args.mapping_file).read().splitlines():
    streamid, filename = line.split()
    filepath = '%s/%s' % (args.directory, filename.split('/')[1])
    mappings[streamid].add(filepath)

  for targetid in targetids:
    start_time = time.time()
    sys.stdout.write('processing targetid %s\n' % (targetid))
    sys.stdout.flush()
    if truth.has_key(targetid):
      matched_item = False
      transport = StringIO()
      protocol = TBinaryProtocol.TBinaryProtocol(transport)
      for streamid in truth[targetid]:
        if mappings.has_key(streamid):
          filenames = mappings[streamid]
          for filename in filenames:
            with open(filename) as f:
              data = f.read()
              thrift_data = decrypt_and_uncompress(data, args.directory)
              for stream_item in get_stream_items(thrift_data):
                if stream_item.stream_id == streamid:
                  sys.stdout.write('matched streamid %s for targetid %s\n' % (streamid, targetid))
                  sys.stdout.flush()
                  matched_item = True
                  stream_item.write(protocol)
                  break
        else:
          sys.stdout.write('streamid %s does not exist in mapping file\n' % streamid)
          sys.stdout.flush()
      if matched_item:
        transport.seek(0)
        thrift_data = transport.getvalue()
        ofname = '%s.bin' % targetid[targetid.rfind('/')+1:]
        ofpath = os.path.join(args.output_dir, ofname)
        tmp_ofpath = ofpath + '.partial'
        fh = open(tmp_ofpath, 'wb')
        fh.write(thrift_data)
        fh.close()
        os.rename(tmp_ofpath, ofpath)
    else:
      sys.stdout.write('targetid %s does not exist in truth data\n' % targetid)
      sys.stdout.flush()
    elapsed = time.time() - start_time
    sys.stdout.write('targetid:%s processed in %s\n' % (targetid, elapsed))
    sys.stdout.flush()

if __name__ == '__main__':
  main()

