package edu.uw.nlp.treckba.preprocess;

import edu.uw.nlp.treckba.gen.StreamItem;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.WritableUtils;
import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;
import org.apache.thrift.TSerializer;
import org.apache.thrift.protocol.TBinaryProtocol;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

// Taken from https://github.com/trec-kba/kba-2012-hadoop-job/blob/master/src/ilps/hadoop/StreamItemWritable.java
public class StreamItemWritable extends StreamItem implements Writable {

    private TSerializer serializer = new TSerializer(new TBinaryProtocol.Factory());
    private TDeserializer deserializer = new TDeserializer(new TBinaryProtocol.Factory());

    @Override
    public void write(DataOutput dataOutput) throws IOException {

        try {
            byte[] bytes = serializer.serialize(this);
            WritableUtils.writeVInt(dataOutput, bytes.length);
            dataOutput.write(bytes, 0, bytes.length);

        } catch (TException e) {
            System.err.println("Exception serializing object " + e.getMessage());
            throw new IOException(e);
        }
    }

    @Override
    public void readFields(DataInput dataInput) throws IOException {

        try {
            int length = WritableUtils.readVInt(dataInput);
            byte[] bytes = new byte[length];
            dataInput.readFully(bytes, 0, length);
            deserializer.deserialize(this, bytes);

        } catch (TException e) {
            System.err.println("Exception deserializing object " + e.getMessage());
            throw new IOException(e);
        }
    }
}
