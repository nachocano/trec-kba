package edu.uw.nlp.treckba.decryption;

import java.io.File;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentLinkedQueue;

public class BulkDecryptorTask implements Callable<Void> {

	private final File file;
	private final String gpg;
	private final ConcurrentLinkedQueue<String> logs;
	private final String context;

	public BulkDecryptorTask(final File f, final String gpg,
			final ConcurrentLinkedQueue<String> logs, final String context) {
		this.file = f;
		this.gpg = gpg;
		this.logs = logs;
		this.context = context;
	}

	@Override
	public Void call() throws Exception {
		final int status = DecryptionUtils.executeDecryption(gpg,
				file.getAbsolutePath());
		if (status != 0) {
			final String str[] = context.split("\\|");
			logs.offer(String.format("status: %s %s", str[0], str[1]));
		} else {
			file.delete();
		}
		return null;
	}
}
