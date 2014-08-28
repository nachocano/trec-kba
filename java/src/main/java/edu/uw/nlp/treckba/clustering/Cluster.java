package edu.uw.nlp.treckba.clustering;

import java.util.LinkedList;
import java.util.List;

public class Cluster {

	private int count = 0;
	private float timeliness = ClusteringConstants.START_TIMELINESS;
	private final List<ClusterExample> examples = new LinkedList<>();
	private final float[] sum = new float[ClusteringConstants.EMBEDDING_DIM];

	public float[] meanNormalized() {
		final float[] mean = new float[ClusteringConstants.EMBEDDING_DIM];
		for (int i = 0; i < mean.length; i++) {
			mean[i] = sum[i] / count;
		}
		return ClusteringUtils.normalize(mean);
	}

	public void incrementCount() {
		count++;
	}

	public void updateSum(final float[] values) {
		for (int i = 0; i < sum.length; i++) {
			sum[i] += values[i];
		}
	}

	public void incrementTimeliness(final float gammaIncrease) {
		timeliness = 1 - (1 - timeliness) * gammaIncrease;
	}

	public void decrementTimeliness(final float gammaDecrease) {
		timeliness *= gammaDecrease;
	}

	public void addExample(final ClusterExample example) {
		examples.add(example);
	}

	public float getTimeliness() {
		return timeliness;
	}

}
