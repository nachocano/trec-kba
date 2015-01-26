import gensim
import argparse
import time
import sys

def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-d', '--dictionary_file', required=True)
  parser.add_argument('-tr', '--train_plain_file', required=True)
  parser.add_argument('-te', '--test_plain_file', required=True)
  parser.add_argument('-otr', '--train_bow', required=True)
  parser.add_argument('-ote', '--test_bow', required=True)
  args = parser.parse_args()

  dictionary = gensim.corpora.Dictionary.load_from_text(args.dictionary_file)

  to_bow(args.train_plain_file, args.train_bow, dictionary)
  to_bow(args.test_plain_file, args.test_bow, dictionary)

def to_bow(input_file, output_file, dictionary):
  out = open(output_file, 'w')
  for line in open(input_file).read().splitlines():
    delimiter = line.find('[')
    fixed = line[:delimiter-1]
    arrays = line[delimiter:]
    lemmas = arrays[1:arrays.find(']')].split(',')
    lemmas = filter(lambda x: x != '', lemmas)
    lemmas = [lemma.strip() for lemma in lemmas]
    new_vec = dictionary.doc2bow(lemmas)
    if len(new_vec) == 0:
     out.write('%s\n' % fixed)
    else:
     counts = ['%s,%s' % (fid,count) for (fid, count) in new_vec]
     counts = ' '.join(counts)
     out.write('%s %s\n' % (fixed, counts))
  out.close()
    
if __name__ == '__main__':
  main()

