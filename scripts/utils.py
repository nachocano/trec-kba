import numpy as np

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

def to_uv(x,y):
    idxs = np.where(y > 0)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]])
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]
    return (x_uv, y_uv)

def to_uv_given_pred(x, y, pred_rnr):
    idxs = np.where(pred_rnr == 1)[0]
    count = len(idxs)
    x_uv = np.zeros([count,x.shape[1]])
    y_uv = np.zeros([count])
    for i, v in enumerate(idxs):
        x_uv[i] = x[v]
        y_uv[i] = y[v]
    return (x_uv, y_uv, idxs)

def feature_importance(importances, classifier):
    indices = np.argsort(importances)[::-1]
    print 'Feature ranking for %s:' % classifier
    for f in xrange(len(importances)):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))