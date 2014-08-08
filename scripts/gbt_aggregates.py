#!/usr/bin/python
from utils import to_rnr, to_uv, to_uv_given_pred, feature_importance, filter_run, build_record, save_model, create_global_data, load_model
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


def update_clusters(targetid, streamid, centroids, cluster_elements, cluster_streamids, example, cluster_name, alpha):
    min_distance = 0
    avg_distance = 0
    tmp_centroids = centroids[targetid]
    if len(tmp_centroids) == 0:
        # new cluster, add it as a centroid and as an element
        #update the cluster_name counter
        tmp_centroids[cluster_name] = example
        cluster_elements[cluster_name].append(example)
        cluster_streamids[cluster_name].append(streamid)
        cluster_name += 1
    else:
        # already have a cluster for the entity, compute the distance to its centroid
        distances = []
        distances_sum = 0
        for cluster in tmp_centroids:
            d = euclidean(example, tmp_centroids[cluster])
            distances.append((cluster,d))
            distances_sum += d
        minimum_tuple = min(tuple(r[::-1]) for r in distances)[::-1]
        candidate_cluster_name = minimum_tuple[0]
        # two new features
        min_distance = minimum_tuple[1]
        avg_distance = distances_sum / len(distances)

        if min_distance < alpha:
            # put in an already existent cluster
            cluster_elements[candidate_cluster_name].append(example)
            cluster_streamids[cluster_name].append(streamid)
            #update the centroid for that cluster
            tmp_centroids[candidate_cluster_name] = np.mean(cluster_elements[candidate_cluster_name], axis=0)
        else:
            # create a new cluster, add the example as the centroid
            tmp_centroids[cluster_name] = example
            cluster_elements[cluster_name].append(example)
            cluster_streamids[cluster_name].append(streamid)
            cluster_name += 1
    return (min_distance, avg_distance, cluster_name)

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-o', '--output_file', required=True)
    parser.add_argument('-tr', '--train_with_vectors_sorted_tsv_file', required=True)
    parser.add_argument('-t', '--test_with_vectors_sorted_tsv_file', required=True)
    parser.add_argument('-i', '--system_id', required=True)
    parser.add_argument('-a', '--alpha', required=True, type=float)
    parser.add_argument('-c', '--clusters_file', required=True)
    parser.add_argument('-rnr', '--rnr_load_model_file', required=False)
    parser.add_argument('-uv', '--uv_save_model_file', required=False)
    
    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))

    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    filter_run["run_info"] = {
        "num_entities": len(entities),
    }
    filter_run["system_id"] = args.system_id

    x_train, y_train, train_context = create_global_data(args.train_with_vectors_sorted_tsv_file)
    x_test, y_test, test_context = create_global_data(args.test_with_vectors_sorted_tsv_file)

    recs = []

    y_test_rnr = to_rnr(y_test)

    assert y_test.shape[0] == len(test_context)
    assert y_test.shape == y_test_rnr.shape
    assert len(y_test_rnr[y_test_rnr == -1]) == 0
    assert len(y_test_rnr[y_test_rnr == 2]) == 0

    clf_rnr_global = load_model(args.rnr_load_model_file)
    pred_rnr_prob = clf_rnr_global.predict_proba(x_test)
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

    # build the aggregate vectors for training data, and then they will be used for testing as well
    centroids = defaultdict(defaultdict)
    cluster_elements = defaultdict(list)
    cluster_streamids = defaultdict(list)
    cluster_name = 0

    x_train_uv_extra_features = np.zeros([x_train_uv.shape[0], x_train_uv.shape[1]+2])
    for i in xrange(x_train_uv.shape[0]):
        idx = train_uv_idxs_context[i]
        streamid, targetid, _ = train_context[idx].split()
        example = x_train_uv[i][25:]
        min_distance, avg_distance, cluster_name = update_clusters(targetid, streamid, centroids, cluster_elements, cluster_streamids, example, cluster_name, args.alpha)
        x_train_uv_extra_features[i] = np.hstack((x_train_uv[i], np.array([min_distance, avg_distance])))

    clf_uv = ensemble.GradientBoostingClassifier()
    clf_uv = clf_uv.fit(x_train_uv_extra_features, y_train_uv)

    #feature_importance(clf_uv.feature_importances_, 'U-V')
    
    save_model(args.uv_save_model_file, clf_uv)

    start = time.time()
    print 'testing on uv classifier...'
    pred_uv_prob = []
    for i in xrange(y_test_uv.shape[0]):
        idx = test_uv_idxs_context[i]
        streamid, targetid, _ = test_context[idx].split()
        example = x_test_uv[i][25:]
        min_distance, avg_distance, cluster_name = update_clusters(targetid, streamid, centroids, cluster_elements, cluster_streamids, example, cluster_name, args.alpha)
        instance_to_predict = np.hstack((x_test_uv[i], np.array([min_distance, avg_distance])))
        pred_uv_prob.append(clf_uv.predict_proba(instance_to_predict)[0])
    elapsed = time.time() - start
    print 'finished testing on uv classifier, took %s' % elapsed

    pred_uv = np.array(map(np.argmax, pred_uv_prob))
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

    clusters_file = open(args.clusters_file, "w")
    for targetid in centroids:
        for cluster in centroids[targetid]:
            clusters_file.write('%s\t%s\t%s\t%s\n' % (targetid, cluster, list(centroids[targetid][cluster]), cluster_streamids[cluster]))
    clusters_file.close()

if __name__ == '__main__':
  np.set_printoptions(threshold=np.nan)
  main()
