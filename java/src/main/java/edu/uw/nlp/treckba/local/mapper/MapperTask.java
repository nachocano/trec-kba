package edu.uw.nlp.treckba.local.mapper;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.tukaani.xz.XZInputStream;

import edu.uw.nlp.treckba.decryption.DecryptionUtils;
import edu.uw.nlp.treckba.gen.StreamItem;

public class MapperTask implements Callable<Void> {

	private final String inputDir;
	private final String gpg;
	private final String file;
	private final Map<String, Pattern> regexes;
	private final AtomicLong errors;
	private final AtomicLong processed;
	private final AtomicLong matches;

	public MapperTask(final String inputDir, final String gpg,
			final String file, final Map<String, Pattern> regexes,
			final AtomicLong errors, final AtomicLong processed,
			final AtomicLong matches) {
		this.inputDir = inputDir;
		this.gpg = gpg;
		this.file = file;
		this.regexes = regexes;
		this.errors = errors;
		this.processed = processed;
		this.matches = matches;
	}

	@Override
	public Void call() throws Exception {
		final File actualFile = new File(inputDir, file);
		try {
			if (!actualFile.exists()) {
				// try with encrypted one
				final File encrypted = new File(inputDir, file.concat(".gpg"));
				if (!encrypted.exists()) {
					errors.incrementAndGet();
					System.out.println("error: file does not exist "
							+ encrypted.getAbsolutePath());
				} else {
					// decrypt it
					final int status = DecryptionUtils.executeDecryption(gpg,
							encrypted.getAbsolutePath());
					if (status != 0) {
						errors.incrementAndGet();
						System.out.println("error: decryption "
								+ encrypted.getAbsolutePath());
					} else {
						encrypted.delete();
						decompressAndSearch(encrypted);
					}
				}

			} else {
				decompressAndSearch(actualFile);
			}
		} catch (final Exception ex) {
			System.out.println("error: catch all exc "
					+ actualFile.getAbsolutePath() + " msg " + ex.getMessage());
		} finally {
			processed.incrementAndGet();
		}
		return null;
	}

	private void decompressAndSearch(final File f) {
		TTransport transport = null;
		try {
			transport = new TIOStreamTransport(new BufferedInputStream(
					new XZInputStream(new FileInputStream(f))));
			final TBinaryProtocol protocol = new TBinaryProtocol(transport);
			transport.open();
			while (true) {
				final StreamItem item = new StreamItem();
				item.read(protocol);
				final String streamId = item.getStream_id();
				final String cleanVisible = item.getBody().getClean_visible()
						.toLowerCase();
				for (final String targetEntity : regexes.keySet()) {
					final Matcher m = regexes.get(targetEntity).matcher(
							cleanVisible);
					if (m.find()) {
						matches.incrementAndGet();
						System.out.println(String.format("match: %s\t%s\t%s",
								streamId, targetEntity, f.getAbsolutePath()));
					}
				}
			}
		} catch (final TTransportException te) {
			if (te.getType() != TTransportException.END_OF_FILE) {
				errors.incrementAndGet();
				System.out.println(String.format(
						"error: exc with file %s. exc %s", file,
						te.getMessage()));
			}
		} catch (final Exception exc) {
			errors.incrementAndGet();
			System.out
					.println(String.format("error: exc %s", exc.getMessage()));
		} finally {
			if (transport != null) {
				transport.close();
			}
		}
	}
}
