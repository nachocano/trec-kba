package edu.uw.nlp.treckba.clustering.vis.pojo;

import java.util.ArrayList;
import java.util.List;

import org.codehaus.jackson.annotate.JsonIgnoreProperties;
import org.codehaus.jackson.annotate.JsonProperty;

@JsonIgnoreProperties({ "cluster_staleness" })
public class Entity {

	private String id;
	private List<Staleness> staleness;
	@JsonProperty("cluster_staleness")
	private List<ClusterStaleness> clusterStaleness;
	private List<Document> docs;

	public Entity() {
		this(null);
	}

	public Entity(final String id) {
		this.id = id;
		staleness = new ArrayList<>();
		docs = new ArrayList<>();
		clusterStaleness = new ArrayList<>();
	}

	public String getId() {
		return id;
	}

	public void setId(final String id) {
		this.id = id;
	}

	public List<Staleness> getStaleness() {
		return staleness;
	}

	public void setStaleness(final List<Staleness> staleness) {
		this.staleness = staleness;
	}

	public void setClusterStaleness(
			final List<ClusterStaleness> clusterStaleness) {
		this.clusterStaleness = clusterStaleness;
	}

	public List<ClusterStaleness> getClusterStaleness() {
		return this.clusterStaleness;
	}

	public List<Document> getDocs() {
		return docs;
	}

	public void setDocs(final List<Document> docs) {
		this.docs = docs;
	}

	public void addDocument(final Document document) {
		this.docs.add(document);
	}

	public void addStaleness(final Staleness staleness) {
		this.staleness.add(staleness);

	}

	public void addClusterStaleness(final ClusterStaleness staleness) {
		this.clusterStaleness.add(staleness);

	}

}
