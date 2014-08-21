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
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-c', '--context_test_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnr', '--rnr_save_model_file', required=False)
    parser.add_argument('-uv', '--uv_save_model_file', required=False)
    args = parser.parse_args()

    filter_run["system_id"] = args.system_id
    
    recs = []

    context = []
    unique_entities = {}
    with open(args.context_test_file) as f:
        for line in f.read().splitlines():
            context.append(line.strip())
            unique_entities[line.strip().split()[1]] = True

    filter_run["run_info"] = {
        "num_entities": len(unique_entities)
    }

    data_train = np.genfromtxt(args.training_file)
    x_train = data_train[:,1:]
    y_train = data_train[:,0]
    data_test = np.genfromtxt(args.test_file)
    x_test = data_test[:,1:]
    y_test = data_test[:,0]


    begin = time.time()

    y_train_rnr = to_rnr(y_train)
    y_test_rnr = to_rnr(y_test)

    assert y_test.shape[0] == len(context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_train_rnr[y_train_rnr == -1]) == 0
    assert len(y_train_rnr[y_train_rnr == 2]) == 0
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    print x_train.shape
    print y_train.shape

    clf_rnr = ensemble.GradientBoostingClassifier()
    clf_rnr = clf_rnr.fit(x_train, y_train_rnr)
    #feature_importance(clf_rnr.feature_importances_, 'R-NR')

    #save_model(args.rnr_save_model_file, clf_rnr)
    
    pred_rnr_prob = clf_rnr.predict_proba(x_test)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))

    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, context, 0, prob[0]))

    assert y_test_rnr.shape == pred_rnr.shape

    x_train_uv, y_train_uv = to_uv(x_train, y_train)
    x_test_uv, y_test_uv, idxs_context = to_uv_given_pred(x_test, y_test, pred_rnr)

    print x_train_uv.shape
    print x_test_uv.shape

    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])
    assert y_test_uv.shape[0] == len(idxs_context)

    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv, y_train_uv)
    #feature_importance(clf_uv.feature_importances_, 'U-V')

    #save_model(args.uv_save_model_file, clf_uv)

    pred_uv_prob = clf_uv.predict_proba(x_test_uv)
    pred_uv = np.array(map(np.argmax, pred_uv_prob))
    pred_uv += 1
    for i, relevance in enumerate(pred_uv):
        prob = max(pred_uv_prob[i])
        recs.append(build_record(idxs_context[i], context, relevance, prob))

    assert len(recs) == y_test.shape[0]
    assert y_test_uv.shape == pred_uv.shape


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
