import numpy
import matplotlib
matplotlib.use('Agg')
from scipy.cluster.vq import *
import pylab
pylab.close()
import matplotlib.pyplot as plt
 
# generate 3 sets of normally distributed points around
# different means with different variances
pt1 = numpy.random.normal(1, 0.2, (100,2))
pt2 = numpy.random.normal(2, 0.5, (300,2))
#pt3 = numpy.random.normal(3, 0.3, (100,2))
 
# slightly move sets 2 and 3 (for a prettier output)
pt2[:,0] += 1
#pt3[:,0] -= 0.5
 
xy = numpy.concatenate((pt1, pt2))
print xy.shape
 
# kmeans for 2 clusters
res, idx = kmeans2(numpy.array(zip(xy[:,0],xy[:,1])),2)

print len(idx)
 
pres = []
sen = []

# plot colored points
for i, index in enumerate(idx):
	if index == 0:
		pres.append(xy[i])
	else:
		sen.append(xy[i])

pres = numpy.array(pres)
sen = numpy.array(sen)
print pres.shape
print sen.shape

fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(pres[:,0],pres[:,1], c=[0.4,1,0.4], label='president')
ax.scatter(sen[:,0],sen[:,1], c=[0.1,0.8,1], label='senator')
ax.legend()
plt.title('Barack Obama Toy Clusters')
 
# mark centroids as (X)
ax.scatter(res[:,0],res[:,1], marker='o', s = 500, linewidths=2, c='none')
ax.scatter(res[:,0],res[:,1], marker='x', s = 500, linewidths=2)
 
plt.savefig('/tmp/kmeans.png')
