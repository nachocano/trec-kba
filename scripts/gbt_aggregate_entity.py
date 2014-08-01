#!/usr/bin/python
from utils import to_rnr, to_uv, to_uv_given_pred, feature_importance, filter_run, build_record, load_model, create_data, get_prob_and_pred, get_prob_and_pred_single
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
    parser.add_argument('-tr', '--train_with_vectors_and_distance_tsv_file', required=True)
    parser.add_argument('-t', '--test_with_vectors_sorted_tsv_file', required=True)
    parser.add_argument('-a', '--aggregate_vector_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnr', '--rnr_load_model_file', required=True)
    parser.add_argument('-uv', '--uv_load_model_file', required=True)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id

    clf_rnr_global = load_model(args.rnr_load_model_file)
    clf_uv_global = load_model(args.uv_load_model_file)  
    
    aggregates = {}
    for line in open(args.aggregate_vector_file).read().splitlines():
        targetid, aggregate = line.split(',')
        aggregate = np.array(aggregate.split()).astype(float)
        aggregates[targetid] = aggregate

    recs = []

    x_train, y_train, train_context = create_data(args.train_with_vectors_and_distance_tsv_file)
    x_test, y_test, test_context = create_data(args.test_with_vectors_sorted_tsv_file)

    # ----- Test on N-RN classifier
    pred_rnr_prob = {}
    pred_rnr = {}
    for targetid in x_test:
        pred_rnr_prob[targetid] = clf_rnr_global.predict_proba(x_test[targetid])
        pred_rnr[targetid] = np.array(map(np.argmax, pred_rnr_prob[targetid]))
    
    for targetid in y_test:
        for i, prob in enumerate(pred_rnr_prob[targetid]):
            if prob[0] >= prob[1]:
                recs.append(build_record(i, test_context[targetid], 0, prob[0]))


    #------------ UV classifier
    
    x_train_uv = {}
    y_train_uv = {}

    for targetid in y_train:
        candidate_x, candidate_y = to_uv(x_train[targetid], y_train[targetid])
        if len(set(candidate_y)) > 1:
            x_train_uv[targetid] = candidate_x
            y_train_uv[targetid] = candidate_y

    x_test_uv = {}
    y_test_uv = {}
    idxs_context = {}
    for targetid in y_test:
        x_test_uv[targetid], y_test_uv[targetid], idxs_context[targetid] = to_uv_given_pred(x_test[targetid], y_test[targetid], pred_rnr[targetid])


    for targetid in y_test:
        assert y_test_uv[targetid].shape[0] == len(pred_rnr[targetid][pred_rnr[targetid] == 1])
        assert y_test_uv[targetid].shape[0] == len(idxs_context[targetid])


    clf_uvs = {}
    for targetid in x_train_uv:
        clf_uv = ensemble.GradientBoostingClassifier()
        clf_uv = clf_uv.fit(x_train_uv[targetid], y_train_uv[targetid])
        #feature_importance(clf_uv.feature_importances_, 'U-V')
        clf_uvs[targetid] = clf_uv


    aggregates_updates = defaultdict(list)
    for target in y_test_uv:
        if not aggregates_updates.has_key(targetid):
            aggregates_updates[targetid].append(np.copy(aggregates[targetid]))


   # predicting U-V
    start = time.time()
    print 'testing on uv classifier...'
    pred_uv_prob = defaultdict(list)
    for targetid in x_test_uv:
        prob_entity = None
        for i in xrange(y_test_uv[targetid].shape[0]):
            distance = euclidean(x_test_uv[targetid][i][25:], aggregates[targetid])
            instance_to_predict = np.hstack((x_test_uv[targetid][i], np.array([distance])))
            if clf_uvs.has_key(targetid):
                prob_entity = clf_uvs[targetid].predict_proba(instance_to_predict)[0]
            prob_global = clf_uv_global.predict_proba(instance_to_predict)[0]
            if prob_entity == None:
                pred_uv_prob[targetid].append(prob_global)
            else:
                prob, pred = get_prob_and_pred_single(prob_global, prob_entity)
                pred_uv_prob[targetid].append(prob)
            aggregates_updates[targetid].append(x_test_uv[targetid][i][25:])
            aggregates[targetid] = np.mean(aggregates_updates[targetid], axis=0)
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    for targetid in y_test_uv:
        pred_uv = np.array(map(np.argmax, pred_uv_prob[targetid]))
        pred_uv += 1
        for i, relevance in enumerate(pred_uv):
            prob = max(pred_uv_prob[targetid][i])
            recs.append(build_record(idxs_context[targetid][i], test_context[targetid], relevance, prob))

    len_predictions = 0
    for targetid in y_test:
        len_predictions += len(y_test[targetid])

    assert len(recs) == len_predictions

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
