package edu.uw.nlp.treckba.clustering;

import java.util.List;

public class ClusteringOutput {

	private final String targetId;
	private final List<Cluster> nounClusters;
	private final List<Cluster> verbClusters;

	public ClusteringOutput(final String targetId,
			final List<Cluster> nounClusters, final List<Cluster> verbClusters) {
		this.targetId = targetId;
		this.nounClusters = nounClusters;
		this.verbClusters = verbClusters;
	}

	public String getTargetId() {
		return targetId;
	}

	public List<Cluster> getNounClusters() {
		return nounClusters;
	}

	public List<Cluster> getVerbClusters() {
		return verbClusters;
	}

}
