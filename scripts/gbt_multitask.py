#!/usr/bin/python
from utils import to_rnr, to_uv_multitask, to_rnr_multitask, feature_importance, filter_run, build_record, load_model, create_global_data, get_prob_and_pred, save_model
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
    parser.add_argument('-tr', '--train_ass_unass_sorted_tsv', required=True)
    parser.add_argument('-t', '--test_ass_unass_sorted_tsv', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnrs', '--rnr_save_model_file', required=False)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    idxs_entities = {}
    for i, entity in enumerate(entities):
        idxs_entities[entity['target_id']] = i

    filter_run["system_id"] = args.system_id

    recs = []

    x_train, y_train, train_context = create_global_data(args.train_ass_unass_sorted_tsv)
    x_test, y_test, test_context = create_global_data(args.test_ass_unass_sorted_tsv)

    print x_train.shape
    print x_test.shape

    unique_entities = {}
    for value in test_context:
        targetid = value.split()[1]
        unique_entities[targetid] = True

    filter_run["run_info"] = {
        "num_entities": len(unique_entities)
    }

    # ---------------- R-NR classifier 

    begin = time.time()

    clf_rnr = None
    if args.rnr_load_model_file:
        clf_rnr = load_model(args.rnr_load_model_file)
    else:
        # train without multitask
        y_train_rnr = to_rnr(y_train)
        clf_rnr = ensemble.GradientBoostingClassifier()
        start = time.time()
        print 'training rnr classifier...'
        clf_rnr = clf_rnr.fit(x_train, y_train_rnr)
        if args.rnr_save_model_file:
            save_model(args.rnr_save_model_file, clf_rnr)
        elapsed = time.time() - start
        print 'finished training rnr classifier, took %s' % elapsed

    y_test_rnr = to_rnr(y_test)
    print y_test_rnr.shape

    print 'testing rnr'
    pred_rnr_prob = clf_rnr.predict_proba(x_test)
    print 'rnr tested'
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))

    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, test_context, 0, prob[0]))

    assert y_test.shape == pred_rnr.shape

    # --------------- U-V classifier

    x_train_uv, y_train_uv = to_uv_multitask(x_train, y_train, train_context, idxs_entities)
    
    print x_train_uv.shape

    print 'training uv...'
    start = time.time()
    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv, y_train_uv)
    print 'trained uv, took %s' % (time.time() - start)

    idxs = np.where(pred_rnr == 1)[0]
    entity_number = len(idxs_entities)
    print 'testing uv...'
    start = time.time()
    for v in idxs:
        targetid = test_context[v].split()[1]
        index = idxs_entities[targetid]
        orig_columns = x_test.shape[1]
        added_columns = np.zeros([orig_columns * entity_number])
        start = orig_columns * index
        end = start + orig_columns
        added_columns[start:end] = x_test[v]
        x_test_uv = np.hstack((x_test[v], added_columns))
        pred_uv_prob = clf_uv.predict_proba(x_test_uv)[0]
        prob = max(pred_uv_prob)
        relevance = np.argmax(pred_uv_prob)
        relevance += 1
        recs.append(build_record(v, test_context, relevance, prob))
    elapsed = time.time() - start
    print 'test uv, took %s' % elapsed

    elapsed_run = time.time() - begin
    print 'all run took %s' % elapsed_run

    # generate output
    output = open(args.output_file, "w")
    filter_run_json_string = json.dumps(filter_run)
    output.write("#%s\n" % filter_run_json_string)

    for rec in recs:
        output.write("\t".join(map(str, rec)) + "\n")

    filter_run["run_info"]["elapsed_time"] = elapsed_run
    filter_run["run_info"]["num_filter_results"] = len(recs)
    filter_run_json_string = json.dumps(filter_run, indent=4, sort_keys=True)
    filter_run_json_string = re.sub("\n", "\n#", filter_run_json_string)
    output.write("#%s\n" % filter_run_json_string)

    output.close()

if __name__ == '__main__':
  np.set_printoptions(threshold=np.nan)
  main()
