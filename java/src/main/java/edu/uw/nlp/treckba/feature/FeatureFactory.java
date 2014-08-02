package edu.uw.nlp.treckba.feature;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FilenameFilter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class FeatureFactory {

	private final ExecutorService executor = Executors.newFixedThreadPool(10);
	private final ConcurrentLinkedQueue<String> features = new ConcurrentLinkedQueue<>();

	public void createFeatures(final String inputDir, final String output,
			final Map<String, List<String>> entities,
			final Map<TruthKey, TruthValue> truths) {
		final File dir = new File(inputDir);
		if (dir.exists() && dir.isDirectory()) {
			final FilenameFilter binFilter = new FilenameFilter() {
				@Override
				public boolean accept(final File dir, final String name) {
					return name.endsWith(".bin");
				}
			};
			final List<CreateFeaturesTask> tasks = new ArrayList<CreateFeaturesTask>();
			for (final File file : dir.listFiles(binFilter)) {
				final String targetEntity = Utils.DIFFEO_URL
						+ file.getName().replace(".bin", "");
				final List<String> entityNames = entities.get(targetEntity);
				tasks.add(new CreateFeaturesTask(file, features, targetEntity,
						entityNames, truths));
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
				for (final String feature : features) {
					pw.println(feature);
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
