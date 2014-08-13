#!/usr/bin/python
from utils import to_rnr, to_uv, to_uv_given_pred, feature_importance, filter_run, build_record, create_global_data, build_record, load_model, save_model
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


def new_features_per_type(targetid, streamid, date_hour, centroids, cluster_elements, example, cluster_name, alpha):
    
    min_distance = 0
    avg_distance = 0
    
    if not centroids.has_key(targetid):
        # new cluster, add the example as the centroids for both nouns and verbs
        # update the cluster_name counter
        centroids[targetid][cluster_name] = example
        cluster_elements[cluster_name].append((streamid, date_hour, example))
        cluster_name += 1
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
            cluster_elements[candidate_cluster_name].append((streamid, date_hour, example))
            # update the centroid for that cluster
            examples = map(operator.itemgetter(2), cluster_elements[candidate_cluster_name])
            examples = np.array(examples)
            centroids[targetid][candidate_cluster_name] = matutils.unitvec(examples.mean(axis=0)).astype(np.float32)
        else:
            # create a new cluster, add the example as the centroid
            centroids[targetid][cluster_name] = example
            cluster_elements[cluster_name].append((streamid, date_hour, example))
            cluster_name += 1
    return (min_distance, avg_distance, cluster_name)


def compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, example, cluster_name_nouns, cluster_name_verbs, alpha_noun, alpha_verb):
    
    nouns = example[:300]
    verbs = example[300:]

    min_distance_noun, avg_distance_noun, cluster_name_nouns = new_features_per_type(targetid, streamid, date_hour, centroids['nouns'], cluster_elements['nouns'], nouns, cluster_name_nouns, alpha_noun)
    min_distance_verb, avg_distance_verb, cluster_name_verbs = new_features_per_type(targetid, streamid, date_hour, centroids['verbs'], cluster_elements['verbs'], verbs, cluster_name_verbs, alpha_verb)

    return min_distance_noun, avg_distance_noun, min_distance_verb, avg_distance_verb, cluster_name_nouns, cluster_name_verbs

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_verb_nouns_sorted_with_embeddings', required=True)
    parser.add_argument('-t', '--test_verb_nouns_sorted_with_embeddings', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-av', '--alpha_verb', required=True, type=float)
    parser.add_argument('-an', '--alpha_noun', required=True, type=float)
    parser.add_argument('-c', '--clusters_folder', required=True)
    parser.add_argument('-rnrs', '--rnr_save_model_file', required=False)
    parser.add_argument('-rnrl', '--rnr_load_model_file', required=False)

    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id

    x_train, y_train, train_context = create_global_data(args.train_verb_nouns_sorted_with_embeddings)
    x_test, y_test, test_context = create_global_data(args.test_verb_nouns_sorted_with_embeddings)

    recs = []

    y_test_rnr = to_rnr(y_test)

    assert y_test.shape[0] == len(test_context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    clf_rnr = None
    if args.rnr_load_model_file:
        clf_rnr = load_model(args.rnr_load_model_file)
    else:
        y_train_rnr = to_rnr(y_train)
        clf_rnr = ensemble.GradientBoostingClassifier()
        clf_rnr = clf_rnr.fit(x_train, y_train_rnr)
    
    if args.rnr_save_model_file:
        save_model(args.rnr_save_model_file, clf_rnr)

    pred_rnr_prob = clf_rnr.predict_proba(x_test)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))
    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, test_context, 0, prob[0]))

    assert y_test_rnr.shape == pred_rnr.shape

    x_train_uv, y_train_uv, train_uv_idxs_context = to_uv(x_train, y_train, True)
    x_test_uv, y_test_uv, test_uv_idxs_context = to_uv_given_pred(x_test, y_test, pred_rnr)

    assert x_train_uv.shape[0] == y_train_uv.shape[0]
    assert y_train_uv.shape[0] == len(train_uv_idxs_context)
    assert x_test_uv.shape[0] == x_test.shape[0] - len(recs)
    assert y_test_uv.shape[0] == len(pred_rnr[pred_rnr == 1])
    assert y_test_uv.shape[0] == len(test_uv_idxs_context)

    centroids = {}
    centroids['nouns'] = defaultdict(lambda: defaultdict(defaultdict))
    centroids['verbs'] = defaultdict(lambda: defaultdict(defaultdict))
    cluster_elements = {}
    cluster_elements['nouns'] = defaultdict(list)
    cluster_elements['verbs'] = defaultdict(list)
    cluster_name_nouns = 0
    cluster_name_verbs = 0

    start = time.time()
    print 'building training for uv classifier...'
    x_train_uv_extra_features = np.zeros([x_train_uv.shape[0], x_train_uv.shape[1]+4])
    for i in xrange(x_train_uv.shape[0]):
        idx = train_uv_idxs_context[i]
        streamid, targetid, date_hour = train_context[idx].split()
        example = x_train_uv[i][25:]
        min_distance_noun, avg_distance_noun, min_distance_verb, avg_distance_verb, cluster_name_nouns, cluster_name_verbs = \
                        compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, example, cluster_name_nouns, cluster_name_verbs, args.alpha_noun, args.alpha_verb)
        x_train_uv_extra_features[i] = np.hstack((x_train_uv[i], np.array([min_distance_noun, avg_distance_noun, min_distance_verb, avg_distance_verb])))
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
    x_test_uv_extra_features = np.zeros([x_test_uv.shape[0], x_test_uv.shape[1]+4])
    for i in xrange(x_test_uv.shape[0]):
        idx = test_uv_idxs_context[i]
        streamid, targetid, date_hour = test_context[idx].split()
        example = x_test_uv[i][25:]
        min_distance_noun, avg_distance_noun, min_distance_verb, avg_distance_verb, cluster_name_nouns, cluster_name_verbs = \
                        compute_new_features(targetid, streamid, date_hour, centroids, cluster_elements, example, cluster_name_nouns, cluster_name_verbs, args.alpha_noun, args.alpha_verb)
        x_test_uv_extra_features[i] = np.hstack((x_test_uv[i], np.array([min_distance_noun, avg_distance_noun, min_distance_verb, avg_distance_verb])))
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

    output = open(args.output_file, "w")
    for rec in recs:
        output.write("\t".join(map(str, rec)) + "\n")

    filter_run_json_string = json.dumps(filter_run, indent=4, sort_keys=True)
    filter_run_json_string = re.sub("\n", "\n#", filter_run_json_string)
    output.write("#%s\n" % filter_run_json_string)
    output.close()

                        
    clusters_noun_file = open(os.path.join(args.clusters_folder, 'clusters_nouns_%s' % args.alpha_noun), 'w')
    for targetid in centroids['nouns']:
        for cluster in centroids['nouns'][targetid]:
            clusters_noun_file.write('%s\t%s\t%s\n' % (targetid, cluster, list(centroids['nouns'][targetid][cluster]))
    clusters_noun_file.close()

    clusters_verbs_file = open(os.path.join(args.clusters_folder, 'clusters_verbs_%s' % args.alpha_verb), 'w')
    for targetid in centroids['verbs']:
        for cluster in centroids['verbs'][targetid]:
            clusters_verbs_file.write('%s\t%s\t%s\t%s\n' % (targetid, cluster, list(centroids['verbs'][targetid][cluster]))
    clusters_verbs_file.close()

if __name__ == '__main__':
  np.set_printoptions(threshold=np.nan)
  main()
