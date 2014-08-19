package edu.uw.nlp.treckba.decryption;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class BulkDecryptor {

	private final ExecutorService executor = Executors.newFixedThreadPool(10);

	public void decrypt(final String inputDir, final Map<String, String> files,
			final String gpg) {
		final File dir = new File(inputDir);
		if (dir.exists() && dir.isDirectory()) {
			final List<Future<Void>> futures = new ArrayList<>();
			for (final Entry<String, String> entry : files.entrySet()) {
				File f = new File(dir, entry.getValue());
				if (f.isFile()) {
					futures.add(executor.submit(new BulkDecryptorTask(f, gpg,
							entry.getKey())));
				} else {
					final String alreadyUnencrypted = entry.getValue().replace(
							".gpg", "");
					f = new File(dir, alreadyUnencrypted);
					if (!f.isFile()) {
						final String str[] = entry.getKey().split("\\|");
						System.out.println(String.format("error: %s %s %s",
								str[0], str[1], f.getAbsolutePath()));
					}
				}
			}
			try {
				for (final Future<Void> future : futures) {
					future.get();
				}
			} catch (final InterruptedException e) {
				System.err.println(String.format("Interrupted exception: %s",
						e.getMessage()));
			} catch (final ExecutionException e) {
				System.err.println(String.format("Execution exception: %s",
						e.getMessage()));
			} finally {
				executor.shutdown();
			}
		}
	}
}
