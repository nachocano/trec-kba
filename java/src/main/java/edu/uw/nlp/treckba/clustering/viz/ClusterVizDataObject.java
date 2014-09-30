package edu.uw.nlp.treckba.clustering.viz;

import java.util.LinkedList;
import java.util.List;

import org.codehaus.jackson.annotate.JsonProperty;

public class ClusterVizDataObject {

	@JsonProperty("c_i")
	private ClusterViz cluster;
	@JsonProperty("c_ijs")
	private List<ClusterViz> clusters;

	public ClusterVizDataObject() {
		clusters = new LinkedList<>();
	}

	public void setCluster(final ClusterViz cluster) {
		this.cluster = cluster;
	}

	public void setClusters(final List<ClusterViz> clusters) {
		this.clusters = clusters;
	}

	public ClusterViz getCluster() {
		return cluster;
	}

	public List<ClusterViz> getClusters() {
		return clusters;
	}

}
