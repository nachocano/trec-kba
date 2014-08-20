package edu.uw.nlp.treckba.downloader;

import java.io.File;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;

public class Downloader {

	private final ExecutorService executor = Executors.newFixedThreadPool(20);
	private final AtomicLong errors = new AtomicLong(0);
	private final AtomicLong successes = new AtomicLong(0);

	public void downloadMissing(final String inputDir,
			final Map<String, Set<String>> filesPerFolder) {
		final File dir = new File(inputDir);
		if (dir.exists() && dir.isDirectory()) {
			for (final String folder : filesPerFolder.keySet()) {
				executor.submit(new DownloaderTask(dir, folder, filesPerFolder
						.get(folder), errors, successes));
			}
		}

	}

}
