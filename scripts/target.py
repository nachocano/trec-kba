#!/usr/bin/python
from __future__ import division
import jsonpickle
import numpy as np
from copy import deepcopy
import json



class Target:
    def __init__(self, targetid):
        self.targetid = targetid
        self.init_clusters = []
        self.streams = []
    
    def __str__(self):
        return jsonpickle.encode(self, unpicklable=False)

    def add_init_cluster(self, init_cluster):
        self.init_clusters.append(init_cluster)

    def add_stream(self, stream):
        self.streams.append(stream)

class InitCluster:
    def __init__(self, clusterid, centroid, docs):
        self.clusterid = clusterid
        self.centroid = str(list(centroid))
        self.docs = str(list(docs))

class Stream:
    def __init__(self, streamid, clusterid, stream_vector, current_centroid, timeliness, min_distance, avg_distance, prediction, truth):
        self.streamid = streamid
        self.clusterid = clusterid
        self.stream_vector = str(stream_vector)
        self.current_centroid = str(current_centroid)
        self.timeliness = timeliness
        self.min_distance = min_distance
        self.avg_distance = avg_distance
        self.prediction = prediction
        self.truth = truth


if __name__ == '__main__':
    target = Target('nacho')
    init_cluster1 = InitCluster(1, np.array([10,20,30]), [('doc1', 'date1', list(np.array([1,2,3]))), ('doc2', 'date2', list(np.array([2,3,4])))])
    stream1 = Stream(1,1,[0,0,0], [100, 100, 100], 10, 0, 10, -1, 1)
    stream2 = Stream(2,1,[1,0,1], [10.2121212, 10, 10], 1, 1, 2, 2, 1)
    target.add_stream(stream1)
    target.add_stream(stream2)
    target.add_init_cluster(init_cluster1)

    targets = []
    targets.append(target)
    targets.append(target)
    #print json.dumps(targets)
    print 'targets : [ %s ]' % (','.join(str(t) for t in targets))

  #print jsonpickle.encode(target, unpicklable=False)


