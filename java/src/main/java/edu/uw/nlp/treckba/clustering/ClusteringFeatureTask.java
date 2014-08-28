package edu.uw.nlp.treckba.clustering;

import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Callable;

public class ClusteringFeatureTask implements Callable<Void> {

	private final List<ClusterExample> train;
	private final List<ClusterExample> test;
	private final String targetId;
	private final List<Cluster> verbs;
	private final List<Cluster> nouns;
	private final HyperParams nounsParams;
	private final HyperParams verbsParams;

	public ClusteringFeatureTask(final String targetId,
			final List<ClusterExample> train, final List<ClusterExample> test,
			final HyperParams nounsParams, final HyperParams verbsParams) {
		this.targetId = targetId;
		this.train = train;
		this.test = test;
		this.verbs = new LinkedList<>();
		this.nouns = new LinkedList<>();
		this.nounsParams = nounsParams;
		this.verbsParams = verbsParams;
	}

	@Override
	public Void call() throws Exception {
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
		return null;
	}

	private void doProcess(final List<ClusterExample> set, final String str) {
		int left = set.size();
		for (final ClusterExample example : set) {
			left -= 1;
			System.out.println(String.format("processing %s for %s, %d left",
					str, targetId, left));
			populateFeatures(verbs, example, example.getVerbs(), verbsParams);
			populateFeatures(nouns, example, example.getNouns(), nounsParams);

		}
	}

	private float[] populateFeatures(final List<Cluster> clusters,
			final ClusterExample example, final WordType exampleWordType,
			final HyperParams params) {
		if (exampleWordType.isZero()) {
			// do not put it in any cluster
			exampleWordType.setAllZeros(1);
			exampleWordType.setMinDistance(1);
			exampleWordType.setAvgDistance(1);
			// timeliness to zero, doesn't belong to any cluster
			exampleWordType.setTimeliness(0);
		} else {
			if (clusters.isEmpty()) {
				// create a new cluster, and add the example to it
				final Cluster c = new Cluster();
				c.updateSum(exampleWordType.getArray());
				c.incrementCount();
				c.addExample(example);
				clusters.add(c);
				// allZeros=0, minDistance=0, avgDistance=0
				exampleWordType.setTimeliness(c.getTimeliness());
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
					// put the example in an existent cluster
					nearestCluster.addExample(example);
					nearestCluster.updateSum(exampleWordType.getArray());
					nearestCluster.incrementCount();
					updateTimeliness(clusters, nearestCluster, params);
					exampleWordType.setTimeliness(nearestCluster.getTimeliness());
				} else {
					// create a new cluster, and add the example to it
					final Cluster c = new Cluster();
					c.updateSum(exampleWordType.getArray());
					c.incrementCount();
					c.addExample(example);
					clusters.add(c);
					// allZeros=0, minDistance=0, avgDistance=0
					exampleWordType.setTimeliness(c.getTimeliness());
				}
			}
		}

		return null;
	}

	private void updateTimeliness(final List<Cluster> clusters,
			final Cluster nearestCluster, final HyperParams params) {
		for (final Cluster cluster : clusters) {
			if (cluster.equals(nearestCluster)) {
				cluster.incrementTimeliness(params.getGammaIncrease());
			} else {
				cluster.decrementTimeliness(params.getGammaDecrease());
			}
		}

	}
}