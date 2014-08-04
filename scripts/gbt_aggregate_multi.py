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
    parser.add_argument('-m', '--save_model_file', required=False)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id
    
    aggregates = {}
    for line in open(args.aggregate_vector_file).read().splitlines():
        targetid, aggregate = line.split(',')
        aggregate = np.array(aggregate.split()).astype(float)
        aggregates[targetid] = aggregate

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

    assert y_test.shape[0] == len(context)

    clf = ensemble.GradientBoostingClassifier()
    clf = clf.fit(x_train, y_train)
    
    #feature_importance(clf.feature_importances_, 'Aggregate MultiClass')

    save_model(args.save_model_file, clf)

    aggregates_updates = defaultdict(list)
    for i in xrange(y_test.shape[0]):
        targetid = context[i].split()[1]
        if not aggregates_updates.has_key(targetid):
            aggregates_updates[targetid].append(np.copy(aggregates[targetid]))

    pred_prob = []
    for i in xrange(y_test.shape[0]):
        targetid = context[i].split()[1]
        distance = euclidean(x_test[i][25:], aggregates[targetid])
        instance_to_predict = np.hstack((x_test[i], np.array([distance])))
        pred_prob.append(clf.predict_proba(instance_to_predict)[0])
        aggregates_updates[targetid].append(x_test[i][25:])
        aggregates[targetid] = np.mean(aggregates_updates[targetid], axis=0)

    pred = np.array(map(np.argmax, pred_prob))
    pred -= 1
    for i, prob in enumerate(pred_prob):
        prediction = pred[i]
        probability = prob[prediction+1]
        truth = int(y_test[i])
        prob_truth = prob[truth+1]
        recs.append(build_record(i, context, prediction, probability))
        print '%s %s' % (prob_truth, truth)

    assert len(recs) == y_test.shape[0]

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
