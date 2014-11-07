package edu.uw.nlp.treckba.clustering.vis.pojo;

public class Cluster {

	private int id;
	private float[] emb;

	public Cluster() {
	}

	public Cluster(final int id, final float[] emb) {
		this.id = id;
		this.emb = emb;
	}

	public int getId() {
		return id;
	}

	public void setId(final int id) {
		this.id = id;
	}

	public float[] getEmb() {
		return emb;
	}

	public void setEmb(final float[] emb) {
		this.emb = emb;
	}

}
