package edu.uw.nlp.treckba.clustering;

import java.util.LinkedList;
import java.util.List;

public class Cluster {

	private int count = 0;
	private float timeliness = ClusteringConstants.START_TIMELINESS;
	private final List<ClusterExample> examples = new LinkedList<>();
	private final float[] sum = new float[ClusteringConstants.EMBEDDING_DIM];
	private long timestamp;
	private final long T;

	public Cluster(final long timestamp, final long T) {
		this.timestamp = timestamp;
		this.T = T;
	}

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

	public void addExample(final ClusterExample example) {
		examples.add(example);
	}

	public float getTimeliness() {
		return timeliness;
	}

	public long getTimestamp() {
		return timestamp;
	}

	public void setTimestamp(final long timestamp) {
		this.timestamp = timestamp;
	}

	public List<ClusterExample> getExamples() {
		return this.examples;
	}

	public float decay(final ClusterExample example, final HyperParams params) {
		// perform the decay
		final long t = example.getTimestamp();
		final long tDiff = t - this.timestamp;
		if (tDiff < 0) {
			return -1.0f;
		}
		final float tDiffNorm = (float) tDiff / this.T;
		final float exp = (float) Math.exp(-params.getGammaDecrease()
				* tDiffNorm);
		final float result = timeliness * exp;
		return result;
	}

	public void incrementTimeliness(final float result, final HyperParams params) {
		timeliness = 1 - (1 - result) * params.getGammaIncrease();
	}
}
