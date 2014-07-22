#!/usr/bin/python

import re
import os
import sys
import json
import time
import argparse
import numpy as np
from sklearn import ensemble
from sklearn import metrics
#import graphlab as gl


def to_rnr(y):
    y_rnr = np.array(y)
    for i, value in enumerate(y):
        if value == -1:
            y_rnr[i] = 0
        elif value == 2:
            y_rnr[i] = 1
    return y_rnr

def to_uv(x,y):
    idxs = y > 0
    count = sum(idxs)
    x_uv = np.zeros([count,x.shape[1]])
    y_uv = np.zeros([count])
    pos = 0
    for i, v in enumerate(idxs):
        if v:
            x_uv[pos] = x[i]
            y_uv[pos] = y[i]
            pos += 1
    return (x_uv, y_uv)


def to_uv_given_pred(x,y, pred_rnr):
# for the ones that I predicted 1, I should get the truth value
# if the truth is -1 or 0, I put them as useful? Or shouldn't I consider them
    idxs = pred_rnr == 1
    count = sum(idxs)
    x_uv = np.zeros([count,x.shape[1]])
    y_uv = np.zeros([count])
    pos = 0
    for i, v in enumerate(idxs):
        if v:
            x_uv[pos] = x[i]
            y_uv[pos] = y[i] if (y[i] == 1 or y[i] == 2) else 1
            pos += 1
    return (x_uv, y_uv)


def main():
 
    filter_run = {
        "$schema": "http://trec-kba.org/schemas/v1.1/filter-run.json",
        "task_id": "kba-ccr-2014",
        "topic_set_id": "kba-2014-ccr-and-ssf",
        "corpus_id": "kba-streamcorpus-2014-v0_3_0-kba-filtered",
        "team_id": "UW",
        "team_name": "University of Washington",
        "poc_name": "UW Baseline", 
        "poc_email": "icano@cs.washington.edu",
        "system_id": "baseline",
        "run_type": "automatic",
        "system_description": "Baseline with RF classifier using docs in train dataset.",
        "system_description_short": "doc and doc-entity features",
        }

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)
    parser.add_argument('-c', '--context_test_file', required=True)
    parser.add_argument('-s', '--ssf', required=False)
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }

    data_train = np.genfromtxt(args.training_file)
    x_train = data_train[:,1:]
    y_train = data_train[:,0]
    data_test = np.genfromtxt(args.test_file)
    x_test = data_test[:,1:]
    y_test = data_test[:,0]

    y_train_rnr = to_rnr(y_train)
    y_test_rnr = to_rnr(y_test)

    assert y_test.shape == y_test_rnr.shape
    assert len(y_train_rnr[y_train_rnr == -1]) == 0
    assert len(y_train_rnr[y_train_rnr == 2]) == 0
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    clf_rnr = ensemble.GradientBoostingClassifier()
    clf_rnr = clf_rnr.fit(x_train, y_train_rnr)
    pred_rnr = clf_rnr.predict(x_test)

    assert y_test_rnr.shape == pred_rnr.shape

    p_rnr_micro, r_rnr_micro, f1_rnr_micro, _ = metrics.precision_recall_fscore_support(y_test_rnr, pred_rnr,
                                                         average="micro")
    print 'RNR Micro:'
    print ' Precision %f' % p_rnr_micro
    print ' Recall %f' % r_rnr_micro
    print ' F1 %f' % f1_rnr_micro

    x_train_uv, y_train_uv = to_uv(x_train, y_train)
    x_test_uv, y_test_uv = to_uv_given_pred(x_test, y_test, pred_rnr)

    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])

    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_rnr.fit(x_train_uv, y_train_uv)

    pred_uv = clf_uv.predict(x_test_uv)

    assert y_test_uv.shape == pred_uv.shape

    p_uv_micro, r_uv_micro, f1_uv_micro, _ = metrics.precision_recall_fscore_support(y_test_uv, pred_uv,
                                                         average="micro")
    print 'UV Micro:'
    print ' Precision %f' % p_uv_micro
    print ' Recall %f' % r_uv_micro
    print ' F1 %f' % f1_uv_micro

    exit()


    start_time = time.time()
    num_entity_doc_compares = 0
    num_filter_results = 0
    num_docs = 0
    num_stream_hours = 0


    with open(args.context_test_file) as f:
        for line in f.read().splitlines():
            pass


    '''
                    ## run a filter algorithm
                    confidence, relevance, contains_mention = \
                        scorer.assess_target(entity_repr)
                    num_entity_doc_compares += 1

                    if confidence > args.cutoff:
                        ## assemble line in the format specified on
                        ## http://trec-kba.org/trec-kba-2013.shtml#submissions
                        ccr_rec = [
                            ## sytem identifier
                            filter_run["team_id"], filter_run["system_id"], 
                                
                            ## this task identifier
                            si.stream_id, target_id, 

                            ## algorithm output:
                            confidence, relevance, contains_mention,

                            ## identify the directory containing this chunk file
                            date_hour, 

                            ## default values for SSF run
                            "NULL", -1, "0-0",
                            ]

                        if not args.ssf:
                            ## use only the CCR record
                            recs = [ccr_rec]

                        else:
                            ## instead of the CCR record, generate SSF records
                            recs = []

                            if relevance == 2:
                                ## on "vital" ranked docs, attempt Streaming
                                ## Slot Filling (SSF)
                                for row in scorer.fill_slots(entity_repr):

                                    ## these fields differ from the base CCR record:
                                    ssf_conf, slot_name, slot_equiv_id, byte_range = row

                                    ## copy CCR record and insert SSF-specific fields:
                                    ssf_rec = copy.deepcopy(ccr_rec)
                                    ssf_rec[4]  = ssf_conf
                                    ssf_rec[8]  = slot_name
                                    ssf_rec[9]  = slot_equiv_id
                                    ssf_rec[10] = byte_range

                                    recs.append(ssf_rec)

                        for rec in recs:
                            assert len(rec) == 11

                            output.write("\t".join(map(str, rec)) + "\n")

                            ## keep count of how many we have save total
                            num_filter_results += 1

                ## print some speed info every 100 entities
                if num_docs % 100 == 0:
                    elapsed = time.time() - start_time
                    doc_rate = float(num_docs) / elapsed
                    scoring_rate = float(num_entity_doc_compares) / elapsed
                    logger.info("%d docs, %d scorings in %.1f --> %.3f docs/sec, %.3f compute_relevance/sec" % (
                            num_docs, num_entity_doc_compares, elapsed, doc_rate, scoring_rate))
    '''

    output = open(args.output_file, "w")


    filter_run["run_info"]["elapsed_time"] = time.time() - start_time

    if args.ssf:
        filter_run["task_id"] = "kba-ssf-2014"

    filter_run_json_string = json.dumps(filter_run, indent=4, sort_keys=True)
    filter_run_json_string = re.sub("\n", "\n#", filter_run_json_string)
    output.write("#%s\n" % filter_run_json_string)
    output.close()

    print "# done!"

if __name__ == '__main__':
  np.set_printoptions(threshold=np.nan)
  main()
