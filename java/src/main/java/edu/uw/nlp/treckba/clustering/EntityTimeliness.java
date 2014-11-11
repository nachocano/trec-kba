package edu.uw.nlp.treckba.clustering;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.clustering.vis.pojo.Entity;
import edu.uw.nlp.treckba.clustering.vis.pojo.Staleness;

public class EntityTimeliness {

	private static final class TimeEntry {
		private final float timeliness;
		private final long timestamp;

		public TimeEntry(final float timeliness, final long timestamp) {
			this.timeliness = timeliness;
			this.timestamp = timestamp;
		}

		public float getTimeliness() {
			return timeliness;
		}

		public long getTimestamp() {
			return timestamp;
		}

		@Override
		public int hashCode() {
			final int prime = 31;
			int result = 1;
			result = prime * result + Float.floatToIntBits(timeliness);
			result = prime * result + (int) (timestamp ^ timestamp >>> 32);
			return result;
		}

		@Override
		public boolean equals(final Object obj) {
			if (this == obj) {
				return true;
			}
			if (obj == null) {
				return false;
			}
			if (getClass() != obj.getClass()) {
				return false;
			}
			final TimeEntry other = (TimeEntry) obj;
			if (Float.floatToIntBits(timeliness) != Float
					.floatToIntBits(other.timeliness)) {
				return false;
			}
			if (timestamp != other.timestamp) {
				return false;
			}
			return true;
		}

	}

	private final long T;

	public EntityTimeliness(final long timestampNormalizer) {
		this.T = timestampNormalizer;
	}

	public void computeTimeliness(final List<ClusterExample> examples,
			final HyperParams params, final Map<String, Entity> entities,
			final int intermediatePoints) {
		final Map<String, TimeEntry> timePerEntity = new HashMap<>();
		int left = examples.size();
		for (final ClusterExample ex : examples) {
			System.out.println("Left " + --left);
			final String targetId = ex.getTargetId();
			if (entities.get(targetId) == null) {
				continue;
			}
			if (!timePerEntity.containsKey(targetId)) {
				if (!ex.discard()) {
					ex.setEntityTimeliness(ClusteringConstants.START_TIMELINESS);
					timePerEntity.put(
							targetId,
							new TimeEntry(ex.getEntityTimeliness(), ex
									.getTimestamp()));
					entities.get(targetId).addStaleness(
							new Staleness(ex.getTimestamp(), ex
									.getEntityTimeliness()));
				}
			} else {
				if (!ex.discard()) {
					final long currentTimestamp = ex.getTimestamp();
					final long previousTimestamp = timePerEntity.get(targetId)
							.getTimestamp();
					final long tDiff = currentTimestamp - previousTimestamp;
					final float tDiffNorm = (float) tDiff / this.T;
					final float exp = (float) Math.exp(-params
							.getGammaDecrease() * tDiffNorm);
					// decay
					final float result = timePerEntity.get(targetId)
							.getTimeliness() * exp;
					// increase it
					final float newTimeliness = 1 - (1 - result)
							* params.getGammaIncrease();
					Validate.isTrue(newTimeliness >= 0 && newTimeliness <= 1);

					// also compute staleness for 9 points in between
					// repeated code, i don't care
					if (tDiff != 0) {
						long intermediateTimestamp = previousTimestamp
								+ intermediatePoints;
						System.out
								.println("Computing intermediate staleness...");
						int numberOfIntermediate = 0;
						while (intermediateTimestamp < currentTimestamp
								&& numberOfIntermediate < 100) {
							final long intDiff = currentTimestamp
									- intermediateTimestamp;
							final float intDiffNorm = (float) intDiff / this.T;
							final float intExp = (float) Math.exp(-params
									.getGammaDecrease() * intDiffNorm);
							// decay
							final float intermediateStaleness = timePerEntity
									.get(targetId).getTimeliness() * intExp;
							entities.get(targetId).addStaleness(
									new Staleness(intermediateTimestamp,
											intermediateStaleness));
							intermediateTimestamp += intermediatePoints;
							numberOfIntermediate++;
							System.out.println("intermediate "
									+ numberOfIntermediate + " staleness "
									+ intermediateStaleness);
						}
						System.out.println("Computed intermediate staleness");
					}
					// doing this after the intermediate calculations
					entities.get(targetId).addStaleness(
							new Staleness(currentTimestamp, result));
					ex.setEntityTimeliness(result);
					timePerEntity.put(targetId, new TimeEntry(newTimeliness,
							currentTimestamp));

				}
			}
		}
	}
}
