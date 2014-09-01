#!/usr/bin/python
from __future__ import division
import argparse
from utils import create_separate_global_data
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import Counter
import time
import numpy as np


def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-tr', '--train_relevant', required=True)
    parser.add_argument('-t', '--test_relevant', required=True)
    args = parser.parse_args()

    start = time.time()
    print 'reading data and building lists'
    x_train_a_r, y_train_a_r, cxt_train_a_r, _, _, _ = create_separate_global_data(args.train_relevant)
    x_test_a_r, y_test_a_r, cxt_test_a_r, _, _, _ = create_separate_global_data(args.test_relevant)

    targetids = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for x, y, cxt in zip(x_train_a_r, y_train_a_r, cxt_train_a_r):
        targetid = cxt.split()[1]
        if y == 1:
            targetids[targetid]['nouns']['useful'].append(x[625:629])
            targetids[targetid]['verbs']['useful'].append(x[629:633])
        elif y == 2:
            targetids[targetid]['nouns']['vital'].append(x[625:629])
            targetids[targetid]['verbs']['vital'].append(x[629:633])
        else:
            print 'invalid label, should be 1 or 2, is %s' % y
    elapsed = time.time() - start
    print 'read data and build lists finished, took %s' % elapsed


    for targetid in targetids:
        if "BNSF_Railway" in targetid:
            features_n_u = feature_lists(targetids[targetid]['nouns']['useful'])
            features_n_v = feature_lists(targetids[targetid]['nouns']['vital'])
            features_v_u = feature_lists(targetids[targetid]['verbs']['useful'])
            features_v_v = feature_lists(targetids[targetid]['verbs']['vital'])
            plot(targetid, features_n_u, features_n_v, features_v_u, features_v_v)
        
def feature_lists(array):
    mins = []
    avgs = []
    times = []
    zeros = []
    for e in array:
        mins.append(e[0])
        avgs.append(e[1])
        times.append(e[2])
        zeros.append(e[3])
    return mins, avgs, times, zeros

def plot(targetid, features_n_u, features_n_v, features_v_u, features_v_v):
    fig = plt.figure()
    fig.suptitle(targetid, fontsize=13, fontweight='bold')
    nr_docs = np.arange(len(features_n_v[0])) + 1
    plt.plot(nr_docs, features_n_v[0], 'r', nr_docs, features_n_v[1], 'g', nr_docs, features_n_v[2], 'b', nr_docs, features_n_v[3], 'y')
    plt.xlabel("nr docs")
    plt.legend(('mins', 'avg', 'timeliness', 'allzeros'), loc="upper right")
    plt.show()

if __name__ == '__main__':
  main()
