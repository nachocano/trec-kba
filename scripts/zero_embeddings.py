#!/usr/bin/python
from __future__ import division
from utils import create_separate_global_data
import re
import os
import sys
import time
import argparse
import numpy as np

from collections import defaultdict


def print_stats(x_matrix, y_vector, mode):
    zero_verbs_useful = 0
    zero_verbs_vital = 0
    zero_nouns_useful = 0
    zero_nouns_vital = 0
    zero_nouns_nr = 0
    zero_verbs_nr = 0
    useful = 0
    vital = 0
    non_relevant = 0
    for x,y in zip(x_matrix, y_vector):
        if y == 1:
            useful += 1
            if np.all(x[25:325] == 0):
                zero_nouns_useful +=1
            if np.all(x[325:625] == 0):
                zero_verbs_useful +=1
        elif y == 2:
            vital += 1
            if np.all(x[25:325] == 0):
                zero_nouns_vital +=1
            if np.all(x[325:625] == 0):
                zero_verbs_vital +=1
        else:
            non_relevant += 1
            if np.all(x[25:325] == 0):
                zero_nouns_nr +=1
            if np.all(x[325:625] == 0):
                zero_verbs_nr +=1

    print '### %s ###' % mode
    print 'number of examples with zero noun embedding that are vital %s' % zero_nouns_vital
    print 'number of examples with zero noun embedding that are useful %s' % zero_nouns_useful
    print 'number of examples with zero noun embedding that are non relevant %s' % zero_nouns_nr
    print 'number of examples with zero verb embedding that are vital %s' % zero_verbs_vital
    print 'number of examples with zero verb embedding that are useful %s' % zero_verbs_useful
    print 'number of examples with zero verb embedding that are non relevant %s' % zero_verbs_nr
    print 'total usefuls %s' % useful
    print 'total vitals %s' % vital
    print 'total non_relevant %s' % non_relevant
    print '### end %s ###' % mode


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-tr', '--training_file', required=True)
    parser.add_argument('-t', '--test_file', required=True)

    args = parser.parse_args()

    x_train_a, y_train_a, cxt_train_a, _, _, _ = create_separate_global_data(args.training_file)
    x_test_a, y_test_a, cxt_test_a, _, _, _ = create_separate_global_data(args.test_file)


    print_stats(x_train_a, y_train_a, 'train')
    print_stats(x_test_a, y_test_a, 'test')



if __name__ == '__main__':
  #np.set_printoptions(threshold=np.nan, linewidth=1000000000000000, )
  main()
