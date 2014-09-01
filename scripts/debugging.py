#!/usr/bin/python
from __future__ import division
import argparse
from utils import create_relevant_global_data
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import Counter
import time
import numpy as np

def populate(targetids, x_a_r, y_a_r, cxt_a_r):
    for x, y, cxt in zip(x_a_r, y_a_r, cxt_a_r):
        targetid = cxt.split()[1]
        if y == 1:
            targetids[targetid]['nouns']['useful'].append(x[625:629])
            targetids[targetid]['verbs']['useful'].append(x[629:633])
        elif y == 2:
            targetids[targetid]['nouns']['vital'].append(x[625:629])
            targetids[targetid]['verbs']['vital'].append(x[629:633])
        else:
            print 'invalid label, should be 1 or 2, is %s' % y

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-tr', '--train_relevant', required=True)
    parser.add_argument('-t', '--test_relevant', required=True)
    parser.add_argument('-r', '--run', required=True)
    args = parser.parse_args()

    start = time.time()
    print 'reading data and building lists'
    x_train_a_r, y_train_a_r, cxt_train_a_r = create_relevant_global_data(args.train_relevant)

    assert len(y_train_a_r[y_train_a_r == -1]) == 0
    assert len(y_train_a_r[y_train_a_r == 0]) == 0
    assert len(y_train_a_r[y_train_a_r == -10]) == 0

    x_test_a_r, y_test_a_r, cxt_test_a_r = create_relevant_global_data(args.test_relevant)

    assert len(y_test_a_r[y_test_a_r == -1]) == 0
    assert len(y_test_a_r[y_test_a_r == 0]) == 0
    assert len(y_test_a_r[y_test_a_r == -10]) == 0

    targetids = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    populate(targetids, x_train_a_r, y_train_a_r, cxt_train_a_r)
    populate(targetids, x_test_a_r, y_test_a_r, cxt_test_a_r)
    elapsed = time.time() - start
    print 'read data and build lists finished, took %s' % elapsed

    #feature_dist(targetids)

    run = read_run(args.run)

    print_errors_per_entity(run, x_train_a_r, y_train_a_r, cxt_train_a_r, x_test_a_r, y_test_a_r, cxt_test_a_r)


 
def read_run(run_file):
    run = defaultdict(dict)
    with open(run_file) as f:
        for line in f.read().splitlines():
            l = line.strip()
            if l.startswith('#'):
                continue
            l = l.split('\t')
            #timestamp = int(streamid.split('-')[0])
            #hour_bucket = int(timestamp / 3600)
            streamid = l[2]
            targetid = l[3]
            relevance = int(l[5])
            #date_hour = l[7]
            if relevance == 1 or relevance == 2:
                run[targetid][streamid] = relevance
    return run

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


def print_errors_per_entity(run, x_train_a_r, y_train_a_r, cxt_train_a_r, x_test_a_r, y_test_a_r, cxt_test_a_r):
    x = np.vstack((x_train_a_r, x_test_a_r))
    y = np.hstack((y_train_a_r, y_test_a_r))
    cxt = cxt_train_a_r + cxt_test_a_r
    errors = defaultdict(list)
    for xi, yi, ci in zip(x, y, cxt):
        streamid, targetid, date_hour = ci.split()
        if run[targetid].has_key(streamid):
            truth_relevance = run[targetid][streamid]
            if yi != truth_relevance:
                errors[targetid].append((streamid, truth_relevance, yi))

    total = 0
    for targetid in errors:
        total += len(errors[targetid])
        print '%s %s' % (targetid, errors[targetid])
    print 'total errors %s' % total

def feature_dist(targetids):
    for targetid in targetids:
        if "Mason" in targetid:
            features_n_u = feature_lists(targetids[targetid]['nouns']['useful'])
            features_n_v = feature_lists(targetids[targetid]['nouns']['vital'])
            features_v_u = feature_lists(targetids[targetid]['verbs']['useful'])
            features_v_v = feature_lists(targetids[targetid]['verbs']['vital'])
            #print '%s\tnouns useful avg min:%s\tnouns vital avg min:%s' % (targetid, np.mean(features_n_u[0]), np.mean(features_n_v[0]))
            #print '%s\tverbs useful avg min:%s\tverbs vital avg min:%s' % (targetid, np.mean(features_v_u[0]), np.mean(features_v_v[0]))
            plot(targetid, features_n_u, features_n_v, features_v_u, features_v_v)


def plot(targetid, features_n_u, features_n_v, features_v_u, features_v_v):
    nr_useful_docs = np.arange(len(features_n_u[0])) + 1
    nr_vital_docs = np.arange(len(features_n_v[0])) + 1
    f, axarr = plt.subplots(2, 2)
    f.suptitle(targetid, fontsize=13, fontweight='bold')
    axarr[0, 0].plot(nr_useful_docs, features_n_u[0], 'r', nr_useful_docs, features_n_u[1], 'g')
    axarr[0, 0].set_title('Nouns Useful')
    axarr[0, 1].plot(nr_vital_docs, features_n_v[0], 'r', nr_vital_docs, features_n_v[1], 'g')
    axarr[0, 1].set_title('Nouns Vital')
    axarr[1, 0].plot(nr_useful_docs, features_v_u[0], 'r', nr_useful_docs, features_v_u[1], 'g')
    axarr[1, 0].set_title('Verbs Useful')
    axarr[1, 1].plot(nr_vital_docs, features_v_v[0], 'r', nr_vital_docs, features_v_v[1], 'g')
    axarr[1, 1].set_title('Verbs Vital')
    plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
    #plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
    plt.legend(('mins', 'avg'), loc="upper right")
    plt.show()

if __name__ == '__main__':
  main()
