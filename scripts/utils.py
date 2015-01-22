import numpy as np
from sklearn.externals import joblib
from collections import defaultdict
from gensim import matutils
from scipy.spatial.distance import euclidean
import time


UNASSESSED_LABEL = -10

filter_run = {
    "$schema": "http://trec-kba.org/schemas/v1.1/filter-run.json",
    "task_id": "kba-ccr-2014",
    "topic_set_id": "kba-2014-ccr-and-ssf",
    "corpus_id": "kba-streamcorpus-2014-v0_3_0-kba-filtered",
    "team_id": "UW",
    "team_name": "University of Washington",
    "poc_name": "Ignacio Cano", 
    "poc_email": "icano@cs.washington.edu",
    "system_id": "TODO",
    "run_type": "automatic",
    "system_description": "TODO",
    "system_description_short": "TODO",
    }

def build_record(idx, context, relevance, prob, predictions=None, truths=None, y_truth=None):
    confidence = int(prob * 1000)
    stream_id, target_id, date_hour = context[idx].split()
    prediction = int(relevance)
    if predictions != None:
        predictions[(stream_id, target_id)] = prediction
    if truths != None and y_truth != None:
        truths[(stream_id, target_id)] = y_truth
    return [filter_run["team_id"], filter_run["system_id"],
            stream_id, target_id, confidence, prediction, 1, date_hour, "NULL", -1, "0-0"]


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

def to_rnr_multitask(x, cxt, entities_idxs):
    entity_number = len(entities_idxs)
    added_columns = x.shape[1] * entity_number
    rest = np.zeros([x.shape[0], added_columns])

    indexes = []
    for element in cxt:
        targetid = element.split()[1]
        indexes.append(entities_idxs[targetid])

    for i, row in enumerate(x):
        start = x.shape[1] * (indexes[i])
        end = start + x.shape[1]
        rest[i][start:end] = row
    new_x = np.hstack((x, rest))
    return new_x

#def to_multitask_single(x, targetid, idxs_entities):
#    idx = idxs_entities[targetid]
#    entity_number = len(idxs_entities)
#    added_columns = x.shape[0] * entity_number
#    rest = np.zeros([added_columns])
#    start = x.shape[0] * idx
#    end = start + x.shape[0]
#    rest[start:end] = x
#    new_x = np.hstack((x, rest))
#    return new_x

def to_multitask(x, cxt, idxs_entities):
    entity_number = len(idxs_entities)
    added_columns = x.shape[1] * entity_number
    rest = np.zeros([x.shape[0], added_columns])
    for i, row in enumerate(x):
        targetid = cxt[i].split()[1]
        start = x.shape[1] * idxs_entities[targetid]
        end = start + x.shape[1]
        rest[i][start:end] = row
    new_x = np.hstack((x, rest))
    return new_x

def to_uv_given_pred(x, pred_rnr):
    idxs = np.where(pred_rnr == 1)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]]).astype(np.float32)
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
    return (x_uv, idxs)

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
        start = x.shape[1] * (indexes[i])
        end = start + x.shape[1]
        rest[i][start:end] = row
    new_x_uv = np.hstack((x_uv, rest))
    return (new_x_uv, y_uv, idxs)

def to_uv_multitask(x,y, cxt, entities_idxs, context=False):
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
        start = x.shape[1] * (indexes[i])
        end = start + x.shape[1]
        rest[i][start:end] = row
    new_x_uv = np.hstack((x_uv, rest))
    if context:
        return (new_x_uv, y_uv, idxs)
    return (new_x_uv, y_uv)

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


def create_separate_global_data(filename):
    x_a_list = []
    y_a_list = []
    cxt_a = []
    x_u_list = []
    y_u_list = []
    cxt_u = []
    with open(filename) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            date_hour = instance[2]
            label = int(instance[3])
            features = instance[4:]
            if label == UNASSESSED_LABEL:
                x_u_list.append(features)
                y_u_list.append(label)
                cxt_u.append('%s %s %s' % (streamid, targetid, date_hour))
            else:
                x_a_list.append(features)
                y_a_list.append(label)
                cxt_a.append('%s %s %s' % (streamid, targetid, date_hour))

    x_a = np.array(x_a_list).astype(np.float32)
    y_a = np.array(y_a_list).astype(int)
    x_u = np.array(x_u_list).astype(np.float32)
    y_u = np.array(y_u_list).astype(int)
    return x_a, y_a, cxt_a, x_u, y_u, cxt_u


def create_relevant_global_data(filename):
    x_r_list = []
    y_r_list = []
    cxt_r = []
    with open(filename) as f:
        for line in f.read().splitlines():
            instance = line.split()
            streamid = instance[0]
            targetid = instance[1]
            date_hour = instance[2]
            label = int(instance[3])
            features = instance[4:]
            if label == 1 or label == 2:
                x_r_list.append(features)
                y_r_list.append(label)
                cxt_r.append('%s %s %s' % (streamid, targetid, date_hour))
    x_r = np.array(x_r_list).astype(np.float32)
    y_r = np.array(y_r_list).astype(int)
    return x_r, y_r, cxt_r

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

def create_global_data_bow(filename):
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
            # do not consider BOW features
            features = instance[4:35]
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

def do_predict_rnr(clf_rnr, x, cxt, recs, returnIdx=False):
    pred_rnr_prob = clf_rnr.predict_proba(x)
    pred_rnr = np.array(map(np.argmax, pred_rnr_prob))
    rel_idxs = []
    for i, prob in enumerate(pred_rnr_prob):
        if prob[0] >= prob[1]:
            recs.append(build_record(i, cxt, 0, prob[0]))
        else:
            rel_idxs.append(i)
    if returnIdx:
        return rel_idxs
    else:
        return pred_rnr

def do_predict_rnr_from_train_u(clf_rnr, x_train, y_train, train_context, recs):
    unassessed_train_idxs = np.where(y_train == UNASSESSED_LABEL)[0]
    relevant_idxs = []
    for row_idx in unassessed_train_idxs:
        pred_prob = clf_rnr.predict_proba(x_train[row_idx,:25])[0]
        pred = np.argmax(pred_prob)
        if pred_prob[0] >= pred_prob[1]:
            recs.append(build_record(row_idx, train_context, 0, pred_prob[0]))
        else:
            relevant_idxs.append(row_idx)
    return relevant_idxs

def do_predict_uv(clf_uv, x, cxt, recs, idxs_cxt=None):
    pred_uv_prob = clf_uv.predict_proba(x)
    pred_uv = np.array(map(np.argmax, pred_uv_prob))
    pred_uv += 1
    for i, relevance in enumerate(pred_uv):
        prob = max(pred_uv_prob[i])
        if idxs_cxt != None:
            recs.append(build_record(idxs_cxt[i], cxt, relevance, prob))
        else:
            recs.append(build_record(i, cxt, relevance, prob))

