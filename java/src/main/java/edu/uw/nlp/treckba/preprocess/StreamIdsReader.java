package edu.uw.nlp.treckba.preprocess;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FilenameFilter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import edu.uw.nlp.treckba.utils.Utils;

public class StreamIdsReader {

	private final ExecutorService executor = Executors.newFixedThreadPool(10);
	private final ConcurrentLinkedQueue<String> streamIds = new ConcurrentLinkedQueue<>();

	public void readStreamIds(final String inputDir, final String output) {
		final File dir = new File(inputDir);
		if (dir.exists() && dir.isDirectory()) {
			final FilenameFilter binFilter = new FilenameFilter() {
				@Override
				public boolean accept(final File dir, final String name) {
					return name.endsWith(".bin");
				}
			};
			final List<StreamIdReaderTask> tasks = new ArrayList<StreamIdReaderTask>();
			for (final File file : dir.listFiles(binFilter)) {
				final String targetEntity = Utils.DIFFEO_URL
						+ file.getName().replace(".bin", "");
				tasks.add(new StreamIdReaderTask(file, streamIds, targetEntity));
			}
			try {
				executor.invokeAll(tasks);
			} catch (final InterruptedException e) {
				System.err.println(String.format("Interrupted exception: %s",
						e.getMessage()));
			}
			PrintWriter pw = null;
			try {
				pw = new PrintWriter(new File(output));
				for (final String streamid : streamIds) {
					pw.println(streamid);
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
