package edu.uw.nlp.treckba.clustering.viz;

import java.util.LinkedList;
import java.util.List;

import org.codehaus.jackson.annotate.JsonProperty;

public class StalenessVizDataObject {

	@JsonProperty("lambda_i")
	private Lambda lambda;
	@JsonProperty("lambda_ijs")
	private List<Lambda> lambdas;

	public StalenessVizDataObject() {
		lambdas = new LinkedList<>();
	}

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
