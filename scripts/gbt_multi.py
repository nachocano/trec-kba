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

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-c', '--context_test_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-m', '--save_model', required=False)
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

    assert y_test.shape[0] == len(context)

    clf = ensemble.GradientBoostingClassifier()
    clf = clf.fit(x_train, y_train)
    #feature_importance(clf.feature_importances_, 'GBT MultiClass')

    if args.save_model:
        save_model(args.save_model, clf)
    
    pred_prob = clf.predict_proba(x_test)
    pred = np.array(map(np.argmax, pred_prob))
    pred -= 1

    assert y_test.shape == pred.shape

    for i, prob in enumerate(pred_prob):
        prediction = pred[i]
        probability = prob[prediction+1]
        truth = int(y_test[i])
        prob_truth = prob[truth+1]
        recs.append(build_record(i, context, prediction, probability))
        print '%s %s %s %s %s %s' % (prob[0], prob[1], prob[2], prob[3], prediction, truth)

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
