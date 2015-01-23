package edu.uw.nlp.treckba.clustering;

import java.util.Map;
import java.util.Set;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

public class WordType {

	private final float[] array;
	private final Map<Integer, Float> sparse;
	private int allZeros;
	private float minDistance;
	private float avgDistance;
	private float lambdaDecrease;
	private float lambdaIncrease;

	public WordType(final float[] array) {
		this.array = array;
		this.sparse = null;
	}

	public WordType(final Map<Integer, Float> sparse) {
		this.sparse = sparse;
		this.array = null;
	}

	public boolean isZero() {
		if (array == null) {
			// is sparse
			final Set<Integer> keys = sparse.keySet();
			for (final int key : keys) {
				if (sparse.get(key) != 0) {
					return false;
				}
			}
		} else {
			for (final float element : array) {
				if (element != 0) {
					return false;
				}
			}
		}
		return true;
	}

	public float[] getArray() {
		return array;
	}

	public Map<Integer, Float> getSparse() {
		return sparse;
	}

	public int getAllZeros() {
		return allZeros;
	}

	public void setAllZeros(final int allZeros) {
		this.allZeros = allZeros;
	}

	public float getMinDistance() {
		return minDistance;
	}

	public void setMinDistance(final float minDistance) {
		this.minDistance = minDistance;
	}

	public float getAvgDistance() {
		return avgDistance;
	}

	public void setAvgDistance(final float avgDistance) {
		this.avgDistance = avgDistance;
	}

	public float getLambdaDecrease() {
		return lambdaDecrease;
	}

	public void setLambdaDecrease(final float lambdaDecrease) {
		this.lambdaDecrease = lambdaDecrease;
	}

	public float getLambdaIncrease() {
		return lambdaIncrease;
	}

	public void setLambdaIncrease(final float lambdaIncrease) {
		this.lambdaIncrease = lambdaIncrease;
	}

	@Override
	public boolean equals(final Object obj) {
		if (obj == this) {
			return true;
		}
		if (!(obj instanceof WordType)) {
			return false;
		}
		final WordType that = (WordType) obj;
		return new EqualsBuilder().append(this.array, that.array)
				.append(this.sparse, that.sparse)
				.append(this.minDistance, that.minDistance)
				.append(this.avgDistance, that.avgDistance)
				.append(this.lambdaDecrease, that.lambdaDecrease)
				.append(this.lambdaIncrease, that.lambdaIncrease)
				.append(this.allZeros, that.allZeros).isEquals();
	}

	@Override
	public int hashCode() {
		return new HashCodeBuilder(17, 37).append(array).append(sparse)
				.append(minDistance).append(avgDistance).append(lambdaDecrease)
				.append(lambdaIncrease).append(allZeros).toHashCode();
	}

	public String featuresToString() {
		final StringBuilder sb = new StringBuilder().append(minDistance)
				.append(ClusteringConstants.WHITE_SPACE).append(avgDistance)
				.append(ClusteringConstants.WHITE_SPACE).append(lambdaDecrease)
				.append(ClusteringConstants.WHITE_SPACE).append(allZeros);
		return sb.toString();

	}

	public String arrayToString() {
		final StringBuilder sb = new StringBuilder().append(array[0]);
		for (int i = 1; i < array.length; i++) {
			sb.append(ClusteringConstants.WHITE_SPACE).append(array[i]);
		}
		return sb.toString();
	}

	public String sparseToString() {
		final StringBuilder sb = new StringBuilder();
		final Set<Integer> keys = sparse.keySet();
		int i = 0;
		for (final int key : keys) {
			if (i != 0) {
				sb.append(ClusteringConstants.WHITE_SPACE);
			}
			sb.append(key + "," + sparse.get(key));
			i++;
		}
		return sb.toString();
	}
}
