package edu.uw.nlp.treckba.preprocess.hadoop;

import java.io.IOException;

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

/**
 * Based on
 * https://github.com/trec-kba/kba-2012-hadoop-job/blob/master/src/ilps/
 * hadoop/ThriftRecordReader.java Added decompression, decryption and implemented
 * a newer interface
 */
public class ThriftRecordReader implements
		RecordReader<Text, StreamItemWritable> {

	private final JobConf conf;
	private final FSDataInputStream in;
	private final FileSplit fileSplit;
	private final Path uncompressedPath;
	private final TProtocol tp;
	private final long start;
	private final long length;
	private long position;

	public ThriftRecordReader(final InputSplit inputSplit, final JobConf jobConf)
			throws IOException {
		fileSplit = (FileSplit) inputSplit;
		conf = jobConf;
		start = fileSplit.getStart();
		length = fileSplit.getLength();
		position = 0;
		final Path path = fileSplit.getPath();

		final FileSystem lfs = LocalFileSystem.getLocal(jobConf);
		final Path decryptedPath = FileUtils.decrypt(path, jobConf);
		uncompressedPath = FileUtils.decompress(decryptedPath, lfs);
		in = lfs.open(uncompressedPath);
		tp = new TBinaryProtocol.Factory().getProtocol(new TIOStreamTransport(
				in));
	}

	@Override
	public boolean next(final Text key, final StreamItemWritable value)
			throws IOException {
		key.set(fileSplit.getPath().toString());

		if (in.available() > 0) {

			try {
				value.read(tp);
				position = length - in.available() - start;
				return true;
			} catch (final Exception e) {
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
		} catch (final IOException exc) {
			System.err
					.println("IOException closing record " + exc.getMessage());
		}
		final FileSystem fs = LocalFileSystem.getLocal(conf);
		final Path compressedPath = new Path(uncompressedPath.toUri()
				.toString() + ".xz");
		final Path encryptedPath = new Path(compressedPath.toString() + ".gpg");

		try {
			fs.delete(encryptedPath, true);
		} catch (final IOException exc) {
			System.err.println("IOException removing encrypted file "
					+ exc.getMessage());
		}
		try {
			fs.delete(compressedPath, true);
		} catch (final IOException exc) {
			System.err.println("IOException removing compressed file "
					+ exc.getMessage());
		}

		try {
			fs.delete(uncompressedPath, true);
		} catch (final IOException exc) {
			System.err.println("IOException removing uncompressed file "
					+ exc.getMessage());
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