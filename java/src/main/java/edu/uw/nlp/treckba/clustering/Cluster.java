package edu.uw.nlp.treckba.clustering;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Cluster {

	private final int name;
	private int count = 0;
	private float lambdaDecrease = ClusteringConstants.START_TIMELINESS;
	private float lambdaIncrease = ClusteringConstants.START_TIMELINESS;
	private final List<ClusterExample> examples = new LinkedList<>();
	private final float[] sum = new float[ClusteringConstants.EMBEDDING_DIM];
	private final Map<Integer, Float> sparseSum = new HashMap<Integer, Float>();
	private long timestamp;
	private final long T;

	public Cluster(final int name, final long timestamp, final long T) {
		this.name = name;
		this.timestamp = timestamp;
		this.T = T;
	}

	public int getName() {
		return name;
	}

	public float[] meanNormalized() {
		final float[] mean = new float[ClusteringConstants.EMBEDDING_DIM];
		for (int i = 0; i < mean.length; i++) {
			mean[i] = sum[i] / count;
		}
		return ClusteringUtils.normalize(mean);
	}

	public Map<Integer, Float> meanNormalizedSparse() {
		final Map<Integer, Float> mean = new HashMap<Integer, Float>();
		for (final Integer k : sparseSum.keySet()) {
			mean.put(k, sparseSum.get(k) / count);
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

	public void updateSum(final Map<Integer, Float> values) {
		final Set<Integer> vKeys = values.keySet();
		for (final Integer k : vKeys) {
			if (!sparseSum.containsKey(k)) {
				sparseSum.put(k, values.get(k));
			} else {
				sparseSum.put(k, values.get(k) + sparseSum.get(k));
			}
		}
	}

	public void addExample(final ClusterExample example) {
		examples.add(example);
	}

	public float getLambdaDecrease() {
		return lambdaDecrease;
	}

	public float getLambdaIncrease() {
		return lambdaIncrease;
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
		lambdaDecrease = lambdaIncrease * exp;
		return lambdaDecrease;
	}

	public void incrementLambda(final HyperParams params) {
		lambdaIncrease = 1 - (1 - lambdaDecrease) * params.getGammaIncrease();
	}
}
