package edu.uw.nlp.treckba.feature;

public class TruthKey {

	private String streamId;
	private String targetId;

	public TruthKey(final String streamId, final String targetId) {
		this.streamId = streamId;
		this.targetId = targetId;
	}

	public String getStreamId() {
		return streamId;
	}

	public void setStreamId(final String streamId) {
		this.streamId = streamId;
	}

	public String getTargetId() {
		return targetId;
	}

	public void setTargetId(final String targetId) {
		this.targetId = targetId;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = (prime * result)
				+ ((streamId == null) ? 0 : streamId.hashCode());
		result = (prime * result)
				+ ((targetId == null) ? 0 : targetId.hashCode());
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
		final TruthKey other = (TruthKey) obj;
		if (streamId == null) {
			if (other.streamId != null) {
				return false;
			}
		} else if (!streamId.equals(other.streamId)) {
			return false;
		}
		if (targetId == null) {
			if (other.targetId != null) {
				return false;
			}
		} else if (!targetId.equals(other.targetId)) {
			return false;
		}
		return true;
	}

}
