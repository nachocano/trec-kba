package edu.uw.nlp.treckba.tools;

import java.io.BufferedInputStream;
import java.io.FileInputStream;

import org.apache.commons.lang3.Validate;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import edu.uw.nlp.treckba.gen.StreamItem;

public class ReadThrift {

	public ReadThrift(final String file) {
		TTransport transport = null;
		try {
			transport = new TIOStreamTransport(new BufferedInputStream(
					new FileInputStream(file)));
			final TBinaryProtocol protocol = new TBinaryProtocol(transport);
			transport.open();
			while (true) {
				final StreamItem item = new StreamItem();
				item.read(protocol);
				final String streamId = item.getStream_id();
				System.out.println(streamId);
			}
		} catch (final TTransportException te) {
			if (te.getType() != TTransportException.END_OF_FILE) {
				System.err
						.println(String.format(
								"exception with file %s. exc %s", file,
								te.getMessage()));
			}
		} catch (final Exception exc) {
			System.err
					.println(String.format("exception: %s", exc.getMessage()));
		} finally {
			if (transport != null) {
				transport.close();
			}
		}
	}

	public static void main(final String[] args) {
		Validate.notBlank(args[0]);
		new ReadThrift(args[0]);
	}
}
