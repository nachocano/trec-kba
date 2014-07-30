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
from scipy.spatial.distance import euclidean
from collections import defaultdict

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


filter_run = {
    "$schema": "http://trec-kba.org/schemas/v1.1/filter-run.json",
    "task_id": "kba-ccr-2014",
    "topic_set_id": "kba-2014-ccr-and-ssf",
    "corpus_id": "kba-streamcorpus-2014-v0_3_0-kba-filtered",
    "team_id": "UW",
    "team_name": "University of Washington",
    "poc_name": "UW Aggregate Embedding", 
    "poc_email": "icano@cs.washington.edu",
    "system_id": "aggregate",
    "run_type": "automatic",
    "system_description": "RF classifier using aggregate vectors distances",
    "system_description_short": "doc and doc-entity features, plus distance from aggregate vectors",
    }

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-c', '--context_test_file', required=True)
    parser.add_argument('-a', '--aggregate_vector_file', required=True)
    parser.add_argument('-s', '--ssf', required=False)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    
    aggregates_rnr = {}
    aggregates_uv = {}
    for line in open(args.aggregate_vector_file).read().splitlines():
        targetid, aggregate = line.split(',')
        aggregate = np.array(aggregate.split()).astype(float)
        aggregates_rnr[targetid] = aggregate
        aggregates_uv[targetid] = np.copy(aggregate)

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
    #print clf_rnr.feature_importances_

    aggregates_updates = defaultdict(list)
    for line in context:
        targetid = line.split()[1]
        if not aggregates_updates.has_key(targetid):
            aggregates_updates[targetid].append(np.copy(aggregates_rnr[targetid]))
    
    start = time.time()
    print 'testing on rnr classifier...'
    pred_rnr = np.zeros(y_test_rnr.shape)
    for i, test_cxt in enumerate(context):
        targetid = test_cxt.split()[1]
        distance = euclidean(x_test[i][25:], aggregates_rnr[targetid])
        instance_to_predict = np.hstack((x_test[i][:25], np.array([distance])))
        pred_rnr[i] = clf_rnr.predict(instance_to_predict)
        aggregates_updates[targetid].append(x_test[i][25:])
        aggregates_rnr[targetid] = np.mean(aggregates_updates[targetid], axis=0)
    elapsed = time.time() - start
    print 'finished testing on rnr classifier, took %s' % elapsed

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

    aggregates_updates.clear()
    aggregates_updates = defaultdict(list)
    for i in xrange(y_test_uv.shape[0]):
        idx = idxs_context[i]
        targetid = context[idx].split()[1]
        if not aggregates_updates.has_key(targetid):
            aggregates_updates[targetid].append(np.copy(aggregates_uv[targetid]))

    start = time.time()
    print 'testing on uv classifier...'
    pred_uv = np.zeros(y_test_uv.shape)
    for i in xrange(pred_uv.shape[0]):
        idx = idxs_context[i]
        targetid = context[idx].split()[1]
        distance = euclidean(x_test_uv[i][25:], aggregates_uv[targetid])
        instance_to_predict = np.hstack((x_test_uv[i][:25], np.array([distance])))
        pred_uv[i] = clf_uv.predict(instance_to_predict)
        aggregates_updates[targetid].append(x_test_uv[i][25:])
        aggregates_uv[targetid] = np.mean(aggregates_updates[targetid], axis=0)
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    for i, relevance in enumerate(pred_uv):
        recs.append(build_record(idxs_context[i], context, relevance))


    assert len(recs) == y_test.shape[0]
    assert y_test_uv.shape == pred_uv.shape

    # some metrics
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
