#!/usr/bin/python
from __future__ import division
import re
import time
import numpy as np
from collections import defaultdict
from gensim import matutils
from target import Target, InitCluster, Stream


START_TIMELINESS = 0.5

def new_features_per_type(targetid, streamid, date_hour, centroids, stream_info, cluster_timeliness, cluster_names, example, alpha, gamma_increase, gamma_decrease, init_clusters_info=None):
    
    min_distance = 0
    avg_distance = 0
    all_zeros = 0
    timeliness = 0

    if np.all(example == 0):
        if not centroids[targetid].has_key(0):
            cluster_timeliness[targetid][0] = START_TIMELINESS
            # only put the centroid to 0 the first time
            centroids[targetid][0] = (example, 1)
        else:
            increase_timeliness(cluster_timeliness, targetid, 0, gamma_increase)

        timeliness = cluster_timeliness[targetid][0]
        decrease_timeliness_except(cluster_timeliness, targetid, 0, gamma_decrease)
        all_zeros = 1
        if init_clusters_info != None:
            init_clusters_info[targetid][0].append((streamid, date_hour, min_distance, avg_distance, list(example)))
        else:
            stream_info[targetid][0].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][0])))
    else:
        if not centroids.has_key(targetid):
            # new cluster, add the example as the centroids
            cluster_name = cluster_names[targetid]
            cluster_timeliness[targetid][cluster_name] = START_TIMELINESS
            timeliness = cluster_timeliness[targetid][cluster_name]
            centroids[targetid][cluster_name] = (example, 1)
            if init_clusters_info != None:
                init_clusters_info[targetid][cluster_name].append((streamid, date_hour, min_distance, avg_distance, list(example)))
            else:
                stream_info[targetid][cluster_name].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][cluster_name])))
            cluster_names[targetid] += 1
        else:
            similarities = []
            similarities_sum = 0
            for cluster in centroids[targetid]:
                centroid = matutils.unitvec(centroids[targetid][cluster][0] / centroids[targetid][cluster][1]).astype(np.float32)
                similarity = np.dot(centroid, example)
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
                # update the centroid for that cluster
                p_sum = centroids[targetid][candidate_cluster_name][0] + example
                p_n = centroids[targetid][candidate_cluster_name][1] + 1
                centroids[targetid][candidate_cluster_name] = (p_sum, p_n)
                if init_clusters_info != None:
                    init_clusters_info[targetid][candidate_cluster_name].append((streamid, date_hour, min_distance, avg_distance, list(example)))
                else:
                    stream_info[targetid][candidate_cluster_name].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][candidate_cluster_name])))
            else:
                # create a new cluster, add the example as the centroid
                cluster_name = cluster_names[targetid]
                cluster_timeliness[targetid][cluster_name] = START_TIMELINESS
                decrease_timeliness_except(cluster_timeliness, targetid, cluster_name, gamma_decrease)
                timeliness = cluster_timeliness[targetid][cluster_name]
                centroids[targetid][cluster_name] = (example, 1)
                if init_clusters_info != None:
                    init_clusters_info[targetid][cluster_name].append((streamid, date_hour, min_distance, avg_distance, list(example)))
                else:
                    stream_info[targetid][cluster_name].append((streamid, date_hour, timeliness, min_distance, avg_distance, list(example), list(centroids[targetid][cluster_name])))
                cluster_names[targetid] += 1
    return (min_distance, avg_distance, all_zeros, timeliness)


def update_clusters(targetid, streamid, date_hour, centroids, stream_info, cluster_timeliness, cluster_names, example, alpha_noun, alpha_verb, gamma_noun_increase, gamma_noun_decrease, gamma_verb_increase, gamma_verb_decrease, init_clusters_info=None):

    nouns = example[:300]
    verbs = example[300:]

    init_cluster_info_noun = init_clusters_info['nouns'] if init_clusters_info != None else None
    init_cluster_info_verb = init_clusters_info['verbs'] if init_clusters_info != None else None

    min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun = new_features_per_type(targetid, streamid, date_hour, centroids['nouns'], stream_info['nouns'], cluster_timeliness['nouns'], cluster_names['nouns'], nouns, alpha_noun, gamma_noun_increase, gamma_noun_decrease, init_cluster_info_noun)
    min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb = new_features_per_type(targetid, streamid, date_hour, centroids['verbs'], stream_info['verbs'], cluster_timeliness['verbs'], cluster_names['verbs'], verbs, alpha_verb, gamma_verb_increase, gamma_verb_decrease, init_cluster_info_verb)
    return min_distance_noun, avg_distance_noun, all_zeros_noun, timeliness_noun, min_distance_verb, avg_distance_verb, all_zeros_verb, timeliness_verb

def build_init_cluster_centroid(init_cluster_info, init_cluster_centroid, centroid):
    for targetid in init_cluster_info:
        for cluster_name in init_cluster_info[targetid]:
            init_cluster_centroid[targetid][cluster_name] = list(matutils.unitvec(centroid[targetid][cluster_name][0] / centroid[targetid][cluster_name][1]).astype(np.float32))

def build_init_clusters_centroids(init_clusters_info, init_clusters_centroids, centroids):
    build_init_cluster_centroid(init_clusters_info['nouns'], init_clusters_centroids['nouns'], centroids['nouns'])
    build_init_cluster_centroid(init_clusters_info['verbs'], init_clusters_centroids['verbs'], centroids['verbs'])

    assert len(init_clusters_info['nouns']) == len(centroids['nouns'])
    assert len(init_clusters_info['nouns']) == len(init_clusters_centroids['nouns'])
    assert len(init_clusters_info['verbs']) == len(centroids['verbs'])
    assert len(init_clusters_info['verbs']) == len(init_clusters_centroids['verbs'])

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
                centre = list(matutils.unitvec(current_centroid[0] / current_centroid[1]).astype(np.float32))
                stream = Stream(streamid, cluster, vector, centre, timeliness, min_distance, avg_distance, predictions[key] if predictions.has_key(key) else None, truths[key] if truths.has_key(key) else None)
                target.add_stream(stream)
        targets.append(target)
    return targets

def increase_timeliness(cluster_timeliness, targetid, cluster_name, gamma_increase):
    prev = cluster_timeliness[targetid][cluster_name]
    cluster_timeliness[targetid][cluster_name] = 1 - (1 - prev) * gamma_increase

def decrease_timeliness_except(cluster_timeliness, targetid, cluster_name, gamma_decrease):
    for cluster in cluster_timeliness[targetid]:
        if cluster != cluster_name:
            prev = cluster_timeliness[targetid][cluster]
            cluster_timeliness[targetid][cluster] = gamma_decrease * prev
