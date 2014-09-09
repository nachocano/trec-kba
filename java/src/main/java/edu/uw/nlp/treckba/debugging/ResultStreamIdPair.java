package edu.uw.nlp.treckba.debugging;

public class ResultStreamIdPair {

	private final String streamId;
	private final String result;

	public ResultStreamIdPair(final String streamId, final String result) {
		this.streamId = streamId;
		this.result = result;
	}

	public String getStreamId() {
		return streamId;
	}

	public String getResult() {
		return result;
	}

}
