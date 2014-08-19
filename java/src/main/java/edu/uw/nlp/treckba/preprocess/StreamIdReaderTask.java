package edu.uw.nlp.treckba.preprocess;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentLinkedQueue;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import edu.uw.nlp.treckba.gen.StreamItem;

public class StreamIdReaderTask implements Callable<Void> {

	private final ConcurrentLinkedQueue<String> queue;
	private final File file;
	private final String targetId;

	public StreamIdReaderTask(final File file,
			final ConcurrentLinkedQueue<String> streamIds,
			final String targetEntity) {
		this.file = file;
		this.queue = streamIds;
		this.targetId = targetEntity;
	}

	@Override
	public Void call() throws Exception {
		System.out.println("processing... " + targetId);
		TTransport transport = null;
		try {
			final FileInputStream inStream = new FileInputStream(file);
			final BufferedInputStream bInStream = new BufferedInputStream(
					inStream);
			transport = new TIOStreamTransport(bInStream);
			final TBinaryProtocol protocol = new TBinaryProtocol(transport);
			transport.open();
			while (true) {
				final StreamItem item = new StreamItem();
				item.read(protocol);
				final String streamId = item.getStream_id();
				queue.offer(String.format("%s %s", streamId, targetId));
			}
		} catch (final TTransportException te) {
			if (te.getType() != TTransportException.END_OF_FILE) {
				System.err.println(String.format(
						"exception with file %s. exc %s", file.getName(),
						te.getMessage()));
			}
		} catch (final Exception exc) {
			System.err
					.println(String.format("exception: %s", exc.getMessage()));
		} finally {
			if (transport != null) {
				transport.close();
			}
			System.out.println("finished processing... " + targetId);
		}
		return null;
	}
}
