#!/usr/bin/python
from utils import to_rnr, to_uv, to_uv_given_pred, feature_importance, filter_run, build_record, save_model
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

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-c', '--context_test_file', required=True)
    parser.add_argument('-a', '--aggregate_vector_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnr', '--rnr_save_model_file', required=False)
    parser.add_argument('-uv', '--uv_save_model_file', required=False)
    parser.add_argument('-s', '--ssf', required=False)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id
    
    aggregates_uv = {}
    for line in open(args.aggregate_vector_file).read().splitlines():
        targetid, aggregate = line.split(',')
        aggregate = np.array(aggregate.split()).astype(float)
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

    x_train_rnr = x_train[:,:-1]
    y_train_rnr = to_rnr(y_train)
    y_test_rnr = to_rnr(y_test)

    assert y_test.shape[0] == len(context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_train_rnr[y_train_rnr == -1]) == 0
    assert len(y_train_rnr[y_train_rnr == 2]) == 0
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    clf_rnr = ensemble.GradientBoostingClassifier()
    clf_rnr = clf_rnr.fit(x_train_rnr, y_train_rnr)
    
    feature_importance(clf_rnr.feature_importances_, 'R-NR')

    save_model(args.rnr_save_model_file, clf_rnr)

    pred_rnr_prob = clf_rnr.predict_proba(x_test)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))
    
    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, context, 0, prob[0]))

    assert y_test_rnr.shape == pred_rnr.shape

    x_train_uv, y_train_uv = to_uv(x_train, y_train)
    x_test_uv, y_test_uv, idxs_context = to_uv_given_pred(x_test, y_test, pred_rnr)

    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])
    assert y_test_uv.shape[0] == len(idxs_context)

    clf_uv = ensemble.GradientBoostingClassifier()
    # train it with the distance field
    clf_uv = clf_uv.fit(x_train_uv, y_train_uv)

    feature_importance(clf_uv.feature_importances_, 'U-V')
    
    save_model(args.uv_save_model_file, clf_uv)

    aggregates_updates = defaultdict(list)
    for i in xrange(y_test_uv.shape[0]):
        idx = idxs_context[i]
        targetid = context[idx].split()[1]
        if not aggregates_updates.has_key(targetid):
            aggregates_updates[targetid].append(np.copy(aggregates_uv[targetid]))

    start = time.time()
    print 'testing on uv classifier...'
    pred_uv_prob = []
    for i in xrange(y_test_uv.shape[0]):
        idx = idxs_context[i]
        targetid = context[idx].split()[1]
        distance = euclidean(x_test_uv[i][25:], aggregates_uv[targetid])
        instance_to_predict = np.hstack((x_test_uv[i], np.array([distance])))
        pred_uv_prob.append(clf_uv.predict_proba(instance_to_predict)[0])
        aggregates_updates[targetid].append(x_test_uv[i][25:])
        aggregates_uv[targetid] = np.mean(aggregates_updates[targetid], axis=0)
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    pred_uv = np.array(map(np.argmax, pred_uv_prob))
    pred_uv += 1
    for i, relevance in enumerate(pred_uv):
        prob = max(pred_uv_prob[i])
        recs.append(build_record(idxs_context[i], context, relevance, prob))

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
