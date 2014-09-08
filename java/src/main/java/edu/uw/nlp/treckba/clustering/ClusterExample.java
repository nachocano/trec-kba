package edu.uw.nlp.treckba.clustering;

import static edu.uw.nlp.treckba.clustering.ClusteringConstants.BUCKETS;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

import edu.uw.nlp.treckba.utils.Utils;

public class ClusterExample {

	private final String streamId;
	private final String targetId;
	private final String dateHour;
	private final int relevance;
	private final long timestamp;
	private float[] features;
	private WordType verbs;
	private WordType nouns;
	// discard flag, not to include it in the output...
	// should have used folder <= training_end_range instead of strictly <. Some
	// unassessed test docs should be part of unassessed train.
	private boolean discardFlag;
	private float entityTimeliness;
	private final int[] preMentions;
	private final int[] dayOfWeek;

	public ClusterExample(final String streamId, final String targetId,
			final String dateHour, final int relevance) {
		this.streamId = streamId;
		this.targetId = targetId;
		this.dateHour = dateHour;
		this.relevance = relevance;
		this.timestamp = Long.valueOf(this.streamId.split("-")[0]);
		this.preMentions = new int[BUCKETS];
		this.dayOfWeek = new int[7];
	}

	public void setNouns(final WordType nouns) {
		this.nouns = nouns;
	}

	public void setVerbs(final WordType verbs) {
		this.verbs = verbs;

	}

	public void setFeatures(final float[] features) {
		this.features = features;
	}

	@Override
	public boolean equals(final Object obj) {
		if (obj == this) {
			return true;
		}
		if (!(obj instanceof ClusterExample)) {
			return false;
		}
		final ClusterExample that = (ClusterExample) obj;
		return new EqualsBuilder().append(this.streamId, that.streamId)
				.append(this.targetId, that.targetId)
				.append(this.dateHour, that.dateHour).isEquals();
	}

	@Override
	public int hashCode() {
		return new HashCodeBuilder(17, 37).append(this.streamId)
				.append(this.targetId).append(this.dateHour).toHashCode();
	}

	public String getDateHour() {
		return dateHour;
	}

	public String getStreamId() {
		return streamId;
	}

	public String getTargetId() {
		return targetId;
	}

	public int getRelevance() {
		return relevance;
	}

	public long getTimestamp() {
		return timestamp;
	}

	public float[] getFeatures() {
		return features;
	}

	public WordType getVerbs() {
		return verbs;
	}

	public WordType getNouns() {
		return nouns;
	}

	public void setDiscardFlag(final boolean discardFlag) {
		this.discardFlag = discardFlag;
	}

	public boolean discard() {
		return this.discardFlag;
	}

	@Override
	public String toString() {
		final StringBuilder sb = new StringBuilder(streamId)
				.append(ClusteringConstants.WHITE_SPACE).append(targetId)
				.append(ClusteringConstants.WHITE_SPACE).append(dateHour)
				.append(ClusteringConstants.WHITE_SPACE).append(relevance)
				.append(ClusteringConstants.WHITE_SPACE).append(features[0]);
		for (int i = 1; i < features.length; i++) {
			sb.append(ClusteringConstants.WHITE_SPACE).append(features[i]);
		}
		final String nounsArrayAsStr = nouns.arrayToString();
		final String verbsArrayAsStr = verbs.arrayToString();
		final String nounsFeaturesAsStr = nouns.featuresToString();
		final String verbsFeaturesAsStr = verbs.featuresToString();
		final String entityTimelinessAsStr = String.format("%.5f",
				entityTimeliness);
		final String preMentionsAsStr = preMentionsToString();
		final String dayOfWeekAsString = dayOfWeekToString();

		// return String.format("%s %s %s %s %s %s", sb.toString(),
		// nounsArrayAsStr, verbsArrayAsStr, nounsFeaturesAsStr,
		// verbsFeaturesAsStr, entityTimelinessAsStr);

		return String.format("%s %s %s %s %s %s %s %s", sb.toString(),
				nounsArrayAsStr, verbsArrayAsStr, nounsFeaturesAsStr,
				verbsFeaturesAsStr, entityTimelinessAsStr, preMentionsAsStr,
				dayOfWeekAsString);
	}

	private String preMentionsToString() {
		final StringBuilder sb = new StringBuilder().append(preMentions[0]);
		for (int i = 1; i < preMentions.length; i++) {
			sb.append(ClusteringConstants.WHITE_SPACE).append(preMentions[i]);
		}
		return sb.toString();
	}

	public float getEntityTimeliness() {
		return entityTimeliness;
	}

	public void setEntityTimeliness(final float globalTimeliness) {
		this.entityTimeliness = globalTimeliness;
	}

	public void updatePreMention(final int bucket, final int value) {
		this.preMentions[bucket] += value;
	}

	public String dayOfWeekToString() {
		this.dayOfWeek[Utils.dayOfWeek(timestamp)] = 1;
		final StringBuilder sb = new StringBuilder().append(dayOfWeek[0]);
		for (int i = 1; i < dayOfWeek.length; i++) {
			sb.append(ClusteringConstants.WHITE_SPACE).append(dayOfWeek[i]);
		}
		return sb.toString();

	}
}
