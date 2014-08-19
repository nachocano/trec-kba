package edu.uw.nlp.treckba.decryption;

import java.io.File;
import java.util.concurrent.Callable;

public class BulkDecryptorTask implements Callable<Void> {

	private final File file;
	private final String gpg;
	private final String context;

	public BulkDecryptorTask(final File f, final String gpg,
			final String context) {
		this.file = f;
		this.gpg = gpg;
		this.context = context;
	}

	@Override
	public Void call() throws Exception {
		try {
			final int status = DecryptionUtils.executeDecryption(gpg,
					file.getAbsolutePath());
			if (status != 0) {
				System.out.println("status: " + logError());
			} else {
				file.delete();
			}
		} catch (final Exception exc) {
			System.out.println("exception: " + logError());
		}
		return null;
	}

	private String logError() {
		final String str[] = context.split("\\|");
		return String
				.format("%s %s %s", str[0], str[1], file.getAbsolutePath());
	}
}
