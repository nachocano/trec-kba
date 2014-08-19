package edu.uw.nlp.treckba.filegen;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import edu.uw.nlp.treckba.utils.StreamIdFilename;

public class FileGen {

	private final ExecutorService executor = Executors.newFixedThreadPool(15);

	public void generateFiles(final String outputDir,
			final Map<String, Set<StreamIdFilename>> elements) {

		final File output = new File(outputDir);
		if (!output.isDirectory()) {
			System.out.println("output dir is not a directory: " + outputDir);
			return;
		}

		final List<Future<Void>> futures = new ArrayList<>();
		for (final String targetId : elements.keySet()) {
			final FileGenTask fgt = new FileGenTask(targetId,
					elements.get(targetId), output);
			final Future<Void> future = executor.submit(fgt);
			futures.add(future);
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
