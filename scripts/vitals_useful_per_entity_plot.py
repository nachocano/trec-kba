#!/usr/bin/python
from __future__ import division
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import Counter


def get_counts(filename):
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    with open(filename) as f:
        for line in f.read().splitlines():
            l = line.strip()
            if l.startswith('#'):
                continue
            l = l.split('\t')
            streamid = l[2]
            timestamp = int(streamid.split('-')[0])
            targetid = l[3]
            relevance = int(l[5])
            date_hour = l[7]
            hour_bucket = int(timestamp / 3600)
            if relevance == 0 or relevance == -1:
                counts[targetid][hour_bucket][0] += 1
            else:
                counts[targetid][hour_bucket][relevance] += 1
    return counts

def get_counts_from_test(filename):
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for line in open(filename).read().splitlines():
        l = line.strip()
        instance = l.split()
        streamid = instance[0]
        targetid = instance[1]
        relevance = int(instance[3])
        timestamp = int(streamid.split('-')[0])
        key = (streamid, targetid)
        hour_bucket = int(timestamp / 3600)
        if relevance == 0 or relevance == -1:
            counts[targetid][hour_bucket][0] += 1
        else:
            counts[targetid][hour_bucket][relevance] += 1
    return counts

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--run_file', required=True)
    parser.add_argument('-t', '--test_tsv_file', required=True)
    args = parser.parse_args()


    truth_counts = get_counts_from_test(args.test_tsv_file)
    run_counts = get_counts(args.run_file)
    
    for targetid in run_counts:
        if "Randy" not in targetid:
            continue
        pred_vitals = []
        truth_vitals = []
        hours = []
        for hour_bucket, count in sorted(run_counts[targetid].iteritems(), key=lambda (k,v) : (k,v)):
            hours.append(hour_bucket)
            pred_vitals.append(count[2] + count[1])
            truth_vitals.append(truth_counts[targetid][hour_bucket][2] + truth_counts[targetid][hour_bucket][1])
        plot(targetid, 'vitals+usefuls', hours, pred_vitals, truth_vitals)

def plot(targetid, y_label, hours, preds, truths):
    print sum(preds)
    print sum(truths)
    fig = plt.figure()
    fig.suptitle(targetid, fontsize=13, fontweight='bold')
    plt.plot(hours, preds, 'r', hours, truths, 'g')
    plt.xlabel("time")
    plt.ylabel(y_label)
    plt.legend(('pred', 'truth'), loc="upper right")
    plt.show()


if __name__ == '__main__':
  main()
