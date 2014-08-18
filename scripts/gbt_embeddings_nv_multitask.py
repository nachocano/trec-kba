#!/usr/bin/python
from __future__ import division
from utils import to_rnr, to_uv_multitask, to_uv_given_pred_multitask, feature_importance, filter_run, build_record, create_global_data, build_record, load_model, save_model, to_rnr_multitask
import re
import os
import sys
import json
import time
import argparse
import numpy as np
from sklearn import ensemble
from sklearn import metrics
from scipy.spatial.distance import euclidean
from collections import defaultdict
from gensim import matutils
import operator

max_timeliness =  100
min_timeliness = -100

def decrease_timeliness_except(cluster_timeliness, cluster_name, gamma):
    for cluster in cluster_timeliness:
        if cluster != cluster_name:
            cluster_timeliness[cluster] = max(cluster_timeliness[cluster] - gamma, min_timeliness)

def new_features_per_type(targetid, streamid, date_hour, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, example, cluster_names, alpha, gamma):
    
    min_distance = 0
    avg_distance = 0
    all_zeros = 0
    timeliness = 0

    if np.all(example == 0):
        if not centroids[targetid].has_key(0):
            cluster_timeliness[targetid][0] += (1/gamma)
        else:
            cluster_timeliness[targetid][0] = min(cluster_timeliness[targetid][0] + (1/gamma), max_timeliness)
        decrease_timeliness_except(cluster_timeliness[targetid], 0, gamma)
        cluster_elements[targetid][0].append(example)
        cluster_elements_info[targetid][0].append((streamid, date_hour, list(example)))
        examples = np.array(cluster_elements[targetid][0])
        centroids[targetid][0] = matutils.unitvec(examples.mean(axis=0)).astype(np.float32)
        all_zeros = 1
        timeliness = cluster_timeliness[targetid][0]
    else:
        if not centroids.has_key(targetid):
            # new cluster, add the example as the centroids for both nouns and verbs
            # update the cluster_name counter
            cluster_name = cluster_names[targetid]
            cluster_timeliness[targetid][cluster_name] += (1/gamma)
            centroids[targetid][cluster_name] = example
            cluster_elements[targetid][cluster_name].append(example)
            cluster_elements_info[targetid][cluster_name].append((streamid, date_hour, list(example)))
            timeliness = cluster_timeliness[targetid][cluster_name]
            cluster_names[targetid] += 1
        else:
            similarities = []
            similarities_sum = 0
            for cluster in centroids[targetid]:
                similarity = np.dot(centroids[targetid][cluster], example)
                similarities.append((cluster, similarity))
                similarities_sum += similarity
        
            maximum_tuple = max(tuple(r[::-1]) for r in similarities)[::-1]
            candidate_cluster_name = maximum_tuple[0]
            max_similarity = float(maximum_tuple[1])
        
            # two new features
            min_distance = abs(1 - max_similarity)
            avg_distance = abs(1 - (similarities_sum / len(similarities)))

            if min_distance < alpha:
                # put in an already existent cluster
                cluster_timeliness[targetid][candidate_cluster_name] = min(cluster_timeliness[targetid][candidate_cluster_name] + (1/gamma), max_timeliness)
                decrease_timeliness_except(cluster_timeliness[targetid], candidate_cluster_name, gamma)
                cluster_elements[targetid][candidate_cluster_name].append(example)
                cluster_elements_info[targetid][candidate_cluster_name].append((streamid, date_hour, list(example)))
                # update the centroid for that cluster
                examples = np.array(cluster_elements[targetid][candidate_cluster_name])
                centroids[targetid][candidate_cluster_name] = matutils.unitvec(examples.mean(axis=0)).astype(np.float32)
                timeliness = cluster_timeliness[targetid][candidate_cluster_name]
            else:
                # create a new cluster, add the example as the centroid
                cluster_name = cluster_names[targetid]
                cluster_timeliness[targetid][cluster_name] = min(cluster_timeliness[targetid][cluster_name] + (1/gamma), max_timeliness)
                decrease_timeliness_except(cluster_timeliness[targetid], cluster_name, gamma)
                centroids[targetid][cluster_name] = example
                cluster_elements[targetid][cluster_name].append(example)
                cluster_elements_info[targetid][cluster_name].append((streamid, date_hour, list(example)))
                timeliness = cluster_timeliness[targetid][cluster_name]
                cluster_names[targetid] += 1
    return (min_distance, avg_distance, all_zeros, timeliness)


def compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, example, cluster_names, alpha_noun, alpha_verb, gamma_noun, gamma_verb):
    
    nouns = example[:300]
    verbs = example[300:]

    min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun = new_features_per_type(targetid, streamid, date_hour, centroids['nouns'], cluster_elements['nouns'], cluster_elements_info['nouns'], cluster_timeliness['nouns'], nouns, cluster_names['nouns'], alpha_noun, gamma_noun)
    min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = new_features_per_type(targetid, streamid, date_hour, centroids['verbs'], cluster_elements['verbs'], cluster_elements_info['verbs'], cluster_timeliness['verbs'], verbs, cluster_names['verbs'], alpha_verb, gamma_verb)
    return min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb


def get_features(x_uv, uv_idxs_context, context, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, cluster_names, alpha_noun, alpha_verb, gamma_noun, gamma_verb, delimiter=None):
    x_uv_extra_features = np.zeros([x_uv.shape[0], x_uv.shape[1]+8])
    for i in xrange(x_uv.shape[0]):
        if delimiter:
            idx = uv_idxs_context[i+delimiter]
        else:
            idx = uv_idxs_context[i]
        streamid, targetid, date_hour = context[idx].split()
        example = x_uv[i][25:625]
        min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, \
        min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = \
        compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, example, cluster_names, alpha_noun, alpha_verb, gamma_noun, gamma_verb)
        print timeliness_noun, timeliness_verb
        x_uv_extra_features[i] = np.hstack((x_uv[i], np.array([min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb])))
    return x_uv_extra_features

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_verb_nouns_sorted_with_embeddings', required=True)
    parser.add_argument('-t', '--test_verb_nouns_sorted_with_embeddings', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-av', '--alpha_verb', required=True, type=float)
    parser.add_argument('-an', '--alpha_noun', required=True, type=float)
    parser.add_argument('-gv', '--gamma_verb', required=True, type=float)
    parser.add_argument('-gn', '--gamma_noun', required=True, type=float)
    parser.add_argument('-c', '--clusters_folder', required=True)
    parser.add_argument('-rnrs', '--rnr_save_model_file', required=False)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)
    parser.add_argument('-s', '--pre_train_split', required=False, type=float)

    args = parser.parse_args()

    if not args.pre_train_split:
        args.pre_train_split = 0.2

    filter_topics = json.load(open(args.entities_json))
    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    idxs_entities = {}
    for i, entity in enumerate(entities):
        idxs_entities[entity['target_id']] = i

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id
    recs = []

    begin = time.time()

    # read whole dataset
    x_train, y_train, train_context = create_global_data(args.train_verb_nouns_sorted_with_embeddings)
    x_test, y_test, test_context = create_global_data(args.test_verb_nouns_sorted_with_embeddings)


    # RNR classifier

    clf_rnr = None
    if args.rnr_load_model_file:
        clf_rnr = load_model(args.rnr_load_model_file)
    else:
        x_train_rnr = to_rnr_multitask(x_train, train_context, idxs_entities)
        y_train_rnr = to_rnr(y_train)
        clf_rnr = ensemble.GradientBoostingClassifier()
        clf_rnr = clf_rnr.fit(x_train_rnr, y_train_rnr)
        if args.rnr_save_model_file:
            save_model(args.rnr_save_model_file, clf_rnr)

    x_test_rnr = to_rnr_multitask(x_test, test_context, idxs_entities)
    y_test_rnr = to_rnr(y_test)
    
    assert y_test.shape[0] == len(test_context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    pred_rnr_prob = clf_rnr.predict_proba(x_test_rnr)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))
    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, test_context, 0, prob[0]))

    assert y_test_rnr.shape == pred_rnr.shape


    # UV classifier
    
    x_all_train_uv, y_all_train_uv, train_uv_idxs_context = to_uv_multitask(x_train, y_train, train_context, idxs_entities, True)
    x_test_uv, y_test_uv, test_uv_idxs_context = to_uv_given_pred_multitask(x_test, y_test, pred_rnr, test_context, idxs_entities)

    assert x_all_train_uv.shape[0] == y_all_train_uv.shape[0]
    assert y_all_train_uv.shape[0] == len(train_uv_idxs_context)
    assert x_test_uv.shape[0] == x_test.shape[0] - len(recs)
    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])
    assert y_test_uv.shape[0] == len(test_uv_idxs_context)

    centroids = {}
    centroids['nouns'] = defaultdict(lambda: defaultdict(defaultdict))
    centroids['verbs'] = defaultdict(lambda: defaultdict(defaultdict))
    cluster_elements = {}
    cluster_elements['nouns'] = defaultdict(lambda: defaultdict(list))
    cluster_elements['verbs'] = defaultdict(lambda: defaultdict(list))
    cluster_elements_info = {}
    cluster_elements_info['nouns'] = defaultdict(lambda: defaultdict(list))
    cluster_elements_info['verbs'] = defaultdict(lambda: defaultdict(list))
    cluster_names = {}
    cluster_names['nouns'] = defaultdict(lambda: 1)
    cluster_names['verbs'] = defaultdict(lambda: 1)
    cluster_timeliness = {}
    cluster_timeliness['nouns'] = defaultdict(lambda: defaultdict(int))
    cluster_timeliness['verbs'] = defaultdict(lambda: defaultdict(int))


    start = time.time()
    print 'pre training clusters with #pre_train_split of the training'
    rows = x_all_train_uv.shape[0]
    delimiter = int(rows * args.pre_train_split)
    x_pre_train_uv = x_all_train_uv[:delimiter]
    x_train_uv = x_all_train_uv[delimiter:]
    y_pre_train_uv = y_all_train_uv[:delimiter]
    y_train_uv = y_all_train_uv[delimiter:]

    assert x_pre_train_uv.shape[0] + x_train_uv.shape[0] == x_all_train_uv.shape[0]
    assert y_pre_train_uv.shape[0] + y_train_uv.shape[0] == y_all_train_uv.shape[0]

    for i in xrange(x_pre_train_uv.shape[0]):
        idx = train_uv_idxs_context[i]
        streamid, targetid, date_hour = train_context[idx].split()
        example = x_pre_train_uv[i][25:625]
        compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, example, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun, args.gamma_verb)
    elapsed = time.time() - start
    print 'finished pre training uv classifier, took %s' % elapsed


    start = time.time()
    print 'building training for uv classifier...'
    x_train_uv_extra_features = get_features(x_train_uv, train_uv_idxs_context, train_context, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun, args.gamma_verb, delimiter)
    elapsed = time.time() - start
    print 'finished building training for uv classifier, took %s' % elapsed

    start = time.time()
    print 'training on uv classifier...'
    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv_extra_features, y_train_uv)
    elapsed = time.time() - start
    print 'finished training on uv classifier, took %s' % elapsed

    start = time.time()
    print 'building testing for uv classifier...'
    x_test_uv_extra_features = get_features(x_test_uv, test_uv_idxs_context, test_context, centroids, cluster_elements, cluster_elements_info, cluster_timeliness, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun, args.gamma_verb)
    elapsed = time.time() - start
    print 'finished building testing for uv classifier, took %s' % elapsed

    start = time.time()
    print 'testing on uv classifier...'
    pred_uv_prob = clf_uv.predict_proba(x_test_uv_extra_features)
    pred_uv = np.array(map(np.argmax, pred_uv_prob))
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    pred_uv += 1
    for i, relevance in enumerate(pred_uv):
        prob = max(pred_uv_prob[i])
        recs.append(build_record(test_uv_idxs_context[i], test_context, relevance, prob))

    assert len(recs) == y_test.shape[0]
    assert y_test_uv.shape == pred_uv.shape

    elapsed_run = time.time() - begin

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


    clusters_noun_file = open(os.path.join(args.clusters_folder, 'clusters_nouns_%s' % args.alpha_noun), 'w')
    for targetid in centroids['nouns']:
        for cluster in centroids['nouns'][targetid]:
            clusters_noun_file.write('%s\t%s\t%s\t%s\n' % (targetid, cluster, list(centroids['nouns'][targetid][cluster]), cluster_elements_info['nouns'][targetid][cluster]))
    clusters_noun_file.close()

    clusters_verbs_file = open(os.path.join(args.clusters_folder, 'clusters_verbs_%s' % args.alpha_verb), 'w')
    for targetid in centroids['verbs']:
        for cluster in centroids['verbs'][targetid]:
            clusters_verbs_file.write('%s\t%s\t%s\t%s\n' % (targetid, cluster, list(centroids['verbs'][targetid][cluster]), cluster_elements_info['verbs'][targetid][cluster]))
    clusters_verbs_file.close()


if __name__ == '__main__':
  #np.set_printoptions(threshold=np.nan, linewidth=1000000000000000, )
  main()
