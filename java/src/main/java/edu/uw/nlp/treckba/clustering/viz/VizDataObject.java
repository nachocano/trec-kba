package edu.uw.nlp.treckba.clustering.viz;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import org.codehaus.jackson.annotate.JsonIgnoreProperties;
import org.codehaus.jackson.annotate.JsonProperty;

import edu.uw.nlp.treckba.clustering.Cluster;
import edu.uw.nlp.treckba.clustering.ClusterExample;

//@JsonIgnoreProperties({ "di", "clusters", "streamids" })
@JsonIgnoreProperties({ "score", "relevance", "lambdas" })
public class VizDataObject {

	private long timestamp;
	private int score;
	private int relevance;
	@JsonProperty("di")
	private float[] document;
	@JsonProperty("streamid")
	private String streamId;

	@JsonProperty("ci")
	private int clusterName;

	private List<ClusterViz> clusters;

	private List<String> streamids;

	@JsonProperty("lambdas")
	private List<Lambda> staleness;

	public VizDataObject() {
		clusters = new LinkedList<>();
		staleness = new LinkedList<>();
	}

	public void setClusters(final List<ClusterViz> c) {
		this.clusters = c;
	}

	public void setRelevance(final int relevance) {
		this.relevance = relevance;
	}

	public void setStaleness(final List<Lambda> s) {
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
			final float[] document, final int score) {
		this.score = -1;
		this.streamId = streamId;
		this.timestamp = timestamp;
		this.document = document;
		this.clusters = new LinkedList<>();
		this.staleness = new LinkedList<>();
	}

	public void setScore(final int score) {
		this.score = score;
	}

	public void setClusterName(final int clusterName) {
		this.clusterName = clusterName;
	}

	public void updateClustersAndStalenesses(final Cluster clu) {
		// for (final Cluster clu : cs) {
		this.clusters.add(new ClusterViz(clu.getName(), clu.meanNormalized()));
		staleness.add(new Lambda(clu.getName(), clu.getLambdaDecrease(), clu
				.getLambdaIncrease()));
		final List<String> sids = new ArrayList<>();
		for (final ClusterExample ce : clu.getExamples()) {
			sids.add(ce.getStreamId());
		}
		this.streamids = sids;
		// }
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

	public List<ClusterViz> getClusters() {
		return clusters;
	}

	public List<Lambda> getStaleness() {
		return staleness;
	}

	public int getRelevance() {
		return relevance;
	}

	public int getClusterName() {
		return clusterName;
	}

	public void setStreamIds(final List<String> streamIds) {
		this.streamids = streamIds;
	}

	public List<String> getStreamIds() {
		return this.streamids;
	}

}
