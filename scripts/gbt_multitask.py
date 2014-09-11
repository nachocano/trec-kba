#!/usr/bin/python
from utils import do_predict_rnr, do_predict_uv, to_uv_multitask, filter_run, build_record, load_model, create_separate_global_data
import re
import json
import time
import argparse
import numpy as np
from sklearn import ensemble

def do_predict_uv_multitask(clf_uv, entities_idxs, cxt, x, recs, pred_rnr=None):
    if pred_rnr != None:
        idxs = np.where(pred_rnr == 1)[0]
        print len(idxs)
    else:
        idxs = np.arange(x.shape[0]).tolist()
    entity_number = len(entities_idxs)
    for v in idxs:
        targetid = cxt[v].split()[1]
        index = entities_idxs[targetid]
        orig_columns = x.shape[1]
        added_columns = np.zeros([orig_columns * entity_number])
        start = orig_columns * index
        end = start + orig_columns
        added_columns[start:end] = x[v]
        x_uv = np.hstack((x[v], added_columns))
        pred_uv_prob = clf_uv.predict_proba(x_uv)[0]
        prob = max(pred_uv_prob)
        relevance = np.argmax(pred_uv_prob)
        relevance += 1
        recs.append(build_record(v, cxt, relevance, prob))

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=True)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))
    
    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities)
    }

    entities_idxs = {}
    for i, entity in enumerate(entities):
        entities_idxs[entity['target_id']] = i

    filter_run["system_id"] = args.system_id

    recs = []

    
    x_train_a, y_train_a, cxt_train_a, x_train_u, y_train_u, cxt_train_u = create_separate_global_data(args.training_file)
    x_test_a, y_test_a, cxt_test_a, x_test_u, y_test_u, cxt_test_u = create_separate_global_data(args.test_file)

    print x_train_a.shape
    print x_test_a.shape
    print x_train_u.shape
    print x_test_u.shape

    # ---------------- R-NR classifier 

    begin = time.time()

    # load rnr basic model
    clf_rnr = load_model(args.rnr_load_model_file)
    # test r-nr
    pred_rnr_a = do_predict_rnr(clf_rnr, x_test_a[:,:25], cxt_test_a, recs)
    pred_rnr_u_from_train = do_predict_rnr(clf_rnr, x_train_u[:,:25], cxt_train_u, recs)
    pred_rnr_u = do_predict_rnr(clf_rnr, x_test_u[:,:25], cxt_test_u, recs)


    # --------------- U-V classifier

    x_train_a_uv, y_train_a_uv = to_uv_multitask(x_train_a, y_train_a, cxt_train_a, entities_idxs)
    
    print x_train_a_uv.shape

    estimators = 150
    random_seed = 37
    max_depth = 110

    # train uv
    print 'training uv...'
    start = time.time()
    clf_uv = ensemble.ExtraTreesClassifier(n_estimators=estimators, max_depth=max_depth, random_state=random_seed)
    clf_uv = clf_uv.fit(x_train_a_uv, y_train_a_uv)
    print 'trained uv, took %s' % (time.time() - start)

    # predict uv

    do_predict_uv_multitask(clf_uv, entities_idxs, cxt_test_a, x_test_a, recs, pred_rnr_a)
    do_predict_uv_multitask(clf_uv, entities_idxs, cxt_train_u, x_train_u, recs, pred_rnr_u_from_train)
    do_predict_uv_multitask(clf_uv, entities_idxs, cxt_test_u, x_test_u, recs, pred_rnr_u)


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
