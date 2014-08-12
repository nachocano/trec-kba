#!/usr/bin/python
from utils import to_rnr, to_uv_multitask, to_uv_given_pred_multitask, feature_importance, filter_run, build_record, load_model, create_global_data, get_prob_and_pred
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
    parser.add_argument('-rnr', '--rnr_load_model_file', required=True)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    idxs_entities = {}
    for i, entity in enumerate(entities):
        idxs_entities[entity['target_id']] = i

    filter_run["system_id"] = args.system_id
    filter_run["run_info"] = {
        "num_entities": len(entities),
    }

    # load global models
    clf_rnr_global = load_model(args.rnr_load_model_file)
        
    recs = []

    x_train, y_train, train_context = create_global_data(args.train_with_vector_tsv_file)
    x_test, y_test, test_context = create_global_data(args.test_with_vector_tsv_file)

    
    # ---------------- R-NR classifier 

    pred_rnr_prob = clf_rnr_global.predict_proba(x_test)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))

    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, test_context, 0, prob[0]))

    assert y_test.shape == pred_rnr.shape

    # --------------- U-V classifier

    x_train_uv, y_train_uv = to_uv_multitask(x_train, y_train, train_context, idxs_entities)
    x_test_uv, y_test_uv, idxs_context = to_uv_given_pred_multitask(x_test, y_test, pred_rnr, test_context, idxs_entities)

    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])
    assert y_test_uv.shape[0] == len(idxs_context)

    print 'training uv...'
    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv, y_train_uv)
    print 'trained uv...'
    #feature_importance(clf_uv.feature_importances_, 'U-V')

    print 'testing uv...'
    pred_uv_prob = clf_uv.predict_proba(x_test_uv)
    pred_uv = np.array(map(np.argmax, pred_uv_prob))
    print 'tested uv...'
    
    pred_uv += 1
    for i, relevance in enumerate(pred_uv):
        prob = max(pred_uv_prob[i])
        recs.append(build_record(idxs_context[i], test_context, relevance, prob))

    assert len(recs) == y_test.shape[0]
    assert y_test_uv.shape == pred_uv.shape

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
