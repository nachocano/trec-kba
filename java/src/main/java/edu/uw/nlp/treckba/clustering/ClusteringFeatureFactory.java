package edu.uw.nlp.treckba.clustering;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ClusteringFeatureFactory {

	private final ExecutorService executor = Executors.newFixedThreadPool(15);

	public void computeFeatures(final Map<String, List<ClusterExample>> train,
			final Map<String, List<ClusterExample>> test,
			final String outputTrain, final String outputTest,
			final HyperParams nounsParams, final HyperParams verbsParams) {

		final File outputTrainFile = new File(outputTrain);
		final File outputTestFile = new File(outputTest);
		final List<ClusteringFeatureTask> tasks = new ArrayList<>();
		for (final String targetId : train.keySet()) {
			final ClusteringFeatureTask t = new ClusteringFeatureTask(targetId,
					train.get(targetId), test.get(targetId), nounsParams,
					verbsParams);
			tasks.add(t);
		}

		try {
			executor.invokeAll(tasks);
		} catch (final InterruptedException e) {
			System.out.println(String.format(
					"error: interrupted exception: %s", e.getMessage()));
		} finally {
			executor.shutdown();
		}

		outputResults(train, outputTrainFile);
		outputResults(test, outputTestFile);
	}

	private void outputResults(final Map<String, List<ClusterExample>> map,
			final File outputFile) {
		PrintWriter pw = null;
		try {
			pw = new PrintWriter(outputFile);
			for (final String targetId : map.keySet()) {
				final List<ClusterExample> examples = map.get(targetId);
				for (final ClusterExample example : examples) {
					pw.println(example.toString());
				}
			}

		} catch (final FileNotFoundException e) {
			System.out.println(String.format(
					"error: writing output results: %s", e.getMessage()));
		} finally {
			if (pw != null) {
				pw.close();
			}
		}

	}

}
