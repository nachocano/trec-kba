package edu.uw.nlp.treckba.clustering.vis.pojo;

public class Cluster {

	private int id;
	private float[] words;

	public Cluster() {
	}

	public Cluster(final int id, final float[] emb) {
		this.id = id;
		this.words = emb;
	}

	public int getId() {
		return id;
	}

	public void setId(final int id) {
		this.id = id;
	}

	public float[] getWords() {
		return words;
	}

	public void setWords(final float[] emb) {
		this.words = emb;
	}

}
