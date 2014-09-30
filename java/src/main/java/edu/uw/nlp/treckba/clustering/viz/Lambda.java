package edu.uw.nlp.treckba.clustering.viz;

import org.codehaus.jackson.annotate.JsonProperty;

public class Lambda {

	@JsonProperty("inc")
	private float lambdaInc;
	@JsonProperty("dec")
	private float lambdaDec;

	public Lambda() {
	}

	public Lambda(final float lambdaDec, final float lambdaInc) {
		this.lambdaDec = lambdaDec;
		this.lambdaInc = lambdaInc;
	}

	public void setLambdaInc(final float lambdaInc) {
		this.lambdaInc = lambdaInc;
	}

	public void setLambdaDec(final float lambdaDec) {
		this.lambdaDec = lambdaDec;
	}

	public float getLambdaInc() {
		return lambdaInc;
	}

	public float getLambdaDec() {
		return lambdaDec;
	}

}
