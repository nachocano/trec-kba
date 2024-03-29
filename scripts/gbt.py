#!/usr/bin/python
from utils import do_predict_rnr, do_predict_uv, create_separate_global_data, to_rnr, to_uv, to_uv_given_pred, filter_run, build_record, save_model, load_model, to_rnr_multitask
import json
import time
import re
import argparse
import numpy as np
from sklearn import ensemble

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)
    parser.add_argument('-rnrs', '--rnr_save_model_file', required=False)

    args = parser.parse_args()

    filter_run["system_id"] = args.system_id
    
    recs = []

    filter_topics = json.load(open(args.entities_json))
    
    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    entities_idxs = {}
    for i, entity in enumerate(entities):
        entities_idxs[entity['target_id']] = i


    # reading data
    print 'reading data'
    x_train_a, y_train_a, cxt_train_a, _, _, _ = create_separate_global_data(args.training_file)
    #x_test_a, y_test_a, cxt_test_a, x_test_u, y_test_u, cxt_test_u = create_separate_global_data(args.test_file)
    print 'read data'

    filter_run["run_info"] = {
        "num_entities": 71
    }

    print x_train_a.shape
    x_train_a = to_rnr_multitask(x_train_a, cxt_train_a, entities_idxs)
    print x_train_a.shape

    begin = time.time()

    y_train_a_rnr = to_rnr(y_train_a)

    assert y_train_a.shape == y_train_a_rnr.shape
    assert len(y_train_a_rnr[y_train_a_rnr == -1]) == 0
    assert len(y_train_a_rnr[y_train_a_rnr == 2]) == 0

    print x_train_a.shape
    #print x_test_a.shape
    #print x_train_u.shape
    #print x_test_u.shape

    estimators = 150
    random_seed = 37
    max_depth = 110

    clf_rnr = None
    if args.rnr_load_model_file:
        clf_rnr = load_model(args.rnr_load_model_file)
    else:
        print 'in here'
        clf_rnr = ensemble.ExtraTreesClassifier(n_estimators=estimators, max_depth=max_depth, random_state=random_seed)
        clf_rnr = clf_rnr.fit(x_train_a, y_train_a_rnr)
        if args.rnr_save_model_file:
            save_model(args.rnr_save_model_file, clf_rnr)
        exit()
    
    # predict R-NR
    pred_rnr_a = do_predict_rnr(clf_rnr, x_test_a, cxt_test_a, recs)
    pred_rnr_u_from_train = do_predict_rnr(clf_rnr, x_train_u, cxt_train_u, recs)
    pred_rnr_u = do_predict_rnr(clf_rnr, x_test_u, cxt_test_u, recs)

    assert y_test_a.shape == pred_rnr_a.shape
    assert y_train_u.shape == pred_rnr_u_from_train.shape
    assert y_test_u.shape == pred_rnr_u.shape


    # build training for uv
    x_train_a_uv, y_train_a_uv = to_uv(x_train_a, y_train_a)

    # build test for uv
    # assessed predicted relevant
    x_test_a_uv, idxs_cxt_test_a_uv = to_uv_given_pred(x_test_a, pred_rnr_a)
    # unassessed of the training predicted relevant
    x_test_u_uv_from_train, idxs_cxt_test_u_uv_from_train = to_uv_given_pred(x_train_u, pred_rnr_u_from_train)
    # and the unassessed of the test predicted relevant
    x_test_u_uv, idxs_cxt_test_u_uv = to_uv_given_pred(x_test_u, pred_rnr_u)

    print x_train_a_uv.shape
    print x_test_a_uv.shape
    print x_test_u_uv_from_train.shape
    print x_test_u_uv.shape

    assert x_test_a_uv.shape[0] == len(pred_rnr_a[pred_rnr_a == 1])
    assert x_test_u_uv_from_train.shape[0] == len(pred_rnr_u_from_train[pred_rnr_u_from_train == 1])
    assert x_test_u_uv.shape[0] == len(pred_rnr_u[pred_rnr_u == 1])

    clf_uv = ensemble.ExtraTreesClassifier(n_estimators=estimators, max_depth=max_depth, random_state=random_seed)
    clf_uv = clf_uv.fit(x_train_a_uv, y_train_a_uv)


    # predict U-V
    pred_uv_a = do_predict_uv(clf_uv, x_test_a_uv, cxt_test_a, recs, idxs_cxt_test_a_uv)
    pred_uv_u_from_train = do_predict_uv(clf_uv, x_test_u_uv_from_train, cxt_train_u, recs, idxs_cxt_test_u_uv_from_train)
    pred_uv_u = do_predict_uv(clf_uv, x_test_u_uv, cxt_test_u, recs, idxs_cxt_test_u_uv)


    assert len(recs) == x_test_a.shape[0] + x_test_u.shape[0] + x_train_u.shape[0]

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
