package edu.uw.nlp.treckba.decryption;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class BulkDecryptor {

	private final ExecutorService executor = Executors.newFixedThreadPool(10);
	private final ConcurrentLinkedQueue<String> logs = new ConcurrentLinkedQueue<>();

	public void decrypt(final String inputDir, final Map<String, String> files,
			final String output, final String gpg) {
		final File dir = new File(inputDir);
		if (dir.exists() && dir.isDirectory()) {
			final List<BulkDecryptorTask> decryptorTasks = new ArrayList<>();
			for (final Entry<String, String> entry : files.entrySet()) {
				File f = new File(dir, entry.getValue());
				if (f.isFile()) {
					decryptorTasks.add(new BulkDecryptorTask(f, gpg, logs,
							entry.getKey()));
				} else {
					final String alreadyUnencrypted = entry.getValue().replace(
							".gpg", "");
					f = new File(dir, alreadyUnencrypted);
					if (!f.isFile()) {
						final String str[] = entry.getKey().split("\\|");
						System.out.println(Arrays.toString(str));
						logs.offer(String
								.format("error: %s %s", str[0], str[1]));
					}
				}
			}
			try {
				executor.invokeAll(decryptorTasks);
			} catch (final InterruptedException e) {
				System.err.println(String.format("Interrupted exception: %s",
						e.getMessage()));
			}

			PrintWriter pw = null;
			try {
				pw = new PrintWriter(new File(output));
				for (final String log : logs) {
					pw.println(log);
				}
			} catch (final FileNotFoundException e) {
				System.err.println(String.format(
						"file not found exception: %s", e.getMessage()));
			} finally {
				if (pw != null) {
					pw.close();
				}
				executor.shutdown();
			}
		}
	}
}
