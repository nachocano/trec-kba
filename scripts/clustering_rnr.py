#!/usr/bin/python
from __future__ import division
from utils import load_model
import os
import sys
import time
import argparse
import numpy as np
from sklearn import ensemble
from collections import defaultdict

def read_data(filename):
    x_list = []
    lines = []
    with open(filename) as f:
        for line in f.read().splitlines():
            lines.append(line)
            instance = line.split()
            x_list.append(instance[4:29])
    return np.array(x_list), lines

def do_predict(clf_rnr, x, lines, nr_file, r_file):
    pred_rnr_prob = clf_rnr.predict_proba(x)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))
    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            instance = lines[i].split()
            streamid = instance[0]
            targetid = instance[1]
            date_hour = instance[2]
            confidence = int(prob[0] * 1000)
            to_write = '%s\t%s\t%s\t0\t1\t%s\tNULL\t-1\t0-0\n' % (streamid, targetid, confidence, date_hour)
            nr_file.write(to_write)
        else:
            r_file.write('%s\n' % lines[i])

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-nro', '--non_relevant_predictions_file', required=True)
    parser.add_argument('-rotr', '--relevant_output_train_unassessed_file', required=True)
    parser.add_argument('-rot', '--relevant_output_test_file', required=True)
    parser.add_argument('-tru', '--train_unassessed', required=True)
    parser.add_argument('-t', '--test_all', required=True)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=True)

    args = parser.parse_args()

    begin = time.time()

    # read whole dataset
    print 'reading dataset'
    start = time.time()
    x_train_u, train_u_lines = read_data(args.train_unassessed)
    x_test, test_lines = read_data(args.test_all)
    elapsed = time.time() - start
    print 'dataset read, took %s' % elapsed

    print 'train u shape %s' % str(x_train_u.shape)
    print 'test shape %s' % str(x_test.shape)

    # RNR classifier
    clf_rnr = load_model(args.rnr_load_model_file)

    nr_file = open(args.non_relevant_predictions_file, 'w')
    rtr_file = open(args.relevant_output_train_unassessed_file, 'w')
    rt_file = open(args.relevant_output_test_file, 'w')

    print 'predicting rnr'
    start = time.time()
    do_predict(clf_rnr, x_train_u, train_u_lines, nr_file, rtr_file)
    do_predict(clf_rnr, x_test, test_lines, nr_file, rt_file)
    elapsed = time.time() - start
    print 'rnr predicted, took %s' % elapsed

    nr_file.close()
    rtr_file.close()
    rt_file.close()


if __name__ == '__main__':
  main()
