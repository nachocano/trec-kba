#!/usr/bin/python
from __future__ import division
from utils import do_predict_rnr, do_predict_rnr_from_train_u, UNASSESSED_LABEL, filter_run, build_record, create_global_data, load_model, to_multitask_single
from cluster_helper import update_clusters, build_init_clusters_centroids
import re
import os
import sys
import json
import time
import argparse
import numpy as np
from sklearn import ensemble
from collections import defaultdict
from target import Target, InitCluster, Stream


def do_predict_train(clf_uv, train, train_context, idxs_entities, recs):
    left = len(train)
    for idx in train:
        left -= 1
        print 'more testing, %s left' % left
        _, targetid, _ = train_context[idx].split()
        x_multitask = to_multitask_single(train[idx][0], targetid, idxs_entities)
        to_test = np.hstack((x_multitask, [train[idx][1], train[idx][2], train[idx][3], train[idx][4], train[idx][5], train[idx][6], train[idx][7], train[idx][8]]))
        pred_uv_prob = clf_uv.predict_proba(to_test)[0]
        prob = max(pred_uv_prob)
        relevance = np.argmax(pred_uv_prob)
        relevance += 1
        recs.append(build_record(idx, train_context, relevance, prob))        

def do_predict_test(clf_uv, x_test, y_test, relevant_idxes_au_test, test_context, idxs_entities, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, recs):
    nr_examples = len(relevant_idxes_au_test)
    left = nr_examples
    for i in xrange(nr_examples):
        left -= 1
        print 'testing, %s left' % left
        idx = relevant_idxes_au_test[i]
        streamid, targetid, date_hour = test_context[idx].split()
        example = x_test[idx][25:]
        # update the clusters for all of the examples
        min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, \
        min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = \
            update_clusters(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, None)
        x_multitask = to_multitask_single(x_test[idx], targetid, idxs_entities)
        to_test = np.hstack((x_multitask, [min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb]))
        pred_uv_prob = clf_uv.predict_proba(to_test)[0]
        prob = max(pred_uv_prob)
        relevance = np.argmax(pred_uv_prob)
        relevance += 1
        recs.append(build_record(idx, test_context, relevance, prob))
    

