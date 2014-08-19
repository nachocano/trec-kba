package edu.uw.nlp.treckba.utils;

public class StreamIdFilename {

	private String streamId;
	private String filename;

	public StreamIdFilename(final String streamId, final String filename) {
		this.streamId = streamId;
		this.filename = filename;
	}

	public String getStreamId() {
		return streamId;
	}

	public void setStreamId(final String streamId) {
		this.streamId = streamId;
	}

	public String getFilename() {
		return filename;
	}

	public void setFilename(final String filename) {
		this.filename = filename;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + (filename == null ? 0 : filename.hashCode());
		result = prime * result + (streamId == null ? 0 : streamId.hashCode());
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
		final StreamIdFilename other = (StreamIdFilename) obj;
		if (filename == null) {
			if (other.filename != null) {
				return false;
			}
		} else if (!filename.equals(other.filename)) {
			return false;
		}
		if (streamId == null) {
			if (other.streamId != null) {
				return false;
			}
		} else if (!streamId.equals(other.streamId)) {
			return false;
		}
		return true;
	}

}
