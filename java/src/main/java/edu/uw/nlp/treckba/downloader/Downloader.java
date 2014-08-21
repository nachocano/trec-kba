package edu.uw.nlp.treckba.downloader;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicLong;

public class Downloader {

	private final ExecutorService executor = Executors.newFixedThreadPool(20);
	private final AtomicLong errors = new AtomicLong(0);
	private final AtomicLong successes = new AtomicLong(0);

	public void downloadMissing(final String inputDir,
			final Map<String, Set<String>> filesPerFolder, final String gpg) {
		final File dir = new File(inputDir);
		final List<Future<Void>> futures = new ArrayList<>();
		if (dir.exists() && dir.isDirectory()) {
			for (final String folder : filesPerFolder.keySet()) {
				final Future<Void> future = executor.submit(new DownloaderTask(
						dir, folder, filesPerFolder.get(folder), errors,
						successes, gpg));
				futures.add(future);
			}
		}

		try {
			for (final Future<Void> future : futures) {
				future.get();
			}
			System.out.println("number of err: " + errors.get());
			System.out.println("number of succ: " + successes.get());

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
