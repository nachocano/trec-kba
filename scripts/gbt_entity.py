#!/usr/bin/python
from utils import to_rnr, to_uv, to_uv_given_pred, feature_importance, filter_run, build_record, load_model
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

def create_data(filename, minimum=-1):
    x_list = defaultdict(list)
    y_list = defaultdict(list)
    context = defaultdict(list)
    with open(filename) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            date_hour = instance[2]
            label = instance[3]
            features = instance[4:]
            x_list[targetid].append(features)
            y_list[targetid].append(label)
            context[targetid].append('%s %s %s' % (streamid, targetid, date_hour))

    x = {}
    y = {}
    for targetid in y_list:
            x[targetid] = np.array(x_list[targetid]).astype(float)
            y[targetid] = np.array(y_list[targetid]).astype(int)
    return x, y, context

def get_prob_and_pred(prob_global, prob_entity):
    prob_tmp_array = []
    pred_tmp_array = []
    mismatches = 0
    predictions_with_global = 0
    predictions_with_entity = 0
    for i in xrange(prob_global.shape[0]):
        pg = prob_global[i]
        pe = prob_entity[i]
        max_pe_idx = np.argmax(pe)
        max_pg_idx = np.argmax(pg)
        if max_pe_idx != max_pg_idx:
            mismatches += 1
        # take the one with highest prob to compute the confidence
        if pe[max_pe_idx] >= pg[max_pg_idx]:
            prob_tmp_array.append(pe)
            pred_tmp_array.append(max_pe_idx)
            predictions_with_entity += 1
        else:
            prob_tmp_array.append(pg)
            pred_tmp_array.append(max_pg_idx)
            predictions_with_global += 1
    return np.array(prob_tmp_array), np.array(pred_tmp_array), mismatches, predictions_with_global, predictions_with_entity

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_with_vector_tsv_file', required=True)
    parser.add_argument('-t', '--test_with_vector_tsv_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnr', '--rnr_load_model_file', required=True)
    parser.add_argument('-uv', '--uv_load_model_file', required=True)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["system_id"] = args.system_id
    filter_run["run_info"] = {
        "num_entities": len(entities),
    }

    # load global models
    clf_rnr_global = load_model(args.rnr_load_model_file)
    clf_uv_global = load_model(args.uv_load_model_file)
        
    recs = []

    x_train, y_train, train_context = create_data(args.train_with_vector_tsv_file)
    x_test, y_test, test_context = create_data(args.test_with_vector_tsv_file)

    
    # ---------------- R-NR classifier 

    x_train_rnr = {}
    y_train_rnr = {}
    for targetid in y_train:
        candidate_y = to_rnr(y_train[targetid])
        if len(set(candidate_y)) > 1:
            x_train_rnr[targetid] = x_train[targetid]
            y_train_rnr[targetid] = candidate_y

    y_test_rnr = {}
    for targetid in y_test:
        y_test_rnr[targetid] = to_rnr(y_test[targetid])

    for targetid in x_train_rnr:
        assert len(y_train_rnr[targetid][y_train_rnr[targetid] == -1]) == 0
        assert len(y_train_rnr[targetid][y_train_rnr[targetid] == 2]) == 0

    for targetid in x_test:
        assert y_test[targetid].shape[0] == len(test_context[targetid])
        assert y_test[targetid].shape == y_test_rnr[targetid].shape
        assert len(y_test_rnr[targetid][y_test_rnr[targetid] == -1]) == 0
        assert len(y_test_rnr[targetid][y_test_rnr[targetid] == 2]) == 0

    # learn a R-NR model for each entity that have at least two examples with different classes (relevant and non relevant)
    clf_rnrs = {}
    for targetid in x_train_rnr:
        clf_rnr = ensemble.GradientBoostingClassifier()
        clf_rnr = clf_rnr.fit(x_train_rnr[targetid], y_train_rnr[targetid])
        #feature_importance(clf_rnr.feature_importances_, 'R-NR for entity %s' % targetid)
        clf_rnrs[targetid] = clf_rnr
    
    
    # predicting R-NR
    pred_rnr_prob = {}
    pred_rnr = {}
    mismatch_predictions_rnr = 0
    global_rnr_pred = 0
    global_rnr_pred_no_entity = 0
    entity_rnr_pred = 0
    for targetid in x_test:
