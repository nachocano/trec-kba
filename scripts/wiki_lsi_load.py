import gensim, bz2
import argparse
import time
import sys

def log(msg):
  sys.stdout.write('%s\n' % msg)
  sys.stdout.flush()


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-tr', '--train_tfidf_file', required=True)
  parser.add_argument('-te', '--test_tfidf_file', required=True)
  parser.add_argument('-otr', '--train_lsi', required=True)
  parser.add_argument('-ote', '--test_lsi', required=True)
  parser.add_argument('-m', '--model', required=True)
  args = parser.parse_args()

  log('loading model')
  start = time.time()
  model = gensim.models.lsimodel.LsiModel()
  model.load(args.model)
  elapsed = time.time() - start
  log('model loaded took %s' % elapsed)
  log('to lsi')
  to_lsi(args.train_bow_file, args.train_tfidf, model)
  to_lsi(args.test_bow_file, args.test_tfidf, model)
  

def to_tfidf(input_file, output_file, model):
  i = 0 
  out = open(output_file, 'w')
  for line in open(input_file).read().splitlines():
    tokens = line.split()
    fixed = ' '.join(tokens[:29])
    bows = tokens[29:]
    doc = []
    for bow in bows:
      w, wc = bow.split(',')
      tup = (int(w), float(wc))
      doc.append(tup)      
    if len(doc) == 0:
      out.write('%s\n' % fixed)
    else:
      lsi_doc = model[doc]
      new_vec = ['%s,%s' % (fid,value) for (fid, value) in lsi_doc]
      new_vec = ' '.join(new_vec)
      out.write('%s %s\n' % (fixed, new_vec))
    i+=1
    print i
  out.close()

if __name__ == '__main__':
  main()

