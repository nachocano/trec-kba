package edu.uw.nlp.treckba.clustering;

import static edu.uw.nlp.treckba.clustering.ClusteringConstants.BUCKETS;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

import edu.uw.nlp.treckba.utils.Utils;

public class ClusterExample {

	public static enum PreMentionType {
		GENERAL, NOUN, VERB, PROPER_NOUN;
	}

	private final String streamId;
	private final String targetId;
	private final String dateHour;
	private final int relevance;
	private final long timestamp;
	private float[] features;
	private WordType verbs;
	private WordType nouns;
	private WordType properNouns;
	// discard flag, not to include it in the output...
	// should have used folder <= training_end_range instead of strictly <. Some
	// unassessed test docs should be part of unassessed train.
	private boolean discardFlag;
	private float entityTimeliness;
	private final int[] preMentions;
	private final int[] dayOfWeek;

	private final int[] preMentionsNouns;
	private final int[] preMentionsVerbs;
	private final int[] preMentionsProperNouns;

	public ClusterExample(final String streamId, final String targetId,
			final String dateHour, final int relevance) {
		this.streamId = streamId;
		this.targetId = targetId;
		this.dateHour = dateHour;
		this.relevance = relevance;
		this.timestamp = Long.valueOf(dateHour);
		this.preMentions = new int[BUCKETS];
		this.preMentionsNouns = new int[BUCKETS];
		this.preMentionsVerbs = new int[BUCKETS];
		this.preMentionsProperNouns = new int[BUCKETS];
		this.dayOfWeek = new int[7];
	}

	public void setNouns(final WordType nouns) {
		this.nouns = nouns;
	}

	public WordType getProperNouns() {
		return properNouns;
	}

	public void setProperNouns(final WordType properNouns) {
		this.properNouns = properNouns;
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
		final StringBuilder sb = new StringBuilder(targetId).append("|")
				.append(streamId).append("|").append(timestamp);
		// .append(ClusteringConstants.WHITE_SPACE).append(relevance)
		// .append(ClusteringConstants.WHITE_SPACE).append(features[0]);
		// for (int i = 1; i < features.length; i++) {
		// sb.append(ClusteringConstants.WHITE_SPACE).append(features[i]);
		// }
		// final String nounsArrayAsStr = nouns.arrayToString();
		// final String verbsArrayAsStr = verbs.arrayToString();
		// final String properNounsArrayAsStr = properNouns.arrayToString();
		final String nounsFeaturesAsStr = nouns.featuresToString();
		// final String verbsFeaturesAsStr = verbs.featuresToString();
		// final String properNounsFeaturesAsStr =
		// properNouns.featuresToString();
		final String entityTimelinessAsStr = String.format("%.5f",
				entityTimeliness);
		// final String dayOfWeekAsString = dayOfWeekToString();
		// final String preMentionsGeneralAsStr =
		// preMentionsArrayToString(preMentions);
		// final String preMentionsNounsAsStr =
		// preMentionsArrayToString(preMentionsNouns);
		// final String preMentionsVerbsAsStr =
		// preMentionsArrayToString(preMentionsVerbs);
		// final String preMentionsProperNounsAsStr =
		// preMentionsArrayToString(preMentionsProperNouns);

		// return String.format("%s %s %s %s %s %s %s %s %s %s %s %s %s",
		// sb.toString(), nounsArrayAsStr, verbsArrayAsStr,
		// properNounsArrayAsStr, nounsFeaturesAsStr, verbsFeaturesAsStr,
		// properNounsFeaturesAsStr, entityTimelinessAsStr,
		// dayOfWeekAsString, preMentionsGeneralAsStr,
		// preMentionsNounsAsStr, preMentionsVerbsAsStr,
		// preMentionsProperNounsAsStr);

		return String.format("%s|%s %s", sb.toString(), nounsFeaturesAsStr,
				entityTimelinessAsStr);

	}

	private String preMentionsArrayToString(final int[] array) {
		final StringBuilder sb = new StringBuilder().append(array[0]);
		for (int i = 1; i < array.length; i++) {
			sb.append(ClusteringConstants.WHITE_SPACE).append(array[i]);
		}
		return sb.toString();
	}

	public float getEntityTimeliness() {
		return entityTimeliness;
	}

	public void setEntityTimeliness(final float globalTimeliness) {
		this.entityTimeliness = globalTimeliness;
	}

	public void updatePreMention(final int bucket, final int value,
			final PreMentionType type) {
		switch (type) {
		case GENERAL:
			this.preMentions[bucket] += value;
			break;
		case VERB:
			this.preMentionsVerbs[bucket] += value;
			break;
		case NOUN:
			this.preMentionsNouns[bucket] += value;
			break;
		case PROPER_NOUN:
			this.preMentionsProperNouns[bucket] += value;
			break;
		default:
			throw new RuntimeException("invalid mention type");
		}

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
