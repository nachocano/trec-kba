package edu.uw.nlp.treckba.clustering.viz;

import java.util.List;

public class ClusterVizDataObject {

	private float[] cluster;

	private List<float[]> clusters;

	public ClusterVizDataObject() {
	}

	public void setCluster(final float[] cluster) {
		this.cluster = cluster;
	}

	public void setClusters(final List<float[]> clusters) {
		this.clusters = clusters;
	}

	public float[] getCluster() {
		return cluster;
	}

	public List<float[]> getClusters() {
		return clusters;
	}

}
