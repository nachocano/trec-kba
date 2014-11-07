package edu.uw.nlp.treckba.clustering.vis.pojo;

public class Staleness {

	private long time;
	private float value;

	public Staleness(final long timestamp, final float lambdaDecrease) {
		this.time = timestamp;
		this.value = lambdaDecrease;
	}

	public long getTime() {
		return time;
	}

	public void setTime(final long time) {
		this.time = time;
	}

	public double getValue() {
		return value;
	}

	public void setValue(final float value) {
		this.value = value;
	}

}
