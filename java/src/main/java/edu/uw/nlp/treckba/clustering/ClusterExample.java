package edu.uw.nlp.treckba.clustering;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

public class ClusterExample {

	private final String streamId;
	private final String targetId;
	private final String dateHour;
	private final int relevance;
	private float[] features;
	private WordType verbs;
	private WordType nouns;

	public ClusterExample(final String streamId, final String targetId,
			final String dateHour, final int relevance) {
		this.streamId = streamId;
		this.targetId = targetId;
		this.dateHour = dateHour;
		this.relevance = relevance;
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

	public float[] getFeatures() {
		return features;
	}

	public WordType getVerbs() {
		return verbs;
	}

	public WordType getNouns() {
		return nouns;
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
		final String nounsAsStr = nouns.toString();
		final String verbsAsStr = verbs.toString();
		return String.format("%s %s %s", sb.toString(),
				nounsAsStr, verbsAsStr);
	}
}
