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
  parser.add_argument('-c', '--corpus_file', required=True)
  parser.add_argument('-o', '--output_file', required=True)
  parser.add_argument('-m', '--model', required=True)
  args = parser.parse_args()
  model = args.model
  assert model == 'lsi' or model == 'lda' or model == 'tfidf'

  begin = time.time()
  
  log('computing dictionary')
  id2word = gensim.corpora.Dictionary.load_from_text(args.dictionary_file)
  elapsed = time.time() - begin
  log('dictionary computed in %s' % elapsed)
  
  start = time.time()
  log('computing mm corpus')
  mm = gensim.corpora.MmCorpus(args.corpus_file)
  #mm = gensim.corpora.MmCorpus(bz2.BZ2File(args.corpus_file))
  elapsed = time.time() - start
  log('mm corpus computed in %s' % elapsed)

  m = None
  start = time.time()
  log('computing %s' % model)
  if model == 'lsi':
    m = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=300)
  elif model == 'lda':
    m = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=300)
  elif model == 'tfidf':
    # maybe not needed
    m = gensim.models.tfidfmodel.TfidfModel(corpus=mm)
  else: 
    log('none')

  elapsed = time.time() - start
  log('%s computed in %s' % (model, elapsed))
  
  start = time.time()
  log('saving %s' % model)
  m.save(args.output_file)
  elapsed = time.time() - start
  log('%s saved in %s' % (model, elapsed))

if __name__ == '__main__':
  main()
