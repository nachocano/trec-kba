#!/usr/bin/python

import re
import os
import sys
import json
import time
import argparse
import numpy as np
from sklearn import ensemble
from sklearn import metrics
#import graphlab as gl


def to_rnr(y):
    y_rnr = np.array(y)
    for i, value in enumerate(y):
        if value == -1:
            y_rnr[i] = 0
        elif value == 2:
            y_rnr[i] = 1
    return y_rnr

def to_uv(x,y):
    idxs = np.where(y > 0)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]])
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]
    return (x_uv, y_uv)

def to_uv_given_pred(x, y, pred_rnr):
    idxs = np.where(pred_rnr == 1)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]])
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]
    return (x_uv, y_uv, idxs)

def build_record(idx, context, relevance):
    stream_id, target_id, date_hour = context[idx].split()
    return [filter_run["team_id"], filter_run["system_id"], 
            stream_id, target_id, 1000, int(relevance), 1, date_hour, "NULL", -1, "0-0"]

def feature_importance(importances, classifier):
    indices = np.argsort(importances)[::-1]
    print 'Feature ranking for %s:' % classifier
    for f in xrange(len(importances)):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

filter_run = {
    "$schema": "http://trec-kba.org/schemas/v1.1/filter-run.json",
    "task_id": "kba-ccr-2014",
    "topic_set_id": "kba-2014-ccr-and-ssf",
    "corpus_id": "kba-streamcorpus-2014-v0_3_0-kba-filtered",
    "team_id": "UW",
    "team_name": "University of Washington",
    "poc_name": "UW Baseline", 
    "poc_email": "icano@cs.washington.edu",
    "system_id": "baseline",
    "run_type": "automatic",
    "system_description": "Baseline with RF classifier using docs in train dataset.",
    "system_description_short": "doc and doc-entity features",
    }

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-c', '--context_test_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-s', '--ssf', required=False)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id
    
    recs = []

    context = []
    with open(args.context_test_file) as f:
        for line in f.read().splitlines():
            context.append(line.strip())

    data_train = np.genfromtxt(args.training_file)
    x_train = data_train[:,1:]
    y_train = data_train[:,0]
    data_test = np.genfromtxt(args.test_file)
    x_test = data_test[:,1:]
    y_test = data_test[:,0]

    y_train_rnr = to_rnr(y_train)
    y_test_rnr = to_rnr(y_test)

    assert y_test.shape[0] == len(context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_train_rnr[y_train_rnr == -1]) == 0
    assert len(y_train_rnr[y_train_rnr == 2]) == 0
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    clf_rnr = ensemble.GradientBoostingClassifier()
    clf_rnr = clf_rnr.fit(x_train, y_train_rnr)
    feature_importance(clf_rnr.feature_importances_, 'R-NR')
    
    pred_rnr = clf_rnr.predict(x_test)

    neutrals = np.where(pred_rnr == 0)[0]
    for i, idx in enumerate(neutrals):
        recs.append(build_record(idx, context, 0))

    assert y_test_rnr.shape == pred_rnr.shape

    x_train_uv, y_train_uv = to_uv(x_train, y_train)
    x_test_uv, y_test_uv, idxs_context = to_uv_given_pred(x_test, y_test, pred_rnr)

    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])
    assert y_test_uv.shape[0] == len(idxs_context)

    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv, y_train_uv)
    feature_importance(clf_uv.feature_importances_, 'U-V')

    pred_uv = clf_uv.predict(x_test_uv)
    for i, relevance in enumerate(pred_uv):
        recs.append(build_record(idxs_context[i], context, relevance))


    assert len(recs) == y_test.shape[0]
    assert y_test_uv.shape == pred_uv.shape

    # some metrics
    print 'macro %s' % str(metrics.precision_recall_fscore_support(y_test_rnr, pred_rnr, average="macro"))
    print 'micro %s' % str(metrics.precision_recall_fscore_support(y_test_rnr, pred_rnr, average="micro"))
    print 'weighted %s' % str(metrics.precision_recall_fscore_support(y_test_rnr, pred_rnr, average="weighted"))

    print 'macro %s' % str(metrics.precision_recall_fscore_support(y_test_uv, pred_uv, average="macro"))
    print 'micro %s' % str(metrics.precision_recall_fscore_support(y_test_uv, pred_uv, average="micro"))
    print 'weighted %s' % str(metrics.precision_recall_fscore_support(y_test_uv, pred_uv, average="weighted"))

    
    output = open(args.output_file, "w")
    for rec in recs:
        output.write("\t".join(map(str, rec)) + "\n")

    filter_run_json_string = json.dumps(filter_run, indent=4, sort_keys=True)
    filter_run_json_string = re.sub("\n", "\n#", filter_run_json_string)
    output.write("#%s\n" % filter_run_json_string)
    output.close()

if __name__ == '__main__':
  np.set_printoptions(threshold=np.nan)
  main()
