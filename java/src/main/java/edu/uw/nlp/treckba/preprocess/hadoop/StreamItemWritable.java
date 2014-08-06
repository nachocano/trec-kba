package edu.uw.nlp.treckba.preprocess.hadoop;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.WritableUtils;
import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;
import org.apache.thrift.TSerializer;
import org.apache.thrift.protocol.TBinaryProtocol;

import edu.uw.nlp.treckba.gen.StreamItem;

// Taken from https://github.com/trec-kba/kba-2012-hadoop-job/blob/master/src/ilps/hadoop/StreamItemWritable.java
public class StreamItemWritable extends StreamItem implements Writable {

	private final TSerializer serializer = new TSerializer(
			new TBinaryProtocol.Factory());
	private final TDeserializer deserializer = new TDeserializer(
			new TBinaryProtocol.Factory());

	@Override
	public void write(final DataOutput dataOutput) throws IOException {

		try {
			final byte[] bytes = serializer.serialize(this);
			WritableUtils.writeVInt(dataOutput, bytes.length);
			dataOutput.write(bytes, 0, bytes.length);

		} catch (final TException e) {
			System.err
					.println("Exception serializing object " + e.getMessage());
			throw new IOException(e);
		}
	}

	@Override
	public void readFields(final DataInput dataInput) throws IOException {

		try {
			final int length = WritableUtils.readVInt(dataInput);
			final byte[] bytes = new byte[length];
			dataInput.readFully(bytes, 0, length);
			deserializer.deserialize(this, bytes);

		} catch (final TException e) {
			System.err.println("Exception deserializing object "
					+ e.getMessage());
			throw new IOException(e);
		}
	}
}
