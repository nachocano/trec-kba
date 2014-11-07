package edu.uw.nlp.treckba.clustering.vis.pojo;

public class Document {

	private long time;
	private String id;

	public Document(final String id, final long timestamp) {
		this.time = timestamp;
		this.id = id;
	}

	public Document() {
	}

	public long getTime() {
		return time;
	}

	public void setTime(final long time) {
		this.time = time;
	}

	public String getId() {
		return id;
	}

	public void setId(final String id) {
		this.id = id;
	}

}