def build_train(x_train, y_train, train_context, delimiter, relevant_idxes_au_train, idxs_entities, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease):
    x_train_a = []
    y_train_a = []
    x_train_u = {}
    nr_examples = len(relevant_idxes_au_train) - delimiter
    left = nr_examples
    for i in xrange(nr_examples):
        left -= 1
        print 'build training, %s left' % left
        idx = relevant_idxes_au_train[i+delimiter]
        streamid, targetid, date_hour = train_context[idx].split()
        example = x_train[idx][25:]
        # update the clusters for all of the examples
        min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, \
        min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = \
            update_clusters(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, None)
        if y_train[idx] != UNASSESSED_LABEL:
            # only train the GBT with the annotated relevant stuff
            x_multitask = to_multitask_single(x_train[idx], targetid, idxs_entities)
            x_train_a.append(np.hstack((x_multitask, [min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb])))
            y_train_a.append(y_train[idx])
        else:
            # save the x_train unassessed to predict on it
            x_train_u[idx] = (x_train[idx], min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb)

    return np.array(x_train_a), np.array(y_train_a), x_train_u
    

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_sorted', required=True)
    parser.add_argument('-t', '--test_sorted', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-av', '--alpha_verb', required=True, type=float)
    parser.add_argument('-an', '--alpha_noun', required=True, type=float)
    parser.add_argument('-gvi', '--gamma_verb_increase', required=True, type=float)
    parser.add_argument('-gvd', '--gamma_verb_decrease', required=True, type=float)
    parser.add_argument('-gni', '--gamma_noun_increase', required=True, type=float)
    parser.add_argument('-gnd', '--gamma_noun_decrease', required=True, type=float)
    parser.add_argument('-c', '--clusters_folder', required=True)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)
    parser.add_argument('-s', '--pre_train_split', required=False, type=float, default=0.2)

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

    begin = time.time()

    # read whole dataset
    print 'reading dataset'
    start = time.time()
    x_train, y_train, train_context = create_global_data(args.train_sorted)
    x_test, y_test, test_context = create_global_data(args.test_sorted)
    elapsed = time.time() - start
    print 'dataset read, took %s' % elapsed

    print x_train.shape
    print x_test.shape

    # RNR classifier
    clf_rnr = load_model(args.rnr_load_model_file)

    print 'predicting rnr'
    start = time.time()
    # predict in all assessed and unassessed test data...
    relevant_idxes_au_test = do_predict_rnr(clf_rnr, x_test[:,:25], test_context, recs, True)
    # predict in train unassessed
    relevant_idxes_u_train = do_predict_rnr_from_train_u(clf_rnr, x_train, y_train, train_context, recs)
    # get the relevant train assessed
    relevant_idxes_a_train = np.where(y_train > 0)[0]

    print 'relevant test %s' % len(relevant_idxes_au_test)
    print 'relevant train a %s' % len(relevant_idxes_a_train)
    print 'relevant train u %s' % len(relevant_idxes_u_train)

    relevant_idxes_au_train = relevant_idxes_a_train + relevant_idxes_u_train
    relevant_idxes_au_train.sort()

    rows = len(relevant_idxes_au_train)
    pre_train_delimiter = int(rows * args.pre_train_split)

    centroids = {}
    centroids['nouns'] = defaultdict(lambda: defaultdict(defaultdict))
    centroids['verbs'] = defaultdict(lambda: defaultdict(defaultdict))
    cluster_elements = {}
    cluster_elements['nouns'] = defaultdict(lambda: defaultdict(list))
    cluster_elements['verbs'] = defaultdict(lambda: defaultdict(list))
    stream_info = {}
    stream_info['nouns'] = defaultdict(lambda: defaultdict(list))
    stream_info['verbs'] = defaultdict(lambda: defaultdict(list))
    cluster_names = {}
    cluster_names['nouns'] = defaultdict(lambda: 1)
    cluster_names['verbs'] = defaultdict(lambda: 1)
    cluster_timeliness = {}
    cluster_timeliness['nouns'] = defaultdict(lambda: defaultdict(int))
    cluster_timeliness['verbs'] = defaultdict(lambda: defaultdict(int))
    init_clusters_centroids = {}
    init_clusters_centroids['nouns'] = defaultdict(lambda: defaultdict(defaultdict))
    init_clusters_centroids['verbs'] = defaultdict(lambda: defaultdict(defaultdict))
    init_clusters_info = {}
    init_clusters_info['nouns'] = defaultdict(lambda: defaultdict(list))
    init_clusters_info['verbs'] = defaultdict(lambda: defaultdict(list))

    start = time.time()
    print 'pre training clusters with %s examples, %s of the training' % (pre_train_delimiter, args.pre_train_split)
    pre_train_u = {}
    for i in xrange(pre_train_delimiter):
        idx = train_context[rel_idxes_au_train[i]]
        streamid, targetid, date_hour = train_context[idx].split()
        example = x_train[idx][25:]
        min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, \
        min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = \
            update_clusters(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, args.alpha_noun, args.alpha_verb, args.gamma_noun_increase, args.gamma_noun_decrease, args.gamma_verb_increase, args.gamma_verb_decrease, init_clusters_info)
        if y_train[idx] == UNASSESSED_LABEL:
            pre_train_u[idx] = (x_train[idx], min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb)
    elapsed = time.time() - start
    print 'pre trained examples unassessed %s' % len(pre_train_u)
    print 'finished pre training uv classifier, took %s' % elapsed

    print 'adding centroids to init_clusters'
    #build_init_clusters_centroids(init_clusters_info, init_clusters_centroids, centroids)
    print 'finished adding centroids to init_clusters'

    start = time.time()
    print 'building training for uv classifier...'
    x_train_a_uv, y_train_a_uv, x_train_u_uv = build_train(x_train, y_train, train_context, pre_train_delimiter, relevant_idxes_au_train, idxs_entities, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun_increase, args.gamma_noun_decrease, args.gamma_verb_increase, args.gamma_verb_decrease)
    elapsed = time.time() - start
    print 'finished building training for uv classifier, took %s' % elapsed

    assert x_train_a_uv.shape[0] == y_train_a_uv.shape[0]
    assert len(y_train_a_uv[y_train_a_uv == -1]) == 0
    assert len(y_train_a_uv[y_train_a_uv == 0]) == 0
    assert len(y_train_a_uv[y_train_a_uv == -10]) == 0

    start = time.time()
    print 'training on uv classifier...'
    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_a_uv, y_train_a_uv)
    elapsed = time.time() - start
    print 'finished training on uv classifier, took %s' % elapsed

    start = time.time()
    print 'testing on uv classifier...'
    do_predict_test(clf_uv, x_test, y_test, relevant_idxes_au_test, test_context, idxs_entities, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun_increase, args.gamma_noun_decrease, args.gamma_verb_increase, args.gamma_verb_decrease, recs)
    do_predict_train(clf_uv, pre_train_u, train_context, idxs_entities, recs)
    do_predict_train(clf_uv, x_train_u_uv, train_context, idxs_entities, recs)
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    print len(recs)
    print (x_test.shape[0] + len(relevant_idxes_u_train))
    #assert len(recs) == x_test.shape[0] + len(relevant_idxes_u_train)

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

    #print 'building targets ...'
    #start = time.time()
    #noun_targets = build_targets('nouns', centroids, init_clusters_centroids, init_clusters_info, stream_info, predictions, truths)
    #verb_targets = build_targets('verbs', centroids, init_clusters_centroids, init_clusters_info, stream_info, predictions, truths)
    #print 'finished building targets, took %s' % (time.time() - start)

    #clusters_noun_file = open(os.path.join(args.clusters_folder, 'nouns_%s' % args.alpha_noun), 'w')
    #clusters_noun_file.write('targets : [ %s ]' % (','.join(str(t) for t in noun_targets)))
    #clusters_noun_file.close()

    #clusters_verbs_file = open(os.path.join(args.clusters_folder, 'verbs_%s' % args.alpha_verb), 'w')
    #clusters_verbs_file.write('targets : [ %s ]' % (','.join(str(t) for t in verb_targets)))
    #clusters_verbs_file.close()

    #print 'noun clusters %s' % stats('nouns', centroids)
    #print 'verb clusters %s' % stats('verbs', centroids)

def stats(word_type, centroids):
    count = 0
    for targetid in centroids[word_type]:
        count += len(centroids[word_type][targetid])
    return count

def build_targets(word_type, centroids, init_clusters_centroids, init_clusters_info, stream_info, predictions, truths):
    targets = []
    for targetid in centroids[word_type]:
        target = Target(targetid)
        for cluster in init_clusters_centroids[word_type][targetid]:
            init_cluster = InitCluster(cluster, init_clusters_centroids[word_type][targetid][cluster], init_clusters_info[word_type][targetid][cluster])
            target.add_init_cluster(init_cluster)
        for cluster in stream_info[word_type][targetid]:
            for (streamid, date_hour, timeliness, min_distance, avg_distance, vector, current_centroid) in stream_info[word_type][targetid][cluster]:
                key = (streamid, targetid)
                stream = Stream(streamid, cluster, vector, current_centroid, timeliness, min_distance, avg_distance, predictions[key] if predictions.has_key(key) else None, truths[key] if truths.has_key(key) else None)
                target.add_stream(stream)
        targets.append(target)
    return targets


if __name__ == '__main__':
  #np.set_printoptions(threshold=np.nan, linewidth=1000000000000000, )
  main()
