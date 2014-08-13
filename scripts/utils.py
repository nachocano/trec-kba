import numpy as np
from sklearn.externals import joblib
from collections import defaultdict
from gensim import matutils
from scipy.spatial.distance import euclidean
import time

filter_run = {
    "$schema": "http://trec-kba.org/schemas/v1.1/filter-run.json",
    "task_id": "kba-ccr-2014",
    "topic_set_id": "kba-2014-ccr-and-ssf",
    "corpus_id": "kba-streamcorpus-2014-v0_3_0-kba-filtered",
    "team_id": "UW",
    "team_name": "University of Washington",
    "poc_name": "TODO", 
    "poc_email": "icano@cs.washington.edu",
    "system_id": "TODO",
    "run_type": "automatic",
    "system_description": "TODO",
    "system_description_short": "TODO",
    }

def build_record(idx, context, relevance, prob):
    confidence = int(prob * 1000)
    stream_id, target_id, date_hour = context[idx].split()
    return [filter_run["team_id"], filter_run["system_id"], 
            stream_id, target_id, confidence, int(relevance), 1, date_hour, "NULL", -1, "0-0"]


def to_rnr(y):
    y_rnr = np.array(y)
    for i, value in enumerate(y):
        if value == -1:
            y_rnr[i] = 0
        elif value == 2:
            y_rnr[i] = 1
    return y_rnr

def to_uv(x,y, context=False):
    idxs = np.where(y > 0)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]]).astype(np.float32)
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]
    if context:
        return (x_uv, y_uv, idxs)
    return (x_uv, y_uv)

def to_uv_multitask(x,y, cxt, entities_idxs):
    idxs = np.where(y > 0)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]]).astype(np.float32)
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]

    indexes = []
    for i, index in enumerate(idxs):
        targetid = cxt[index].split()[1]
        indexes.append(entities_idxs[targetid])

    entity_number = len(entities_idxs)
    added_columns = x.shape[1] * entity_number
    rest = np.zeros([count, added_columns])
    for i, row in enumerate(x_uv):
        start = entity_number * (indexes[i]+1)
        for j in xrange(row.shape[0]):
            rest[i,start] = row[j]
            start+=1
    new_x_uv = np.hstack((x_uv, rest))
    return (new_x_uv, y_uv)

def to_uv_given_pred(x, y, pred_rnr):
    idxs = np.where(pred_rnr == 1)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]]).astype(np.float32)
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]
    return (x_uv, y_uv, idxs)

def to_uv_given_pred_multitask(x, y, pred_rnr, cxt, entities_idxs):
    idxs = np.where(pred_rnr == 1)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]]).astype(np.float32)
    y_uv = np.zeros([count])
    indexes = []
    for i, index in enumerate(idxs):
        targetid = cxt[index].split()[1]
        indexes.append(entities_idxs[targetid])

    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]

    entity_number = len(entities_idxs)
    added_columns = x.shape[1] * entity_number
    rest = np.zeros([count, added_columns])
    for i, row in enumerate(x_uv):
        start = entity_number * (indexes[i]+1)
        for j in xrange(row.shape[0]):
            rest[i,start] = row[j]
            start+=1
    new_x_uv = np.hstack((x_uv, rest))
    return (new_x_uv, y_uv, idxs)


def feature_importance(importances, classifier):
    indices = np.argsort(importances)[::-1]
    print 'Feature ranking for %s:' % classifier
    for f in xrange(len(importances)):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

def save_model(filename, model):
    if filename:
        print 'saving model to %s' % filename
        joblib.dump(model, filename)
        print 'model saved to %s' % filename

def load_model(filename):
    print 'loading model from %s' % filename
    clf = joblib.load(filename)
    print 'model loaded from %s' % filename
    return clf

def create_data(filename):
    x_list = defaultdict(list)
    y_list = defaultdict(list)
    context = defaultdict(list)
    with open(filename) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            date_hour = instance[2]
            label = instance[3]
            features = instance[4:]
            x_list[targetid].append(features)
            y_list[targetid].append(label)
            context[targetid].append('%s %s %s' % (streamid, targetid, date_hour))

    x = {}
    y = {}
    for targetid in y_list:
            x[targetid] = np.array(x_list[targetid]).astype(np.float32)
            y[targetid] = np.array(y_list[targetid]).astype(int)
    return x, y, context

def create_global_data(filename):
    x_list = []
    y_list = []
    context = []
    with open(filename) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            date_hour = instance[2]
            label = instance[3]
            features = instance[4:]
            x_list.append(features)
            y_list.append(label)
            context.append('%s %s %s' % (streamid, targetid, date_hour))

    x = np.array(x_list).astype(np.float32)
    y = np.array(y_list).astype(int)
    return x, y, context

def get_prob_and_pred(prob_global, prob_entity):
    prob_tmp_array = []
    pred_tmp_array = []
    mismatches = 0
    predictions_with_global = 0
    predictions_with_entity = 0
    for i in xrange(prob_global.shape[0]):
        pg = prob_global[i]
        pe = prob_entity[i]
        max_pe_idx = np.argmax(pe)
        max_pg_idx = np.argmax(pg)
        if max_pe_idx != max_pg_idx:
            mismatches += 1
        # take the one with highest prob to compute the confidence
        if pe[max_pe_idx] >= pg[max_pg_idx]:
            prob_tmp_array.append(pe)
            pred_tmp_array.append(max_pe_idx)
            predictions_with_entity += 1
        else:
            prob_tmp_array.append(pg)
            pred_tmp_array.append(max_pg_idx)
            predictions_with_global += 1
    return np.array(prob_tmp_array), np.array(pred_tmp_array), mismatches, predictions_with_global, predictions_with_entity

def get_prob_and_pred_single(pg, pe):
    max_pe_idx = np.argmax(pe)
    max_pg_idx = np.argmax(pg)
    # take the one with highest prob to compute the confidence
    if pe[max_pe_idx] >= pg[max_pg_idx]:
        return pe, max_pe_idx
    else:
        return pg, max_pg_idx

def similar_words(model, target_vector, topn=10):
    dists = np.dot(model.syn0norm, target_vector)
    best = np.argsort(dists)[::-1][:topn]
    result = [(model.index2word[sim], dists[sim]) for sim in best]
    return result[:topn]

