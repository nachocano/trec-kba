import gensim, bz2
import argparse
import time
import sys

def log(msg):
  sys.stdout.write('%s\n' % msg)
  sys.stdout.flush()


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-d', '--dictionary_file', required=True)
  parser.add_argument('-tr', '--train_bow_file', required=True)
  parser.add_argument('-te', '--test_bow_file', required=True)
  parser.add_argument('-otr', '--train_tfidf', required=True)
  parser.add_argument('-ote', '--test_tfidf', required=True)
  parser.add_argument('-c', '--corpus_file', required=True)
  parser.add_argument('-m', '--model_output', required=True)
  args = parser.parse_args()

  id2word = gensim.corpora.Dictionary.load_from_text(args.dictionary_file)
  corpus_bow = gensim.corpora.MmCorpus(args.corpus_file)
  log('loading model')
  start = time.time()
  model = gensim.models.tfidfmodel.TfidfModel(corpus=corpus_bow, id2word=id2word)
  elapsed = time.time() - start
  log('saving model, load took %s' % elapsed)
  model.save(args.model_output)
  log('to tfidf')
  to_tfidf(args.train_bow_file, args.train_tfidf, model)
  to_tfidf(args.test_bow_file, args.test_tfidf, model)
  

def to_tfidf(input_file, output_file, tfidf):
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
      tfidf_doc = tfidf[doc]
      new_vec = ['%s,%s' % (fid,value) for (fid, value) in tfidf_doc]
      new_vec = ' '.join(new_vec)
      out.write('%s %s\n' % (fixed, new_vec))
    i+=1
    print i
  out.close()

if __name__ == '__main__':
  main()

