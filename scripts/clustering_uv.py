#!/usr/bin/python
from __future__ import division
from utils import to_multitask, create_separate_global_data, filter_run, build_record, create_global_data, load_model
import re
import os
import sys
import json
import time
import argparse
import numpy as np
from sklearn import ensemble
from collections import defaultdict

def do_predict(clf_uv, x, cxt, idxs_entities, recs):
    entity_number = len(idxs_entities)
    orig_columns = x.shape[1]
    for i in xrange(x.shape[0]):
        targetid = cxt[i].split()[1]
        idx = idxs_entities[targetid]
        added_columns = np.zeros([orig_columns * entity_number])
        start = orig_columns * idx
        end = start + orig_columns
        added_columns[start:end] = x[i]
        new_x = np.hstack((x[i], added_columns))
        pred_uv_prob = clf_uv.predict_proba(new_x)[0]
        prob = max(pred_uv_prob)
        relevance = np.argmax(pred_uv_prob)
        relevance += 1
        recs.append(build_record(i, cxt, relevance, prob))

def add_nr_results(filename, recs, filter_run):
    print 'adding nr results...'
    nr_results = 0
    with open(filename) as f:
        for line in f.read().splitlines():
            nr_results += 1
            arr = [filter_run["team_id"], filter_run["system_id"]]
            without_quotes = []
            for e in line.split("\t"):
                without_quotes.append(e.replace("'", ""))
            arr.extend(without_quotes)
            recs.append(arr)
    print 'added %d nr results' % nr_results


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_relevant', required=True)
    parser.add_argument('-t', '--test_relevant', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)
    parser.add_argument('-nr', '--no_relevant_file', required=True)

    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))
    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id

    idxs_entities = {}
    for i, entity in enumerate(entities):
        idxs_entities[entity['target_id']] = i

    recs = []

    add_nr_results(args.no_relevant_file, recs, filter_run)

    begin = time.time()

    # read whole dataset
    print 'reading dataset'
    start = time.time()
    x_train_a_r, y_train_a_r, cxt_train_a_r, x_train_u_r, y_train_u_r, cxt_train_u_r = create_separate_global_data(args.train_relevant)
    x_test_r, y_test_r, cxt_test_r = create_global_data(args.test_relevant)
    elapsed = time.time() - start
    print 'dataset read, took %s' % elapsed

    print 'train assessed relevant %s' % str(x_train_a_r.shape)
    print 'train unassessed relevant %s' % str(x_train_u_r.shape)
    print 'test relevant %s' % str(x_test_r.shape)

    # RNR classifier
    clf_rnr = load_model(args.rnr_load_model_file)

    start = time.time()
    print 'to multitask x_train_a_r...'
    x_train_a_r_multitask = to_multitask(x_train_a_r, cxt_train_a_r, idxs_entities)
    elapsed = time.time() - start
    print 'finished to multitask, took %s' % elapsed

    print x_train_a_r_multitask.shape

    start = time.time()
    print 'training uv classifier...'
    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_a_r_multitask, y_train_a_r)
    elapsed = time.time() - start
    print 'finished training uv classifier, took %s' % elapsed

    start = time.time()
    print 'testing uv classifier...'
    do_predict(clf_uv, x_test_r, cxt_test_r, idxs_entities, recs)
    do_predict(clf_uv, x_train_u_r, cxt_train_u_r, idxs_entities, recs)
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    print len(recs)

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
  #np.set_printoptions(threshold=np.nan, linewidth=1000000000000000, )
  main()
