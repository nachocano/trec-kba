package edu.uw.nlp.treckba.clustering;

import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Callable;

public class ClusteringFeatureTask implements Callable<ClusteringOutput> {

	private final List<ClusterExample> train;
	private final List<ClusterExample> test;
	private final String targetId;
	private final List<Cluster> verbs;
	private final List<Cluster> nouns;
	private final HyperParams nounsParams;
	private final HyperParams verbsParams;
	private final long timestampNormalizer;

	public ClusteringFeatureTask(final String targetId,
			final List<ClusterExample> train, final List<ClusterExample> test,
			final HyperParams nounsParams, final HyperParams verbsParams,
			final long timestampNormalizer) {
		this.targetId = targetId;
		this.train = train;
		this.test = test;
		this.verbs = new LinkedList<>();
		this.nouns = new LinkedList<>();
		this.nounsParams = nounsParams;
		this.verbsParams = verbsParams;
		this.timestampNormalizer = timestampNormalizer;
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
		return new ClusteringOutput(targetId, nouns, verbs);
	}

	private void doProcess(final List<ClusterExample> set, final String str) {
		int left = set.size();
		for (final ClusterExample example : set) {
			left -= 1;
			System.out.println(String.format("processing %s for %s, %d left",
					str, targetId, left));
			populateFeatures(verbs, example, example.getVerbs(), verbsParams,
					timestampNormalizer);
			populateFeatures(nouns, example, example.getNouns(), nounsParams,
					timestampNormalizer);

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
			// timeliness to zero, doesn't belong to any cluster
			exampleWordType.setTimeliness(0);
		} else {
			if (clusters.isEmpty()) {
				// create a new cluster, and add the example to it
				final Cluster c = new Cluster(example.getTimestamp(),
						timestampNormalizer);
				c.updateSum(exampleWordType.getArray());
				c.incrementCount();
				c.addExample(example);
				clusters.add(c);
				// allZeros=0, minDistance=0, avgDistance=0, timeliness=0.5
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
						exampleWordType.setTimeliness(result);
						nearestCluster.incrementTimeliness(result, params);
						nearestCluster.setTimestamp(example.getTimestamp());
					}
				} else {
					// create a new cluster, and add the example to it
					final Cluster c = new Cluster(example.getTimestamp(),
							timestampNormalizer);
					c.updateSum(exampleWordType.getArray());
					c.incrementCount();
					c.addExample(example);
					clusters.add(c);
					// allZeros=0, minDistance=0, avgDistance=0, timeliness=0.5
					exampleWordType.setTimeliness(c.getTimeliness());
				}
			}
		}

		return null;
	}

}
