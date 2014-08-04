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

def get_disambiguated_counts(filename):
    truth_counts = defaultdict(list)
    for line in open(filename).read().splitlines():
        l = line.strip()
        if l.startswith('#'):
            continue
        instance = l.split()
        streamid = instance[2]
        targetid = instance[3]
        relevance = int(instance[5])
        key = (streamid, targetid)
        truth_counts[key].append(relevance)

    majority_relevance = {}
    for key in truth_counts:
        counter = Counter(truth_counts[key])
        distinct_annotations = set(counter.values())
        if distinct_annotations == 1:
             majority_relevance[key] = max(list(counter.elements()))
        else:
            majority_relevance[key] = counter.most_common()[0][0]

    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    processed = {}
    for line in open(filename).read().splitlines():
        l = line.strip()
        if l.startswith('#'):
            continue
        l = l.split()
        streamid = l[2]
        timestamp = int(streamid.split('-')[0])
        targetid = l[3]
        key = (streamid, targetid)
        if processed.has_key(key):
            continue
        processed[key] = True
        relevance = majority_relevance[key]
        date_hour = l[7]
        hour_bucket = int(timestamp / 3600)
        if relevance == 0 or relevance == -1:
            counts[targetid][hour_bucket][0] += 1
        else:
            counts[targetid][hour_bucket][relevance] += 1
    return counts

def main():
 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--run_file', required=True)
    parser.add_argument('-t', '--truth_file', required=True)
    args = parser.parse_args()


    truth_counts = get_disambiguated_counts(args.truth_file)
    run_counts = get_counts(args.run_file)
    
    for targetid in run_counts:
        pred_vitals = []
        truth_vitals = []
        hours = []
        for hour_bucket, count in sorted(run_counts[targetid].iteritems(), key=lambda (k,v) : (k,v)):
            hours.append(hour_bucket)
            pred_vitals.append(count[2])
            truth_vitals.append(truth_counts[targetid][hour_bucket][2])
        plot(targetid, 'vitals', hours, pred_vitals, truth_vitals)

def plot(targetid, y_label, hours, preds, truths):
    fig = plt.figure()
    fig.suptitle(targetid, fontsize=13, fontweight='bold')
    plt.plot(hours, preds, 'r', hours, truths, 'g')
    plt.xlabel("time")
    plt.ylabel(y_label)
    plt.legend(('pred', 'truth'), loc="upper right")
    plt.show()


if __name__ == '__main__':
  main()
