package edu.uw.nlp.treckba.preprocess;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileSplit;
import org.apache.hadoop.mapred.InputSplit;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.RecordReader;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TIOStreamTransport;

import java.io.IOException;

// Based on https://github.com/trec-kba/kba-2012-hadoop-job/blob/master/src/ilps/hadoop/ThriftRecordReader.java
public class ThriftRecordReader implements RecordReader<Text, StreamItemWritable> {

    private FSDataInputStream in;
    private FileSplit fileSplit;
    private TProtocol tp;
    private long start;
    private long length;
    private long position;

    public ThriftRecordReader(InputSplit inputSplit, JobConf conf) throws IOException {
        fileSplit = (FileSplit) inputSplit;
        start = fileSplit.getStart();
        length = fileSplit.getLength();
        position = 0;
        Path path = fileSplit.getPath();
        FileSystem fs = path.getFileSystem(conf);
        in = fs.open(path);
        tp = new TBinaryProtocol.Factory().getProtocol(new TIOStreamTransport(in));
    }


    @Override
    public boolean next(Text key, StreamItemWritable value) throws IOException {

        key.set(fileSplit.getPath().toString());

        if (in.available() > 0) {

            try {
                value.read(tp);
                position = length - in.available() - start;
                return true;
            } catch (Exception e) {
                System.err.println("Error getting next " + e.getMessage());
                throw new IOException(e);
            }
        }
        return false;
    }

    @Override
    public Text createKey() {
        return new Text();
    }

    @Override
    public StreamItemWritable createValue() {
        return new StreamItemWritable();
    }

    @Override
    public long getPos() throws IOException {
        return position;
    }

    @Override
    public void close() throws IOException {
        if (in != null) {
            in.close();
        }
    }

    @Override
    public float getProgress() throws IOException {
        if (length == 0) {
            return 0.0f;
        }
        return Math.min(1.0f, position / (float) length);
    }


}