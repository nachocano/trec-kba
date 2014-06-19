package edu.uw.nlp.treckba.preprocess;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocalFileSystem;
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

/** Based on https://github.com/trec-kba/kba-2012-hadoop-job/blob/master/src/ilps/hadoop/ThriftRecordReader.java
 *  Added decompression and implemented a newer interface
 */
public class ThriftRecordReader implements RecordReader<Text, StreamItemWritable> {

    private JobConf conf;
    private FSDataInputStream in;
    private FileSplit fileSplit;
    private Path uncompressedPath;
    private TProtocol tp;
    private long start;
    private long length;
    private long position;

    public ThriftRecordReader(InputSplit inputSplit, JobConf jobConf) throws IOException {
        fileSplit = (FileSplit) inputSplit;
        conf = jobConf;
        start = fileSplit.getStart();
        length = fileSplit.getLength();
        position = 0;
        Path path = fileSplit.getPath();

        FileSystem lfs = LocalFileSystem.getLocal(jobConf);
        Path decryptedPath = FileUtils.decrypt(path, jobConf);
        uncompressedPath = FileUtils.decompress(decryptedPath, lfs);
        in = lfs.open(uncompressedPath);
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
                return false;
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
        try {
            if (in != null) {
                in.close();
            }
        } catch (IOException exc) {
            System.err.println("IOException closing record " + exc.getMessage());
        }
        FileSystem fs = LocalFileSystem.getLocal(conf);
        Path compressedPath = new Path(uncompressedPath.toUri().toString() + ".xz");
        Path encryptedPath = new Path(compressedPath.toString() + ".gpg");

        try {
            fs.delete(encryptedPath, true);
        } catch(IOException exc) {
            System.err.println("IOException removing encrypted file " + exc.getMessage());
        }
        try {
            fs.delete(compressedPath, true);
        } catch(IOException exc) {
            System.err.println("IOException removing compressed file " + exc.getMessage());
        }

        try {
            fs.delete(uncompressedPath, true);
        } catch(IOException exc) {
            System.err.println("IOException removing uncompressed file " + exc.getMessage());
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