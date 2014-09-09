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
from copy import deepcopy

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

    estimator = 150
    random_seed = 37

    max_depths = [3, 6, 10, 20]
    subsamples = [0.3, 0.5, 0.7, 1]
    subsamples_names = [03,05,07,1]
    learning_rates = [0.1, 0.3, 0.5]
    learning_rates_names = [01, 03, 05]

    for max_depth in max_depths:
        for subsample, subsample_name in zip(subsamples, subsamples_names):
            for l_rate, l_rate_name in zip(learning_rates, learning_rates_names):
                filter_run["system_id"] = '%s_%s_%s_%s' % (args.system_id, max_depth, subsample_name, l_rate_name)

                newrecs = deepcopy(recs)

                start = time.time()
                print 'training uv classifier with max_depth %s, subsample %s and learn rate %s' % (max_depth, subsample, l_rate)
                clf_uv = ensemble.GradientBoostingClassifier(n_estimators=estimator, max_depth=max_depth, learning_rate=l_rate, random_state=random_seed)
                clf_uv = clf_uv.fit(x_train_a_r_multitask, y_train_a_r)
                elapsed = time.time() - start
                print 'finished training uv classifier with max_depth %s, subsample %s and learn rate %s, took %s' % (max_depth, subsample, l_rate, elapsed) 

                start = time.time()
                print 'testing uv classifier with max_depth %s, subsample %s and learn rate %s' % (max_depth, subsample, l_rate)
                #do_predict(clf_uv, x_train_a_r, cxt_train_a_r, idxs_entities, recs)
                do_predict(clf_uv, x_test_r, cxt_test_r, idxs_entities, newrecs)
                do_predict(clf_uv, x_train_u_r, cxt_train_u_r, idxs_entities, newrecs)
                elapsed = time.time() - start
                print 'finished testing uv classifier with max_depth %s, subsample %s and learn rate %s, took %s' % (max_depth, subsample, l_rate, elapsed) 

                # generate output
                out_file = '%s_%s_%s_%s' % (args.output_file, max_depth, subsample_name, l_rate_name)
                output = open(out_file, "w")
                filter_run_json_string = json.dumps(filter_run)
                output.write("#%s\n" % filter_run_json_string)

                for rec in newrecs:
                    output.write("\t".join(map(str, rec)) + "\n")


                filter_run["run_info"]["num_filter_results"] = len(newrecs)
                filter_run_json_string = json.dumps(filter_run, indent=4, sort_keys=True)
                filter_run_json_string = re.sub("\n", "\n#", filter_run_json_string)
                output.write("#%s\n" % filter_run_json_string)
                output.close()
    
    elapsed_run = time.time() - begin
    print 'all run took %s' % elapsed_run



if __name__ == '__main__':
  #np.set_printoptions(threshold=np.nan, linewidth=1000000000000000, )
  main()
