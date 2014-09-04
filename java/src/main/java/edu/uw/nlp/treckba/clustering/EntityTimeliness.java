package edu.uw.nlp.treckba.clustering;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.Validate;

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
			final HyperParams params) {
		final Map<String, TimeEntry> timePerEntity = new HashMap<>();
		for (final ClusterExample ex : examples) {
			final String targetId = ex.getTargetId();
			if (!timePerEntity.containsKey(targetId)) {
				if (!ex.discard()) {
					ex.setEntityTimeliness(ClusteringConstants.START_TIMELINESS);
					timePerEntity.put(
							targetId,
							new TimeEntry(ex.getEntityTimeliness(), ex
									.getTimestamp()));
				}
			} else {
				if (!ex.discard()) {
					final long currentTimestamp = ex.getTimestamp();
					final long tDiff = currentTimestamp
							- timePerEntity.get(targetId).getTimestamp();
					final float tDiffNorm = (float) tDiff / this.T;
					final float exp = (float) Math.exp(-params
							.getGammaDecrease() * tDiffNorm);
					// decay
					final float result = timePerEntity.get(targetId)
							.getTimeliness() * exp;
					ex.setEntityTimeliness(result);
					// increase it
					final float newTimeliness = 1 - (1 - result)
							* params.getGammaIncrease();
					Validate.isTrue(newTimeliness >= 0 && newTimeliness <= 1);
					timePerEntity.put(targetId, new TimeEntry(newTimeliness,
							currentTimestamp));
				}
			}
		}
	}

}
