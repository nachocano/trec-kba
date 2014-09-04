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
        nouns = x[625:629]
        verbs = x[629:633]
        assert nouns[2] >= 0 and nouns[2] <= 1
        assert verbs[2] >= 0 and verbs[2] <= 1
        #if nouns[2] < 0.5 and nouns[2] > 0:
        #    print nouns[2]
        targetid = cxt.split()[1]
        if y == 1:
            targetids[targetid]['nouns']['useful'].append(nouns)
            targetids[targetid]['verbs']['useful'].append(verbs)
        elif y == 2:
            targetids[targetid]['nouns']['vital'].append(nouns)
            targetids[targetid]['verbs']['vital'].append(verbs)
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

    #x_test_a_r, y_test_a_r, cxt_test_a_r = create_relevant_global_data(args.test_relevant)

    #assert len(y_test_a_r[y_test_a_r == -1]) == 0
    #assert len(y_test_a_r[y_test_a_r == 0]) == 0
    #assert len(y_test_a_r[y_test_a_r == -10]) == 0

    targetids = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    populate(targetids, x_train_a_r, y_train_a_r, cxt_train_a_r)
    #populate(targetids, x_test_a_r, y_test_a_r, cxt_test_a_r)
    elapsed = time.time() - start
    print 'read data and build lists finished, took %s' % elapsed

    timeliness_vs_min_distance(targetids)
    #feature_dist(targetids)

    #run = read_run(args.run)

    #print_errors_per_entity(run, x_train_a_r, y_train_a_r, cxt_train_a_r, x_test_a_r, y_test_a_r, cxt_test_a_r)


 
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
    #x = np.vstack((x_train_a_r, x_test_a_r))
    #y = np.hstack((y_train_a_r, y_test_a_r))
    #cxt = cxt_train_a_r + cxt_test_a_r
    counts_v = defaultdict(lambda: defaultdict(int))
    print 'number test assessed relevant docs %s' % y_test_a_r.shape[0]
    #errors = defaultdict(list)
    for xi, yi, ci in zip(x_test_a_r, y_test_a_r, cxt_test_a_r):
        streamid, targetid, date_hour = ci.split()
        if run[targetid].has_key(streamid):
            prediction = run[targetid][streamid]
            vital_only(counts_v, targetid, yi, prediction)
            #if yi != prediction:
            #errors[targetid].append((streamid, yi, prediction))

    tps = 0
    tns = 0
    fps = 0
    fns = 0
    for targetid in counts_v:
        tps += counts_v[targetid]['TP']
        fps += counts_v[targetid]['FP']
        fns += counts_v[targetid]['FN']
        tns += counts_v[targetid]['TN']

    print 'TP %s' % tps
    print 'TN %s' % tns
    print 'FP %s' % fps
    print 'FN %s' % fns

    p = precision(tps, fps)
    r = recall(tps, fns)
    f1 = fscore(p, r)

    print 'precision %s, recall %s, f1 %s' % (p, r, f1) 

#    total = 0
#    for targetid in errors:
#        total += len(errors[targetid])
#        print '%s %s' % (targetid, errors[targetid])
#    print 'total errors %s' % total

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


def feature_dist(targetids):
    for targetid in targetids:
        if "Mason" in targetid:
            features_n_u = feature_lists(targetids[targetid]['nouns']['useful'])
            features_n_v = feature_lists(targetids[targetid]['nouns']['vital'])
            features_v_u = feature_lists(targetids[targetid]['verbs']['useful'])
            features_v_v = feature_lists(targetids[targetid]['verbs']['vital'])
            #print '%s\tnouns useful avg min:%s\tnouns vital avg min:%s' % (targetid, np.mean(features_n_u[0]), np.mean(features_n_v[0]))
            #print '%s\tverbs useful avg min:%s\tverbs vital avg min:%s' % (targetid, np.mean(features_v_u[0]), np.mean(features_v_v[0]))
            plot_dist(targetid, features_n_u, features_n_v, features_v_u, features_v_v)


def plot_dist(targetid, features_n_u, features_n_v, features_v_u, features_v_v):
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

def vital_only(counts_v, targetid, truth, prediction):
    if prediction == 2 and truth == 2:
        counts_v[targetid]['TP'] += 1
    elif prediction == 2 and truth != 2:
        counts_v[targetid]['FP'] += 1
    elif prediction != 2 and truth == 2:
        counts_v[targetid]['FN'] += 1
    elif prediction != 2 and truth != 2:
        counts_v[targetid]['TN'] += 1


def timeliness_vs_min_distance(targetids):
    features_n_u_min = []
    features_n_v_min = []
    features_v_u_min = []
    features_v_v_min = []
    features_n_u_avg = []
    features_n_v_avg = []
    features_v_u_avg = []
    features_v_v_avg = []
    features_n_u_time = []
    features_n_v_time = []
    features_v_u_time = []
    features_v_v_time = []
    for targetid in targetids:
        features_n_u = feature_lists(targetids[targetid]['nouns']['useful'])
        features_n_u_min.extend(features_n_u[0])
        features_n_u_avg.extend(features_n_u[1])
        features_n_u_time.extend(features_n_u[2])
        features_n_v = feature_lists(targetids[targetid]['nouns']['vital'])
        features_n_v_min.extend(features_n_v[0])
        features_n_v_avg.extend(features_n_v[1])
        features_n_v_time.extend(features_n_v[2])
        features_v_u = feature_lists(targetids[targetid]['verbs']['useful'])
        features_v_u_min.extend(features_v_u[0])
        features_v_u_avg.extend(features_v_u[1])
        features_v_u_time.extend(features_v_u[2])
        features_v_v = feature_lists(targetids[targetid]['verbs']['vital'])
        features_v_v_min.extend(features_v_v[0])
        features_v_v_avg.extend(features_v_v[1])
        features_v_v_time.extend(features_v_v[2])
    plot_timeliness_vs_x("Min Distance", features_n_u_min, features_n_v_min, features_v_u_min, features_v_v_min, features_n_u_time, features_n_v_time, features_v_u_time, features_v_v_time)
    plot_timeliness_vs_x("Avg Distance", features_n_u_avg, features_n_v_avg, features_v_u_avg, features_v_v_avg, features_n_u_time, features_n_v_time, features_v_u_time, features_v_v_time)


def plot_timeliness_vs_x(vs, features_n_u_x, features_n_v_x, features_v_u_x, features_v_v_x, features_n_u_y, features_n_v_y, features_v_u_y, features_v_v_y):
    f, axarr = plt.subplots(1, 2)
    f.suptitle("Timeliness vs %s" % vs, fontsize=13, fontweight='bold')
    axarr[0].scatter(features_n_u_x, features_n_u_y, c='b', label='useful')
    axarr[0].scatter(features_n_v_x, features_n_v_y, c='r', label='vital')
    axarr[0].set_title('Nouns')
    axarr[1].scatter(features_v_u_x, features_v_u_y, c='b', label='useful')
    axarr[1].scatter(features_v_v_x, features_v_v_y, c='r', label='vital')
    axarr[1].set_title('Verbs')
    plt.legend(loc="upper right")
    plt.xlabel(vs.lower())
    plt.ylabel('timeliness')
    plt.show()


if __name__ == '__main__':
  main()
