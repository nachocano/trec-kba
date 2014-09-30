package edu.uw.nlp.treckba.clustering.viz;

import org.codehaus.jackson.annotate.JsonProperty;

public class ClusterViz {

	private int name;
	@JsonProperty("c_ij")
	private float[] emb;

	public ClusterViz() {
	}

	public ClusterViz(final int name, final float[] emb) {
		this.name = name;
		this.emb = emb;
	}

	public float[] getEmb() {
		return emb;
	}

	public void setEmb(final float[] emb) {
		this.emb = emb;
	}

	public int getName() {
		return name;
	}

	public void setName(final int name) {
		this.name = name;
	}

}
