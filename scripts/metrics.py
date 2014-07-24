#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict


counts_v = defaultdict(lambda: defaultdict(int))
counts_vu = defaultdict(lambda: defaultdict(int))

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    # test.tsv
    parser.add_argument('-t', '--truth', required=True)
    parser.add_argument('-r', '--run', required=True)
    args = parser.parse_args()

    run = {}
    with open(args.run) as f:
        for line in f.read().splitlines():
            l = line.strip()
            if l.startswith('#'):
                continue
            l = l.split('\t')
            streamid = l[2]
            targetid = l[3]
            relevance = l[5]
            date_hour = l[7]
            run[(streamid, targetid, date_hour)] = int(relevance)

    truth = {}
    with open(args.truth) as f:
        for line in f.read().splitlines():
            l = line.strip().split()
            streamid = l[0]
            targetid = l[1]
            date_hour = l[2]
            relevance = l[3]
            truth[(streamid, targetid, date_hour)] = int(relevance)

    assert len(truth) == len(run)

    for key in truth:
        truth_relevance = truth[key]
        run_relevance = run[key]
        targetid = key[1]
        vital_only(targetid, truth_relevance, run_relevance)
        vital_plus_useful(targetid, truth_relevance, run_relevance)

    print 'micro v   %s' % str(micro_stats(counts_v))
    print 'micro v+u %s' % str(micro_stats(counts_vu))
    print 'macro v   %s' % str(macro_stats(counts_v))
    print 'macro v+u %s' % str(macro_stats(counts_vu))

def micro_stats(counts):
    tp = 0
    fp = 0
    fn = 0
    for targetid in counts:
        tp += counts[targetid]['TP']
        fp += counts[targetid]['FP']
        fn += counts[targetid]['FN']
    p = precision(tp, fp)
    r = recall(tp, fn)
    f1 = fscore(p, r)
    return p, r, f1

def macro_stats(counts):
    precisions = []
    recalls = []
    fscores = []
    for targetid in counts:
        p = precision(counts[targetid]['TP'], counts[targetid]['FP'])
        precisions.append(p)
        r = recall(counts[targetid]['TP'], counts[targetid]['FN'])
        recalls.append(r)
        fscores.append(fscore(p, r))
    p = sum(precisions) / len(precisions)
    r = sum(recalls) / len(recalls)
    f1 = fscore(p, r)
    return p, r, f1

def vital_only(targetid, truth, prediction):
    if prediction == 2 and truth == 2:
        counts_v[targetid]['TP'] += 1
    elif prediction == 2 and truth != 2:
        counts_v[targetid]['FP'] += 1
    elif prediction != 2 and truth == 2:
        counts_v[targetid]['FN'] += 1

def vital_plus_useful(targetid, truth, prediction):
    if (prediction == 1 and truth == 1) or (prediction == 2 and truth == 2):
        counts_vu[targetid]['TP'] += 1
    elif (prediction == 1 and truth != 1) or (prediction == 2 and truth != 2):
        counts_vu[targetid]['FP'] += 1
    elif (prediction != 1 and truth == 1) or (prediction != 2 and truth == 2):
        counts_vu[targetid]['FN'] += 1

def precision(TP, FP):
    if (TP+FP) > 0:
        precision = float(TP) / (TP + FP)
        return precision
    else:
        return 0.0

def recall(TP, FN):
    if (TP+FN) > 0:
        recall = float(TP) / (TP + FN)
        return recall
    else:
        return 0.0

def fscore(precision=None, recall=None):
    if precision + recall > 0:
        return float(2 * precision * recall) / (precision + recall)
    else:
        return 0.0
    
def scaled_utility(TP, FP, FN, MinNU = -0.5):
    if (TP + FN) > 0:
        T11U = float(2 * TP - FP)
        MaxU = float(2 * (TP + FN))
        T11NU = float(T11U) / MaxU 
        return (max(T11NU, MinNU) - MinNU) / (1 - MinNU)
    else:
        return 0.0


if __name__ == '__main__':
  main()
