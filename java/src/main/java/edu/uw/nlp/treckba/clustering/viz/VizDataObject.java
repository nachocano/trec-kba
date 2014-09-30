package edu.uw.nlp.treckba.clustering.viz;

import java.util.LinkedList;
import java.util.List;

import org.codehaus.jackson.annotate.JsonProperty;

import edu.uw.nlp.treckba.clustering.Cluster;

public class VizDataObject {

	private long timestamp;
	private int score;
	private int relevance;
	@JsonProperty("d_i")
	private float[] document;
	@JsonProperty("streamid")
	private String streamId;

	@JsonProperty("clusters")
	private ClusterVizDataObject cluster;
	@JsonProperty("lambdas")
	private StalenessVizDataObject staleness;

	public VizDataObject() {
	}

	public void setCluster(final ClusterVizDataObject c) {
		this.cluster = c;
	}

	public void setRelevance(final int relevance) {
		this.relevance = relevance;
	}

	public void setStaleness(final StalenessVizDataObject s) {
		this.staleness = s;
	}

	public void setTimestamp(final long timestamp) {
		this.timestamp = timestamp;
	}

	public void setDocument(final float[] document) {
		this.document = document;
	}

	public void setStreamId(final String streamId) {
		this.streamId = streamId;
	}

	public VizDataObject(final String streamId, final long timestamp,
			final float[] document) {
		this.streamId = streamId;
		this.timestamp = timestamp;
		this.document = document;
		this.cluster = new ClusterVizDataObject();
		this.staleness = new StalenessVizDataObject();
	}

	public void setScore(final int score) {
		this.score = score;
	}

	public void updateStaleness(final float lambdaDecrease,
			final float lambdaIncrease) {
		staleness.setLambda(new Lambda(lambdaDecrease, lambdaIncrease));
	}

	public void updateCluster(final Cluster c) {
		cluster.setCluster(new ClusterViz(c.getName(), c.meanNormalized()));
	}

	public void updateClustersAndStalenesses(final List<Cluster> clusters,
			final Cluster c) {
		final List<ClusterViz> clustersEmbeddings = new LinkedList<>();
		final List<Lambda> lambdas = new LinkedList<>();
		for (final Cluster clu : clusters) {
			// use the object identity
			if (c != clu) {
				clustersEmbeddings.add(new ClusterViz(clu.getName(), clu
						.meanNormalized()));
				lambdas.add(new Lambda(clu.getLambdaDecrease(), clu
						.getLambdaIncrease()));
			}
		}
		cluster.setClusters(clustersEmbeddings);
		staleness.setLambdas(lambdas);
	}

	public long getTimestamp() {
		return timestamp;
	}

	public int getScore() {
		return score;
	}

	public float[] getDocument() {
		return document;
	}

	public String getStreamId() {
		return streamId;
	}

	public ClusterVizDataObject getCluster() {
		return cluster;
	}

	public StalenessVizDataObject getStaleness() {
		return staleness;
	}

	public int getRelevance() {
		return relevance;
	}

}
