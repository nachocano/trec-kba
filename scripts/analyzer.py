import re
import argparse
from collections import defaultdict
import zipimport
import os
from cStringIO import StringIO
import numpy as np

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
  parser.add_argument('-t', '--test_file', required=True)
  parser.add_argument('-r', '--run_file', required=True)
  parser.add_argument('-d', '--distances_file', required=True)
  args = parser.parse_args()

  run = defaultdict(defaultdict)
  with open(args.run_file) as f:
    for line in f.read().splitlines():
      l = line.strip()
      if l.startswith('#'):
          continue
      l = l.split('\t')
      streamid = l[2]
      targetid = l[3]
      relevance = l[5]
      date_hour = l[7]
      run[targetid][(streamid, date_hour)] = int(relevance)

  truth = defaultdict(defaultdict)
  with open(args.test_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      relevance = l[3]
      truth[targetid][(streamid, date_hour)] = int(relevance)

  assert len(truth) == len(run)

  distances = defaultdict(defaultdict)
  with open(args.distances_file) as f:
    for line in f.read().splitlines():
      l = line.strip().split()
      streamid = l[0]
      targetid = l[1]
      date_hour = l[2]
      distance = float(l[3])
      distances[targetid][(streamid, date_hour)] = distance

  useful = []
  vital = []
  for targetid in run:
    #if "Shawn" not in targetid:
    #  continue
    for streamid, date_hour in distances[targetid]:
      truth_relevance = truth[targetid][(streamid, date_hour)]
      run_relevance = run[targetid][(streamid, date_hour)]
      distance = distances[targetid][(streamid, date_hour)]
      if truth_relevance == -1 or truth_relevance == 0:
        continue
      if run_relevance == 1:
        useful.append(distance)
      if run_relevance == 2:
        vital.append(distance)

  print 'mean vital %s' % np.mean(vital)
  print 'median vital %s' % np.median(vital)
  print 'max vital %s' % np.max(vital)
  print 'mean useful %s' % np.mean(useful)
  print 'median useful %s' % np.median(useful)
  print 'max useful %s' % np.max(useful)

'''
  corrects = defaultdict(int)
  wrongs = defaultdict(int)
  for targetid in run:
    for streamid, date_hour in distances[targetid]:
      truth_relevance = truth[targetid][(streamid, date_hour)]
      run_relevance = run[targetid][(streamid, date_hour)]
      distance = distances[targetid][(streamid, date_hour)]
      if truth_relevance == -1 or truth_relevance == 0:
        continue
      if (truth_relevance != run_relevance):
          wrongs[targetid] += 1
      else:
          corrects[targetid] += 1

  for key, value in sorted(corrects.iteritems(), key=lambda (k,v) : (v,k)):
    print key, value
'''


  #for key, value in sorted(wrongs.iteritems(), key=lambda (k,v) : (v,k)):
  #  print key, value


  #wrong_hist, wrong_bin_edges = np.histogram(wrong_distances)
  #print wrong_hist
  #print wrong_bin_edges

  #correct_hist, correct_bin_edges = np.histogram(correct_distances)
  #print correct_hist
  #print correct_bin_edges

  #print max(correct_distances)
  #print min(correct_distances)
  #print max(wrong_distances)
  #print min(wrong_distances)
  #correct_distances.sort()
  #wrong_distances.sort()


'''
  for targetid in wrong_predictions:
    print 'processing targetid %s' % targetid
    filename = '%s.bin' % targetid[targetid.rfind('/')+1:]
    filepath = os.path.join(args.input_dir, filename)
    if not os.path.isfile(filepath):
      print 'missing file %s. continue with next one' % filepath
      continue
    with open(filepath, 'r') as f:
      thrift_data = f.read()
      for streamid, date_hour in truth[targetid]:
        truth_relevance = truth[targetid][(streamid, date_hour)]
        run_relevance = run[targetid][(streamid, date_hour)]
        for stream_item in get_stream_items(thrift_data):
          if stream_item.stream_id in wrong_predictions[targetid]:
            print stream_item.body.clean_visible
'''       

if __name__ == '__main__':
  main()

