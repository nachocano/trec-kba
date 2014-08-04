#!/usr/bin/python
from utils import to_rnr, to_uv, to_uv_given_pred, feature_importance, filter_run, build_record, load_model, create_data, get_prob_and_pred
import re
import os
import sys
import json
import time
import argparse
import numpy as np
from sklearn import ensemble
from sklearn import metrics
from collections import defaultdict

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_with_vector_tsv_file', required=True)
    parser.add_argument('-t', '--test_with_vector_tsv_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-m', '--load_model_file', required=True)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["system_id"] = args.system_id
    filter_run["run_info"] = {
        "num_entities": len(entities),
    }

    # load global models
    clf_global = load_model(args.load_model_file)
        
    recs = []

    x_train, y_train, train_context = create_data(args.train_with_vector_tsv_file)
    x_test, y_test, test_context = create_data(args.test_with_vector_tsv_file)

    x_train_ent = {}
    y_train_ent = {}
    for targetid in y_train:
        if len(set(y_train[targetid])) == 4:
            x_train_ent[targetid] = x_train[targetid]
            y_train_ent[targetid] = y_train[targetid]

    clfs = {}
    for targetid in x_train_ent:
        clf = ensemble.GradientBoostingClassifier()
        clf = clf.fit(x_train_ent[targetid], y_train_ent[targetid])
        clfs[targetid] = clf

    pred_prob = {}
    pred = {}
    for targetid in x_test:
        prob_entity = None
        if clfs.has_key(targetid):
            prob_entity = clfs[targetid].predict_proba(x_test[targetid])
        prob_global = clf_global.predict_proba(x_test[targetid])
        if prob_entity == None:
            pred_prob[targetid] = prob_global
            pred[targetid] = np.array(map(np.argmax, prob_global))
        else:
            pred_prob[targetid], pred[targetid], _, _, _ = get_prob_and_pred(prob_global, prob_entity)

    for targetid in y_test:
        pred[targetid] -= 1
        for i, prob in enumerate(pred_prob[targetid]):
            prediction = pred[targetid][i]
            probability = prob[prediction+1]
            truth = int(y_test[targetid][i])
            prob_truth = prob[truth+1]
            recs.append(build_record(i, test_context[targetid], prediction, probability))
            print '%s %s' % (prob_truth, truth)

    for targetid in y_test:
        assert y_test[targetid].shape == pred[targetid].shape

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
