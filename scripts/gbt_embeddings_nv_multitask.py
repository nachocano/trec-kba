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
from target import Target, InitCluster, Stream

starting_timeliness = 0.5

def increase_timeliness(cluster_timeliness, targetid, cluster_name, gamma_increase):
    prev = cluster_timeliness[targetid][cluster_name]
    cluster_timeliness[targetid][cluster_name] = 1 - (1 - prev) * gamma_increase

def decrease_timeliness_except(cluster_timeliness, targetid, cluster_name, gamma_decrease):
    for cluster in cluster_timeliness[targetid]:
        if cluster != cluster_name:
            prev = cluster_timeliness[targetid][cluster]
            cluster_timeliness[targetid][cluster] = gamma_decrease * prev

def new_features_per_type(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, alpha, gamma_increase, gamma_decrease, init_clusters_info=None):
    
    min_distance = 0
    avg_distance = 0
    all_zeros = 0
    timeliness = 0

    if np.all(example == 0):
        if not centroids[targetid].has_key(0):
            cluster_timeliness[targetid][0] = starting_timeliness
        else:
            increase_timeliness(cluster_timeliness, targetid, 0, gamma_increase)

        timeliness = cluster_timeliness[targetid][0]
        decrease_timeliness_except(cluster_timeliness, targetid, 0, gamma_decrease)
        cluster_elements[targetid][0].append(example)
        examples = np.array(cluster_elements[targetid][0])
        centroids[targetid][0] = matutils.unitvec(examples.mean(axis=0)).astype(np.float32)
        all_zeros = 1
        if init_clusters_info != None:
            init_clusters_info[targetid][0].append((streamid, date_hour, min_distance, avg_distance, list(example)))
        else:
            stream_info[targetid][0].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][0])))
    else:
        if not centroids.has_key(targetid):
            # new cluster, add the example as the centroids
            cluster_name = cluster_names[targetid]
            cluster_timeliness[targetid][cluster_name] = starting_timeliness
            timeliness = cluster_timeliness[targetid][cluster_name]
            centroids[targetid][cluster_name] = example
            cluster_elements[targetid][cluster_name].append(example)
            if init_clusters_info != None:
                init_clusters_info[targetid][cluster_name].append((streamid, date_hour, min_distance, avg_distance, list(example)))
            else:
                stream_info[targetid][cluster_name].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][cluster_name])))
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
            min_distance = 1 - max_similarity
            avg_distance = 1 - (similarities_sum / len(similarities))

            if min_distance < alpha:
                # put in an already existent cluster
                increase_timeliness(cluster_timeliness, targetid, candidate_cluster_name, gamma_increase)
                decrease_timeliness_except(cluster_timeliness, targetid, candidate_cluster_name, gamma_decrease)
                timeliness = cluster_timeliness[targetid][candidate_cluster_name]
                cluster_elements[targetid][candidate_cluster_name].append(example)
                # update the centroid for that cluster
                examples = np.array(cluster_elements[targetid][candidate_cluster_name])
                centroids[targetid][candidate_cluster_name] = matutils.unitvec(examples.mean(axis=0)).astype(np.float32)
                if init_clusters_info != None:
                    init_clusters_info[targetid][candidate_cluster_name].append((streamid, date_hour, min_distance, avg_distance, list(example)))
                else:
                    stream_info[targetid][candidate_cluster_name].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][candidate_cluster_name])))
            else:
                # create a new cluster, add the example as the centroid
                cluster_name = cluster_names[targetid]
                cluster_timeliness[targetid][cluster_name] = starting_timeliness
                decrease_timeliness_except(cluster_timeliness, targetid, cluster_name, gamma_decrease)
                timeliness = cluster_timeliness[targetid][cluster_name]
                centroids[targetid][cluster_name] = example
                cluster_elements[targetid][cluster_name].append(example)
                if init_clusters_info != None:
                    init_clusters_info[targetid][cluster_name].append((streamid, date_hour, min_distance, avg_distance, list(example)))
                else:
                    stream_info[targetid][cluster_name].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][cluster_name])))
                cluster_names[targetid] += 1
    return (min_distance, avg_distance, all_zeros, timeliness)


def compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, init_clusters_info=None):

    nouns = example[:300]
    verbs = example[300:]

    init_cluster_info_noun = None if not init_clusters_info else init_clusters_info['nouns']
    init_cluster_info_verb = None if not init_clusters_info else init_clusters_info['verbs']

    min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun = new_features_per_type(targetid, streamid, date_hour, centroids['nouns'], cluster_elements['nouns'], stream_info['nouns'], cluster_timeliness['nouns'], cluster_names['nouns'], nouns, alpha_noun, gamma_noun_increase, gamma_noun_decrease, init_cluster_info_noun)
    min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = new_features_per_type(targetid, streamid, date_hour, centroids['verbs'], cluster_elements['verbs'], stream_info['verbs'], cluster_timeliness['verbs'], cluster_names['verbs'], verbs, alpha_verb, gamma_verb_increase, gamma_verb_decrease, init_cluster_info_verb)
    return min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb

