package edu.uw.nlp.treckba.clustering.viz;

import java.util.List;

public class StalenessVizDataObject {

	private Lambda lambda;

	private List<Lambda> lambdas;

	public Lambda getLambda() {
		return lambda;
	}

	public void setLambda(final Lambda lambda) {
		this.lambda = lambda;
	}

	public void setLambdas(final List<Lambda> lambdas) {
		this.lambdas = lambdas;
	}

	public List<Lambda> getLambdas() {
		return lambdas;
	}

}
