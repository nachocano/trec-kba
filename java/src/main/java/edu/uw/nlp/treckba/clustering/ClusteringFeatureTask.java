package edu.uw.nlp.treckba.clustering;

import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Callable;

import edu.uw.nlp.treckba.clustering.viz.VizDataObject;

public class ClusteringFeatureTask implements Callable<ClusteringOutput> {

	private final List<ClusterExample> train;
	private final List<ClusterExample> test;
	private final String targetId;
	private final List<Cluster> verbs;
	private final List<Cluster> nouns;
	private final List<Cluster> properNouns;
	private final HyperParams nounsParams;
	private final HyperParams verbsParams;
	private final long timestampNormalizer;
	private final List<VizDataObject> vizDataObjects;
	private final boolean vizEnabled;

	public ClusteringFeatureTask(final String targetId,
			final List<ClusterExample> train, final List<ClusterExample> test,
			final HyperParams nounsParams, final HyperParams verbsParams,
			final long timestampNormalizer,
			final List<VizDataObject> vizDataObjects) {
		this.targetId = targetId;
		this.train = train;
		this.test = test;
		this.verbs = new LinkedList<>();
		this.nouns = new LinkedList<>();
		this.properNouns = new LinkedList<>();
		this.nounsParams = nounsParams;
		this.verbsParams = verbsParams;
		this.timestampNormalizer = timestampNormalizer;
		this.vizDataObjects = vizDataObjects;
		this.vizEnabled = vizDataObjects != null;
	}

	@Override
	public ClusteringOutput call() throws Exception {
		final long start = System.currentTimeMillis();
		try {
			System.out.println("processing " + targetId);
			doProcess(train, "train");
			doProcess(test, "test");
		} catch (final Exception exc) {
			System.out.println("error: exception processing " + targetId
					+ ". msg " + exc.getMessage());
		} finally {
			System.out.println(String.format("finished processing %s, took %s",
					targetId, (System.currentTimeMillis() - start) / 1000));

		}
		return new ClusteringOutput(targetId, nouns, verbs, properNouns);
	}

	private void doProcess(final List<ClusterExample> set, final String str) {
		int left = set.size();
		for (final ClusterExample example : set) {
			left -= 1;
			System.out.println(String.format("processing %s for %s, %d left",
					str, targetId, left));
			// populateFeatures(verbs, example, example.getVerbs(), verbsParams,
			// timestampNormalizer);
			populateFeatures(nouns, example, example.getNouns(), nounsParams,
					timestampNormalizer);
			// populateFeatures(properNouns, example, example.getProperNouns(),
			// nounsParams, timestampNormalizer);

		}
	}

	private float[] populateFeatures(final List<Cluster> clusters,
			final ClusterExample example, final WordType exampleWordType,
			final HyperParams params, final long timestampNormalizer) {
		if (exampleWordType.isZero()) {
			// do not put it in any cluster
			exampleWordType.setAllZeros(1);
			exampleWordType.setMinDistance(1);
			exampleWordType.setAvgDistance(1);
			// lambdas to zero, doesn't belong to any cluster, TODO check
			exampleWordType.setLambdaDecrease(0);
			exampleWordType.setLambdaIncrease(0);
		} else {
			VizDataObject vizObject = null;
			if (vizEnabled) {
				vizObject = new VizDataObject(example.getStreamId(),
						example.getTimestamp(), exampleWordType.getArray());
				vizObject.setRelevance(example.getRelevance());
			}
			if (clusters.isEmpty()) {
				// create a new cluster, and add the example to it
				final Cluster c = new Cluster(example.getTimestamp(),
						timestampNormalizer);
				c.updateSum(exampleWordType.getArray());
				c.incrementCount();
				c.addExample(example);
				clusters.add(c);
				// allZeros=0, minDistance=0, avgDistance=0, lambdaDec=0.5,
				// lambdaInc=0.5
				exampleWordType.setLambdaDecrease(c.getLambdaDecrease());
				exampleWordType.setLambdaIncrease(c.getLambdaIncrease());
				if (vizEnabled) {
					// no need to set other stuff, cause is the only one in the
					// cluster
					vizObject.updateStaleness(c.getLambdaDecrease(),
							c.getLambdaIncrease());
					vizObject.updateCluster(c);
				}
			} else {
				float maxSimilarity = Float.MIN_VALUE;
				float similaritiesSum = 0;
				Cluster nearestCluster = null;
				for (final Cluster c : clusters) {
					// this may take time, try to profile it
					final float sim = ClusteringUtils.dotProduct(
							c.meanNormalized(), exampleWordType.getArray());
					similaritiesSum += sim;
					if (sim > maxSimilarity) {
						maxSimilarity = sim;
						nearestCluster = c;
					}
				}
				// two new features
				final float minDistance = 1 - maxSimilarity;
				final float avgDistance = 1 - similaritiesSum / clusters.size();
				exampleWordType.setMinDistance(minDistance);
				exampleWordType.setAvgDistance(avgDistance);

				if (minDistance < params.getAlpha()) {
					final float result = nearestCluster.decay(example, params);
					// if result is -1 is because there were some unassessed
					// test docs that should have been part of train,
					// their timestamp is before
					if (result == -1.0f) {
						example.setDiscardFlag(true);
					} else {
						// put the example in an existent cluster
						nearestCluster.addExample(example);
						nearestCluster.updateSum(exampleWordType.getArray());
						nearestCluster.incrementCount();
						nearestCluster.incrementLambda(params);
						nearestCluster.setTimestamp(example.getTimestamp());
						exampleWordType.setLambdaDecrease(nearestCluster
								.getLambdaDecrease());
						exampleWordType.setLambdaIncrease(nearestCluster
								.getLambdaIncrease());
						if (vizEnabled) {
							vizObject.updateStaleness(
									exampleWordType.getLambdaDecrease(),
									exampleWordType.getLambdaIncrease());
							vizObject.updateCluster(nearestCluster);
							vizObject.updateClustersAndStalenesses(clusters,
									nearestCluster);
						}
					}
				} else {
					// create a new cluster, and add the example to it
					final Cluster c = new Cluster(example.getTimestamp(),
							timestampNormalizer);
					c.updateSum(exampleWordType.getArray());
					c.incrementCount();
					c.addExample(example);
					clusters.add(c);
					// allZeros=0, minDistance=0, avgDistance=0, lambdaDec=0.5,
					// lambdaInc=0.5
					exampleWordType.setLambdaDecrease(c.getLambdaDecrease());
					exampleWordType.setLambdaIncrease(c.getLambdaIncrease());
					if (vizEnabled) {
						vizObject.updateStaleness(
								exampleWordType.getLambdaDecrease(),
								exampleWordType.getLambdaIncrease());
						vizObject.updateCluster(c);
						vizObject.updateClustersAndStalenesses(clusters, c);
					}
				}
			}
			if (vizEnabled) {
				vizDataObjects.add(vizObject);
			}
		}
		return null;
	}
}
