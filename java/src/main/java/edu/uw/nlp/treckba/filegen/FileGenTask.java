package edu.uw.nlp.treckba.filegen;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.Set;
import java.util.concurrent.Callable;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.tukaani.xz.XZInputStream;

import edu.uw.nlp.treckba.gen.StreamItem;
import edu.uw.nlp.treckba.utils.StreamIdFilename;
import edu.uw.nlp.treckba.utils.Utils;

public class FileGenTask implements Callable<Void> {

	private final String targetEntity;
	private final Set<StreamIdFilename> elements;
	private final File outputDir;
	private final String outputFilename;

	public FileGenTask(final String targetEntity,
			final Set<StreamIdFilename> elements, final File outputDir) {
		this.targetEntity = targetEntity;
		this.elements = elements;
		this.outputDir = outputDir;
		this.outputFilename = getFilename(targetEntity);
	}

	@Override
	public Void call() throws Exception {
		final int size = elements.size();
		System.out.println(String.format("processing %s, total files %s",
				targetEntity, size));
		BufferedOutputStream bos = null;
		TTransport outTrans = null;
		try {
			bos = new BufferedOutputStream(new FileOutputStream(new File(
					outputDir, outputFilename)));
			outTrans = new TIOStreamTransport(bos);
			final TBinaryProtocol outProtocol = new TBinaryProtocol(outTrans);
			outTrans.open();
			int left = size;
			for (final StreamIdFilename sifn : elements) {
				left -= 1;
				System.out.println(String.format("processing %s, %d left...",
						targetEntity, left));
				final String filename = sifn.getFilename();
				final String streamId = sifn.getStreamId();
				final File f = new File(filename);
				if (!f.isFile()) {
					System.out.println(String.format("missing: %s %s %s",
							targetEntity, streamId, filename));
					continue;
				}
				TTransport transport = null;
				try {
					transport = new TIOStreamTransport(new BufferedInputStream(
							new XZInputStream(new FileInputStream(filename))));
					final TBinaryProtocol protocol = new TBinaryProtocol(
							transport);
					transport.open();

					while (true) {
						final StreamItem item = new StreamItem();
						item.read(protocol);
						if (streamId.equals(item.getStream_id())) {
							item.write(outProtocol);
							bos.flush();
							break;
						}
					}
				} catch (final TTransportException te) {
					if (te.getType() != TTransportException.END_OF_FILE) {
						System.err.println(String.format(
								"exception with file %s. exc %s", filename,
								te.getMessage()));
					}
				} catch (final Exception exc) {
					System.err.println(String.format("exception: %s",
							exc.getMessage()));
				} finally {
					if (transport != null) {
						transport.close();
					}
				}
			}
		} catch (final Exception exc) {
			System.err
					.println(String.format("exception: %s", exc.getMessage()));
		} finally {
			if (outTrans != null) {
				outTrans.close();
			}

		}
		return null;
	}

	private String getFilename(final String targetEntity) {
		return targetEntity.replace(Utils.DIFFEO_URL, "").concat(".bin");
	}

}
