package edu.uw.nlp.treckba.clustering;

public class HyperParams {

	private float alpha;
	private float gammaIncrease;
	private float gammaDecrease;

	public HyperParams(final float alpha, final float gammaIncrease,
			final float gammaDecrease) {
		this.alpha = alpha;
		this.gammaIncrease = gammaIncrease;
		this.gammaDecrease = gammaDecrease;
	}

	public void setAlpha(final float alpha) {
		this.alpha = alpha;
	}

	public void setGammaIncrease(final float gammaIncrease) {
		this.gammaIncrease = gammaIncrease;
	}

	public void setGammaDecrease(final float gammaDecrease) {
		this.gammaDecrease = gammaDecrease;
	}

	public float getAlpha() {
		return alpha;
	}

	public float getGammaIncrease() {
		return gammaIncrease;
	}

	public float getGammaDecrease() {
		return gammaDecrease;
	}

}