def build_init_cluster_centroid(init_cluster_info, init_cluster_centroid, centroid):
    for targetid in init_cluster_info:
        for cluster_name in init_cluster_info[targetid]:
            init_cluster_centroid[targetid][cluster_name] = list(centroid[targetid][cluster_name])

def build_init_clusters_centroids(init_clusters_info, init_clusters_centroids, centroids):
    build_init_cluster_centroid(init_clusters_info['nouns'], init_clusters_centroids['nouns'], centroids['nouns'])
    build_init_cluster_centroid(init_clusters_info['verbs'], init_clusters_centroids['verbs'], centroids['verbs'])

    assert len(init_clusters_info['nouns']) == len(centroids['nouns'])
    assert len(init_clusters_info['nouns']) == len(init_clusters_centroids['nouns'])
    assert len(init_clusters_info['verbs']) == len(centroids['verbs'])
    assert len(init_clusters_info['verbs']) == len(init_clusters_centroids['verbs'])

def get_features(x_uv, y_uv, mode, uv_idxs_context, context, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, init_cluster_info, delimiter=None):
    x_uv_filtered = []
    y_uv_filtered = []
    for i in xrange(x_uv.shape[0]):
        if delimiter != None:
            idx = uv_idxs_context[i+delimiter]
        else:
            idx = uv_idxs_context[i]
        streamid, targetid, date_hour = context[idx].split()
        example = x_uv[i][25:625]
        min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, \
        min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = \
        compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, init_cluster_info)
        if mode == 'train':
            # only train the GBT with the annotated stuff, but update the clusters for all of them
            if y_uv[i] != -10:
                x_uv_filtered.append(np.hstack((x_uv[i], [min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb])))
                y_uv_filtered.append(y_uv[i])
        elif mode == 'test':
            # test the GBT with all the annotated and unassessed stuff
            x_uv_filtered.append(np.hstack((x_uv[i], [min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb])))
            y_uv_filtered.append(y_uv[i])
        else:
            print 'error, no mode %s defined' % mode
    return np.array(x_uv_filtered), np.array(y_uv_filtered)
    

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_verb_nouns_assessed_unassessed_sorted', required=True)
    parser.add_argument('-t', '--test_verb_nouns_sorted_with_embeddings', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-av', '--alpha_verb', required=True, type=float)
    parser.add_argument('-an', '--alpha_noun', required=True, type=float)
    parser.add_argument('-gvi', '--gamma_verb_increase', required=True, type=float)
    parser.add_argument('-gvd', '--gamma_verb_decrease', required=True, type=float)
    parser.add_argument('-gni', '--gamma_noun_increase', required=True, type=float)
    parser.add_argument('-gnd', '--gamma_noun_decrease', required=True, type=float)
    parser.add_argument('-c', '--clusters_folder', required=True)
    parser.add_argument('-rnrs', '--rnr_save_model_file', required=False)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)
    parser.add_argument('-s', '--pre_train_split', required=False, type=float, default=0.2)

    args = parser.parse_args()

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
    x_train, y_train, train_context = create_global_data(args.train_verb_nouns_assessed_unassessed_sorted)
    x_test, y_test, test_context = create_global_data(args.test_verb_nouns_sorted_with_embeddings)


    # RNR classifier

    clf_rnr = None
    if args.rnr_load_model_file:
        clf_rnr = load_model(args.rnr_load_model_file)
    else:
        x_train_rnr = to_rnr_multitask(x_train, train_context, idxs_entities)
        y_train_rnr = to_rnr(y_train)
        clf_rnr = ensemble.GradientBoostingClassifier()
        start = time.time()
        print 'training rnr classifier...'
        clf_rnr = clf_rnr.fit(x_train_rnr, y_train_rnr)
        if args.rnr_save_model_file:
            save_model(args.rnr_save_model_file, clf_rnr)
        elapsed = time.time() - start
        print 'finished training rnr classifier, took %s' % elapsed
        exit()

    print 'converting to rnr...'
    start = time.time()
    x_test_rnr = to_rnr_multitask(x_test, test_context, idxs_entities)
    y_test_rnr = to_rnr(y_test)
    print 'finished converting to rnr, took %s' % (time.time() - start)
    
    assert y_test.shape[0] == len(test_context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    start = time.time()
    print 'testing rnr classifier...'
    pred_rnr_prob = clf_rnr.predict_proba(x_test_rnr)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))
    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, test_context, 0, prob[0]))
    elapsed = time.time() - start
    print 'finished testing rnr classifier, took %s' % elapsed
    assert y_test_rnr.shape == pred_rnr.shape


    # UV classifier
    print 'converting to uv...'
    start = time.time()
    x_all_train_uv, y_all_train_uv, train_uv_idxs_context = to_uv_multitask(x_train, y_train, train_context, idxs_entities, True)
    x_test_uv, y_test_uv, test_uv_idxs_context = to_uv_given_pred_multitask(x_test, y_test, pred_rnr, test_context, idxs_entities)
    print 'finished converting to uv, took %s' % (time.time() - start)

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
    print 'pre training clusters with %s of the training' % args.pre_train_split
    rows = x_all_train_uv.shape[0]
    delimiter = int(rows * args.pre_train_split)
    x_pre_train_uv = x_all_train_uv[:delimiter]
    print 'pre training examples are %d' % x_pre_train_uv.shape[0]
    x_train_uv = x_all_train_uv[delimiter:]
    y_pre_train_uv = y_all_train_uv[:delimiter]
    y_train_uv = y_all_train_uv[delimiter:]

    assert x_pre_train_uv.shape[0] + x_train_uv.shape[0] == x_all_train_uv.shape[0]
    assert y_pre_train_uv.shape[0] + y_train_uv.shape[0] == y_all_train_uv.shape[0]

    for i in xrange(x_pre_train_uv.shape[0]):
        idx = train_uv_idxs_context[i]
        streamid, targetid, date_hour = train_context[idx].split()
        example = x_pre_train_uv[i][25:625]
        compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, example, args.alpha_noun, args.alpha_verb, args.gamma_noun_increase, args.gamma_noun_decrease, args.gamma_verb_increase, args.gamma_verb_decrease, init_clusters_info)
    elapsed = time.time() - start
    print 'finished pre training uv classifier, took %s' % elapsed

    print 'adding centroids to init_clusters'
    build_init_clusters_centroids(init_clusters_info, init_clusters_centroids, centroids)
    print 'finished adding centroids to init_clusters'

    start = time.time()
    print 'building training for uv classifier...'
    x_train_uv_filtered_extra_features, y_train_uv_filtered_extra_features = get_features(x_train_uv, y_train_uv, 'train', train_uv_idxs_context, train_context, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun_increase, args.gamma_noun_decrease, args.gamma_verb_increase, args.gamma_verb_decrease, None, delimiter)
    elapsed = time.time() - start
    print 'finished building training for uv classifier, took %s' % elapsed

    assert x_train_uv_filtered_extra_features.shape[0] == y_train_uv_filtered_extra_features.shape[0]
    assert len(y_train_uv_filtered_extra_features[y_train_uv_filtered_extra_features == -1]) == 0
    assert len(y_train_uv_filtered_extra_features[y_train_uv_filtered_extra_features == 0]) == 0
    assert len(y_train_uv_filtered_extra_features[y_train_uv_filtered_extra_features == -10]) == 0

    start = time.time()
    print 'training on uv classifier...'
    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv_filtered_extra_features, y_train_uv_filtered_extra_features)
    elapsed = time.time() - start
    print 'finished training on uv classifier, took %s' % elapsed

    start = time.time()
    print 'building testing for uv classifier...'
    x_test_uv_extra_features, _ = get_features(x_test_uv, y_test_uv, 'test', test_uv_idxs_context, test_context, centroids, cluster_elements, stream_info, cluster_timeliness, cluster_names, args.alpha_noun, args.alpha_verb, args.gamma_noun_increase, args.gamma_noun_decrease, args.gamma_verb_increase, args.gamma_verb_decrease, None)
    elapsed = time.time() - start
    print 'finished building testing for uv classifier, took %s' % elapsed

    start = time.time()
    print 'testing on uv classifier...'
    pred_uv_prob = clf_uv.predict_proba(x_test_uv_extra_features)
    pred_uv = np.array(map(np.argmax, pred_uv_prob))
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    pred_uv += 1
    predictions = {}
    truths = {}
    for i, relevance in enumerate(pred_uv):
        prob = max(pred_uv_prob[i])
        truth_value = y_test_uv[i]
        truth = None
        # means is assessed
        if truth_value != -10:
            truth = y_test_uv[i]+1
        recs.append(build_record(test_uv_idxs_context[i], test_context, relevance, prob, predictions, truths, truth))


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

    print 'building targets ...'
    start = time.time()
    noun_targets = build_targets('nouns', centroids, init_clusters_centroids, init_clusters_info, stream_info, predictions, truths)
    verb_targets = build_targets('verbs', centroids, init_clusters_centroids, init_clusters_info, stream_info, predictions, truths)
    print 'finished building targets, took %s' % (time.time() - start)

    clusters_noun_file = open(os.path.join(args.clusters_folder, 'nouns_%s' % args.alpha_noun), 'w')
    clusters_noun_file.write('targets : [ %s ]' % (','.join(str(t) for t in noun_targets)))
    clusters_noun_file.close()

    clusters_verbs_file = open(os.path.join(args.clusters_folder, 'verbs_%s' % args.alpha_verb), 'w')
    clusters_verbs_file.write('targets : [ %s ]' % (','.join(str(t) for t in verb_targets)))
    clusters_verbs_file.close()

    print 'noun clusters %s' % stats('nouns', centroids)
    print 'verb clusters %s' % stats('verbs', centroids)

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
