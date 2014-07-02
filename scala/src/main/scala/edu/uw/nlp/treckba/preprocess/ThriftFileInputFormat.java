package edu.uw.nlp.treckba.preprocess;


import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.Reporter;



import java.io.IOException;

// Based on https://github.com/trec-kba/kba-2012-hadoop-job/blob/master/src/ilps/hadoop/ThriftFileInputFormat.java
public class ThriftFileInputFormat extends FileInputFormat<Text, StreamItemWritable> {

    @Override
    public org.apache.hadoop.mapred.RecordReader<Text, StreamItemWritable> getRecordReader(org.apache.hadoop.mapred.InputSplit inputSplit, JobConf conf, Reporter reporter) throws IOException {
        return new ThriftRecordReader(inputSplit, conf);
    }

    @Override
    protected boolean isSplitable(org.apache.hadoop.fs.FileSystem fs, org.apache.hadoop.fs.Path filename) {
        return false;
    }
}