#        prob_entity = None
#        if clf_rnrs.has_key(targetid):
#            prob_entity = clf_rnrs[targetid].predict_proba(x_test[targetid])
        prob_global = clf_rnr_global.predict_proba(x_test[targetid])
#        if prob_entity == None:
        pred_rnr_prob[targetid] = prob_global
        pred_rnr[targetid] = np.array(map(np.argmax, prob_global))
        global_rnr_pred_no_entity += 1
#        else:
#            pred_rnr_prob[targetid], pred_rnr[targetid], mismatches, pred_global, pred_entity = get_prob_and_pred(prob_global, prob_entity)
#            mismatch_predictions_rnr += mismatches
#            global_rnr_pred += pred_global
#            entity_rnr_pred += pred_entity

    for targetid in y_test:
        for i, prob in enumerate(pred_rnr_prob[targetid]):
            if prob[0] >= prob[1]:
                recs.append(build_record(i, test_context[targetid], 0, prob[0]))

    for targetid in y_test:
        assert y_test_rnr[targetid].shape == pred_rnr[targetid].shape

    # -----------------------U-V classifier

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


    # learn a U-V model for each entity that have at least two examples with different classes (useful and vital)
    clf_uvs = {}
    for targetid in x_train_uv:
        clf_uv = ensemble.GradientBoostingClassifier()
        clf_uv = clf_uv.fit(x_train_uv[targetid], y_train_uv[targetid])
        #feature_importance(clf_uv.feature_importances_, 'U-V')
        clf_uvs[targetid] = clf_uv

    # predicting U-V
    pred_uv_prob = {}
    pred_uv = {}
    mismatch_predictions_uv = 0
    global_uv_pred = 0
    global_uv_pred_no_entity = 0
    entity_uv_pred = 0
    for targetid in x_test_uv:
        prob_entity = None
        if clf_uvs.has_key(targetid):
            prob_entity = clf_uvs[targetid].predict_proba(x_test_uv[targetid])
        prob_global = clf_uv_global.predict_proba(x_test_uv[targetid])
        if prob_entity == None:
            pred_uv_prob[targetid] = prob_global
            pred_uv[targetid] = np.array(map(np.argmax, prob_global))
            global_uv_pred_no_entity += 1
        else:
            pred_uv_prob[targetid], pred_uv[targetid], mismatches, global_pred, entity_pred = get_prob_and_pred(prob_global, prob_entity)
            mismatch_predictions_uv += mismatches
            global_uv_pred += global_pred
            entity_uv_pred += entity_pred

    for targetid in pred_uv:
        pred_uv[targetid] += 1
        for i, relevance in enumerate(pred_uv[targetid]):
            prob = max(pred_uv_prob[targetid][i])
            recs.append(build_record(idxs_context[targetid][i], test_context[targetid], relevance, prob))

    for targetid in y_test_uv:
        assert y_test_uv[targetid].shape == pred_uv[targetid].shape

    len_predictions = 0
    for targetid in y_test:
        len_predictions += len(y_test[targetid])

    assert len(recs) == len_predictions

    # some metrics
    print 'mismatches rnr %d' % mismatch_predictions_rnr
    print 'mismatches uv %d' % mismatch_predictions_uv
    print 'pred global rnr %d' % global_rnr_pred
    print 'pred global rnr no entity %d' % global_rnr_pred_no_entity
    print 'pred entity rnr %d' % entity_rnr_pred
    print 'pred global uv %d' % global_uv_pred
    print 'pred global uv no entity %d' % global_uv_pred_no_entity
    print 'pred entity uv %d' % entity_uv_pred

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
