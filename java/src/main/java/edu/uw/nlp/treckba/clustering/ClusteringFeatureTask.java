package edu.uw.nlp.treckba.clustering;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Callable;

import org.apache.commons.lang3.Validate;
import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

import edu.uw.nlp.treckba.clustering.vis.pojo.ClusterStaleness;
import edu.uw.nlp.treckba.clustering.vis.pojo.Document;
import edu.uw.nlp.treckba.clustering.vis.pojo.Entity;
import edu.uw.nlp.treckba.clustering.viz.VizDataObject;
import edu.uw.nlp.treckba.utils.Utils;

public class ClusteringFeatureTask implements Callable<Entity> {

	private final List<ClusterExample> train;
	private final List<ClusterExample> test;
	private final String targetId;
	private final List<Cluster> verbs;
	private final List<Cluster> nouns;
	private final List<Cluster> properNouns;
	private final HyperParams nounsParams;
	private final HyperParams verbsParams;
	private final long timestampNormalizer;
	private final boolean vizEnabled;
	private final String vizOutput;
	private int clusterName = 1;
	private int count = 0; // to generate the json, ugly as hell
	private final Entity entity;

	public ClusteringFeatureTask(final String targetId,
			final List<ClusterExample> train, final List<ClusterExample> test,
			final HyperParams nounsParams, final HyperParams verbsParams,
			final long timestampNormalizer, final String vizOutput) {
		this.targetId = targetId;
		this.train = train;
		this.test = test;
		this.verbs = new LinkedList<>();
		this.nouns = new LinkedList<>();
		this.properNouns = new LinkedList<>();
		this.nounsParams = nounsParams;
		this.verbsParams = verbsParams;
		this.timestampNormalizer = timestampNormalizer;
		this.vizEnabled = vizOutput != null;
		this.vizOutput = vizOutput;
		this.entity = new Entity(targetId);

	}

	@Override
	public Entity call() throws Exception {
		final long start = System.currentTimeMillis();
		try {
			System.out.println("processing " + targetId);
			doProcess(train, "train");
			// doProcess(test, "test", vizWriter);
		} catch (final Exception exc) {
			System.out.println("error: exception processing " + targetId
					+ ". msg " + exc.getMessage());
		} finally {
			System.out.println(String.format("finished processing %s, took %s",
					targetId, (System.currentTimeMillis() - start) / 1000));
		}
		return this.entity;
	}

	private void doProcess(final List<ClusterExample> set, final String str) {
		int left = set.size();
		for (final ClusterExample example : set) {
			left -= 1;
			System.out.println(String.format("processing %s for %s, %d left",
					str, targetId, left));
			// populateFeatures(verbs, example, example.getVerbs(), verbsParams,
			// timestampNormalizer);
			populateFeatures(nouns, example, example.getNouns(), nounsParams,
					timestampNormalizer);
			// populateFeatures(properNouns, example, example.getProperNouns(),
			// nounsParams, timestampNormalizer);

		}
	}

	private float[] populateFeatures(final List<Cluster> clusters,
			final ClusterExample example, final WordType exampleWordType,
			final HyperParams params, final long timestampNormalizer) {
		if (exampleWordType.isZero()) {
			// do not put it in any cluster
			exampleWordType.setAllZeros(1);
			exampleWordType.setMinDistance(1);
			exampleWordType.setAvgDistance(1);
			// lambdas to zero, doesn't belong to any cluster, TODO check
			exampleWordType.setLambdaDecrease(0);
			exampleWordType.setLambdaIncrease(0);
		} else {
			count++;
			entity.addDocument(new Document(example.getStreamId(), example
					.getTimestamp()));
			if (clusters.isEmpty()) {
				// create a new cluster, and add the example to it
				final Cluster c = new Cluster(clusterName++,
						example.getTimestamp(), timestampNormalizer);
				c.updateSum(exampleWordType.getArray());
				c.incrementCount();
				c.addExample(example);
				clusters.add(c);
				// allZeros=0, minDistance=0, avgDistance=0, lambdaDec=0.5,
				// lambdaInc=0.5
				exampleWordType.setLambdaDecrease(c.getLambdaDecrease());
				exampleWordType.setLambdaIncrease(c.getLambdaIncrease());
				entity.addClusterStaleness(new ClusterStaleness(c.getName(),
						example.getTimestamp(), c.getLambdaDecrease()));
			} else {
				float maxSimilarity = Float.MIN_VALUE;
				float similaritiesSum = 0;
				Cluster nearestCluster = null;
				for (final Cluster c : clusters) {
					// this may take time, try to profile it
					final float sim = ClusteringUtils.dotProduct(
							c.meanNormalized(), exampleWordType.getArray());
					similaritiesSum += sim;
					if (sim > maxSimilarity) {
						maxSimilarity = sim;
						nearestCluster = c;
					}
				}
				// two new features
				final float minDistance = 1 - maxSimilarity;
				final float avgDistance = 1 - similaritiesSum / clusters.size();
				exampleWordType.setMinDistance(minDistance);
				exampleWordType.setAvgDistance(avgDistance);

				if (minDistance < params.getAlpha()) {
					final float result = nearestCluster.decay(example, params);
					// if result is -1 is because there were some unassessed
					// test docs that should have been part of train,
					// their timestamp is before
					if (result == -1.0f) {
						Validate.isTrue(false);
						System.exit(1);
						example.setDiscardFlag(true);
					} else {
						// put the example in an existent cluster
						nearestCluster.addExample(example);
						nearestCluster.updateSum(exampleWordType.getArray());
						nearestCluster.incrementCount();
						nearestCluster.incrementLambda(params);
						nearestCluster.setTimestamp(example.getTimestamp());
						exampleWordType.setLambdaDecrease(nearestCluster
								.getLambdaDecrease());
						exampleWordType.setLambdaIncrease(nearestCluster
								.getLambdaIncrease());
						entity.addClusterStaleness(new ClusterStaleness(
								nearestCluster.getName(), example
										.getTimestamp(), nearestCluster
										.getLambdaDecrease()));
					}
				} else {
					// create a new cluster, and add the example to it
					final Cluster c = new Cluster(clusterName++,
							example.getTimestamp(), timestampNormalizer);
					c.updateSum(exampleWordType.getArray());
					c.incrementCount();
					c.addExample(example);
					clusters.add(c);
					// allZeros=0, minDistance=0, avgDistance=0, lambdaDec=0.5,
					// lambdaInc=0.5
					exampleWordType.setLambdaDecrease(c.getLambdaDecrease());
					exampleWordType.setLambdaIncrease(c.getLambdaIncrease());
					entity.addClusterStaleness(new ClusterStaleness(
							c.getName(), example.getTimestamp(), c
									.getLambdaDecrease()));
				}
			}
		}
		return null;
	}

	private String getFilename(final String targetEntity) {
		return targetEntity.replace(Utils.DIFFEO_URL, "").concat(".json");
	}

	private void writeVizObject(final PrintWriter pw, final VizDataObject obj) {
		final ObjectMapper mapper = new ObjectMapper();
		try {
			final String output = mapper.writeValueAsString(obj);
			// if is the first one
			if (count == 1) {
				pw.println(output);
			} else {
				pw.println(", " + output);
			}
		} catch (final JsonGenerationException e) {
			System.out.println("jsonGeneration Exception " + e.getMessage());
		} catch (final JsonMappingException e) {
			System.out.println("jsonMapping Exception " + e.getMessage());
		} catch (final IOException e) {
			System.out.println("io Exception " + e.getMessage());
		}
	}

}
