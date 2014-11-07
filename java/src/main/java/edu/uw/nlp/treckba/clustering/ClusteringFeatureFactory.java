package edu.uw.nlp.treckba.clustering;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import edu.uw.nlp.treckba.clustering.viz.VizDataObject;

public class ClusteringFeatureFactory {

	private final ExecutorService executor = Executors.newFixedThreadPool(15);

	public void computeFeatures(final Map<String, List<ClusterExample>> train,
			final Map<String, List<ClusterExample>> test,
			final String outputTrain, final String outputTest,
			final HyperParams nounsParams, final HyperParams verbsParams,
			final long timestampNormalizer, final String vizOutput) {

		final File outputTrainFile = new File(outputTrain);
		// final File outputTestFile = new File(outputTest);

		final List<ClusteringFeatureTask> tasks = new ArrayList<>();
		for (final String targetId : train.keySet()) {
			final List<VizDataObject> vizDataObjects = null;
			final ClusteringFeatureTask t = new ClusteringFeatureTask(targetId,
					train.get(targetId), null, nounsParams, verbsParams,
					timestampNormalizer, vizOutput);
			tasks.add(t);
		}

		List<ClusteringOutput> clusteringOutputs = null;
		try {
			final List<Future<ClusteringOutput>> futures = executor
					.invokeAll(tasks);
			clusteringOutputs = printClusterStats(futures);

		} catch (final InterruptedException e) {
			System.out.println(String.format(
					"error: interrupted exception: %s", e.getMessage()));
		} catch (final Exception e) {
			System.out.println(String.format("error: exception: %s",
					e.getMessage()));
		} finally {
			executor.shutdown();
		}

		final List<ClusterExample> wholeCorpus = ClusteringUtils.sort(train);
		System.out.println(wholeCorpus.size());
		//
		final EntityTimeliness et = new EntityTimeliness(timestampNormalizer);
		et.computeTimeliness(wholeCorpus, nounsParams);

		// final PreMentions pms = new PreMentions();
		// pms.computePreMentions(train, test);
		// pms.computePreMentions(clusteringOutputs);

		outputResults(train, outputTrainFile);
		// outputResults(test, outputTestFile);

	}

	private List<ClusteringOutput> printClusterStats(
			final List<Future<ClusteringOutput>> futures)
			throws InterruptedException, ExecutionException, Exception {
		final List<ClusteringOutput> cOutputs = new LinkedList<>();
		int nounClusters = 0;
		// int verbClusters = 0;
		// int properNounClusters = 0;
		for (final Future<ClusteringOutput> future : futures) {
			final ClusteringOutput output = future.get();
			cOutputs.add(output);
			if (output != null) {
				final int nounSize = output.getNounClusters().size();
				// final int verbSize = output.getVerbClusters().size();
				// final int properNounSize = output.getProperNounClusters()
				// .size();
				nounClusters += nounSize;
				// verbClusters += verbSize;
				// properNounClusters += properNounSize;
			}
		}

		System.out.println("clusters " + nounClusters);
		// System.out.println("verb clusters " + verbClusters);
		// System.out.println("proper noun clusters " + properNounClusters);
		return cOutputs;
	}

	private void outputResults(final Map<String, List<ClusterExample>> map,
			final File outputFile) {
		PrintWriter pw = null;
		int discarded = 0;
		try {
			pw = new PrintWriter(outputFile);
			for (final String targetId : map.keySet()) {
				final List<ClusterExample> examples = map.get(targetId);
				for (final ClusterExample example : examples) {
					if (!example.discard()) {
						pw.println(example.toString());
					} else {
						discarded++;
					}
				}
			}

		} catch (final FileNotFoundException e) {
			System.out.println(String.format(
					"error: writing output results: %s", e.getMessage()));
		} finally {
			if (pw != null) {
				pw.close();
			}
			System.out.println("discarded: " + discarded);
		}
	}

}
