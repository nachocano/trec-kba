package edu.uw.nlp.treckba.clustering;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

import edu.uw.nlp.treckba.clustering.vis.pojo.Entity;
import edu.uw.nlp.treckba.clustering.viz.VizDataObject;

public class ClusteringFeatureFactory {

	private final ExecutorService executor = Executors.newFixedThreadPool(15);

	public void computeFeatures(final Map<String, List<ClusterExample>> train,
			final Map<String, List<ClusterExample>> test,
			final String outputTrain, final String outputTest,
			final HyperParams nounsParams, final HyperParams verbsParams,
			final long timestampNormalizer, final String vizOutput,
			final int intermediatePoints) {

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

		final Map<String, Entity> entities = new HashMap<String, Entity>();
		try {
			final List<Future<Entity>> futures = executor.invokeAll(tasks);
			for (final Future<Entity> future : futures) {
				final Entity entity = future.get();
				// if (entity.getDocs().size() < 20) {
				// continue;
				// }
				entities.put(entity.getId(), entity);
			}
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
		et.computeTimeliness(wholeCorpus, nounsParams, entities,
				intermediatePoints);

		// final PreMentions pms = new PreMentions();
		// pms.computePreMentions(train, test);
		// pms.computePreMentions(clusteringOutputs);

		// outputResults(train, outputTrainFile);
		// outputResults(test, outputTestFile);
		outputVisResults(entities, outputTrainFile);

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

	private void outputVisResults(final Map<String, Entity> entities,
			final File outputFile) {
		final Set<String> keys = entities.keySet();
		final List<Entity> ents = new ArrayList<>();
		for (final String key : keys) {
			ents.add(entities.get(key));
		}
		final ObjectMapper mapper = new ObjectMapper();
		PrintWriter pw = null;
		try {
			pw = new PrintWriter(outputFile);
			for (final Entity entity : ents) {
				final String output = mapper.writeValueAsString(entity);
				pw.println(output);
			}
		} catch (final JsonGenerationException e) {
			System.out.println("jsonGeneration Exception " + e.getMessage());
		} catch (final JsonMappingException e) {
			System.out.println("jsonMapping Exception " + e.getMessage());
		} catch (final IOException e) {
			System.out.println("io Exception " + e.getMessage());
		} finally {
			if (pw != null) {
				pw.close();
			}
		}

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
