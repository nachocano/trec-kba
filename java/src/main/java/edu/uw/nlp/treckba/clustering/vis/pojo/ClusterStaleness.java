package edu.uw.nlp.treckba.clustering.vis.pojo;

public class ClusterStaleness {

	private int cluster;
	private long time;
	private float value;

	public ClusterStaleness() {
	}

	public ClusterStaleness(final int clusterName, final long timestamp,
			final float lambdaDecrease) {
		this.cluster = clusterName;
		this.time = timestamp;
		this.value = lambdaDecrease;
	}

	public int getCluster() {
		return cluster;
	}

	public void setCluster(final int cluster) {
		this.cluster = cluster;
	}

	public long getTime() {
		return time;
	}

	public void setTime(final long time) {
		this.time = time;
	}

	public double getValue() {
		return value;
	}

	public void setValue(final float value) {
		this.value = value;
	}

}
