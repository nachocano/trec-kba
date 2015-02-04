#!/usr/bin/python
from __future__ import division
import os
import sys
import argparse
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

def mapping(filename):
    if 'emb_comb' in filename:
        return 'embedding, single'
    elif 'emb_pos' in filename:
        return 'embedding, pos'
    elif 'basic_single' in filename:
        return 'baseline'
    elif 'basic_multi' in filename:
        return 'baseline, multi-task'
    elif 'clust_dyn' in filename:
        return 'combined'
    elif 'clust_stat' in filename:
        return 'clustering only'
    elif 'mean_dyn' in filename:
        return 'staleness only'
    elif 'mean_stat' in filename:
        pass
    else:    
        print filename
        print 'wrong mapping'
        exit()

def to_list(data, index):
    return [elem[index] for elem in data]


def do_plot(data, directory, index, label, mode):
    plt.figure()
    for key in data:
        plt.plot(to_list(data[key], 0), to_list(data[key], index), label=key)
    plt.xlabel('Cutoff')
    plt.ylim(-0.01, 1.3)
    plt.xlim(1000,0)
    if mode == 'micro' and label == 'Precision':
        plt.legend(loc='upper right')
    else:
        plt.legend(loc='upper left')
    path_to_write_graph = os.path.join(directory, mode + label)
    plt.savefig(path_to_write_graph)
    plt.close()

def precision_recall(data, directory, mode):
    plt.figure()
    for key in data:
        plt.plot(to_list(data[key], 2), to_list(data[key], 1), label=key)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim(0, 1)
    plt.xlim(0,1)
    plt.legend(loc='upper right')
    path_to_write_graph = os.path.join(directory, mode + 'PrecisionRecall')
    plt.savefig(path_to_write_graph)
    plt.close()


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--directory', required=True)
    parser.add_argument('-od', '--out_dir', required=True)
    parser.add_argument('-m', '--mode', required=True)
    
    args = parser.parse_args()

    assert args.mode == 'micro' or args.mode == 'macro'

    data = defaultdict(list)
    for f in os.listdir(args.directory):
        filename = os.path.join(args.directory,f)
        if os.path.isfile(filename) and '.txt' in filename:
            key = mapping(filename)
            for line in open(filename).read().splitlines():
                cutoff, precision, recall, f1, su = line.split(',')
                data[key].append((cutoff, precision, recall, f1, su))

    
    #do_plot(data, args.out_dir, 1, "Precision", args.mode)
    #do_plot(data, args.out_dir, 2, "Recall", args.mode)
    #do_plot(data, args.out_dir, 3, "F1", args.mode)
    #do_plot(data, args.out_dir, 4, "SU", args.mode)

    precision_recall(data, args.out_dir, args.mode)
    
  
if __name__ == '__main__':
  main()
