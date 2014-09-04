package edu.uw.nlp.treckba.clustering;

import java.util.List;

import org.apache.commons.lang3.Validate;

public class CorpusTimeliness {

	private final long T;

	public CorpusTimeliness(final long timestampNormalizer) {
		this.T = timestampNormalizer;
	}

	public void computeTimeliness(final List<ClusterExample> examples,
			final HyperParams params) {
		final ClusterExample ex = examples.get(0);
		float timeliness = ClusteringConstants.START_TIMELINESS;
		ex.setGlobalTimeliness(timeliness);
		long timestamp = ex.getTimestamp();
		for (int i = 1; i < examples.size(); i++) {
			final ClusterExample currentExample = examples.get(i);
			if (!currentExample.discard()) {
				final long currentTimestamp = currentExample.getTimestamp();
				final long tDiff = currentTimestamp - timestamp;
				final float tDiffNorm = (float) tDiff / this.T;
				final float exp = (float) Math.exp(-params.getGammaDecrease()
						* tDiffNorm);
				final float result = timeliness * exp;
				currentExample.setGlobalTimeliness(result);
				timeliness = 1 - (1 - result) * params.getGammaIncrease();
				Validate.isTrue(timeliness >= 0 && timeliness <= 1);
				timestamp = currentTimestamp;
			}
		}
	}

}
