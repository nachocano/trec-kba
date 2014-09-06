#!/usr/bin/python
from utils import do_predict_rnr, do_predict_uv, create_separate_global_data, to_rnr_multitask, save_model, to_rnr
import json
import time
import re
import argparse
import numpy as np
from sklearn import ensemble
import json

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-e', '--entities_json', required=True)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-rnrs', '--rnr_save_model_file', required=True)

    args = parser.parse_args()

    filter_topics = json.load(open(args.entities_json))
    entities = []
    [entities.append(e) for e in filter_topics["targets"] if e['training_time_range_end']]

    entities_idxs = {}
    for i, entity in enumerate(entities):
        entities_idxs[entity['target_id']] = i

    # reading data
    print 'reading data'
    x_train_a, y_train_a, cxt_train_a, _, _, _ = create_separate_global_data(args.training_file)
    print 'read data'

    print 'to multitask'
    x_train_a_rnr = to_rnr_multitask(x_train_a, cxt_train_a, entities_idxs)
    y_train_a_rnr = to_rnr(y_train_a)
    print 'multitask done'

    assert y_train_a.shape == y_train_a_rnr.shape
    assert len(y_train_a_rnr[y_train_a_rnr == -1]) == 0
    assert len(y_train_a_rnr[y_train_a_rnr == 2]) == 0

    print x_train_a.shape
    print x_train_a_rnr.shape

    print 'training classifer'
    clf_rnr = ensemble.ExtraTreesClassifier(n_estimators=150, random_state=37)
    clf_rnr = clf_rnr.fit(x_train_a_rnr, y_train_a_rnr)
    print 'classifier trained'
    save_model(args.rnr_save_model_file, clf_rnr)

if __name__ == '__main__':
  main()
