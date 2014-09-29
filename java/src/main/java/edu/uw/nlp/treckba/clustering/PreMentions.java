package edu.uw.nlp.treckba.clustering;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.clustering.ClusterExample.PreMentionType;

public class PreMentions {

	private final ExecutorService executor = Executors.newFixedThreadPool(15);

	private Map<String, List<ClusterExample>> merge(
			final Map<String, List<ClusterExample>> train,
			final Map<String, List<ClusterExample>> test) {
		Validate.isTrue(train.size() == test.size());
		final Map<String, List<ClusterExample>> examples = new HashMap<String, List<ClusterExample>>();
		for (final String targetId : train.keySet()) {
			final List<ClusterExample> trainList = new ArrayList<ClusterExample>(
					train.get(targetId));
			final List<ClusterExample> testList = new ArrayList<ClusterExample>(
					test.get(targetId));
			trainList.addAll(testList);
			examples.put(targetId, trainList);
		}
		return examples;
	}

	public void computePreMentions(
			final Map<String, List<ClusterExample>> train,
			final Map<String, List<ClusterExample>> test) {
		final Map<String, List<ClusterExample>> trainAndTest = merge(train,
				test);
		System.out.println("computing pre mentions...");
		final long start = System.currentTimeMillis();
		for (final String targetId : trainAndTest.keySet()) {
			System.out.println("computing pre mentions for " + targetId);
			final List<ClusterExample> examples = trainAndTest.get(targetId);
			updatePreMention(examples, PreMentionType.GENERAL);
			System.out.println("computed pre mentions for " + targetId);
		}
		final long end = System.currentTimeMillis();
		System.out.println(String.format("pre mentions computed, took %s ...",
				(end - start) / 1000));
	}

	private void updatePreMention(final List<ClusterExample> examples,
			final PreMentionType type) {
		// examples are in order be in order
		if (examples.size() > 0) {
			// leave the first example empty...
			for (int i = examples.size() - 1; i > 0; i--) {
				final ClusterExample currentExample = examples.get(i);
				if (!currentExample.discard()) {
					final long currentTimestamp = currentExample.getTimestamp();
					for (int j = i - 1; j >= 0; j--) {
						final long pastTimestamp = examples.get(j)
								.getTimestamp();
						final long diffInSeconds = currentTimestamp
								- pastTimestamp;
						if (diffInSeconds > ClusteringConstants.SECONDS_IN_WEEK) {
							// won't be in any other, so I break and continue
							// with the next. Should speed things up
							break;
						}
						currentExample
								.updatePreMention(
										ClusteringConstants.ONE_HOUR_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_HOUR ? 1
												: 0, type);
						currentExample
								.updatePreMention(
										ClusteringConstants.FIVE_HOURS_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_FIVE_HOURS ? 1
												: 0, type);
						currentExample
								.updatePreMention(
										ClusteringConstants.TEN_HOURS_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_TEN_HOURS ? 1
												: 0, type);
						currentExample
								.updatePreMention(
										ClusteringConstants.ONE_DAY_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_DAY ? 1
												: 0, type);
						currentExample
								.updatePreMention(
										ClusteringConstants.TWO_DAYS_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_TWO_DAYS ? 1
												: 0, type);
						currentExample
								.updatePreMention(
										ClusteringConstants.FOUR_DAYS_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_FOUR_DAYS ? 1
												: 0, type);
						currentExample
								.updatePreMention(
										ClusteringConstants.ONE_WEEK_BUCKET,
										diffInSeconds <= ClusteringConstants.SECONDS_IN_WEEK ? 1
												: 0, type);
					}
				}
			}
		}
	}

	public void computePreMentions(
			final List<ClusteringOutput> clusteringOutputs) {

		final List<PreMentionTask> tasks = new ArrayList<>();
		for (final ClusteringOutput out : clusteringOutputs) {
			tasks.add(new PreMentionTask(out));
		}

		try {
			executor.invokeAll(tasks);

		} catch (final InterruptedException e) {
			System.out.println(String.format(
					"error: interrupted exception: %s", e.getMessage()));
		} catch (final Exception e) {
			System.out.println(String.format("error: exception: %s",
					e.getMessage()));
		} finally {
			executor.shutdown();
		}
	}

	private void computePreMentionsForClusters(final List<Cluster> clusters,
			final PreMentionType type) {
		for (final Cluster c : clusters) {
			updatePreMention(c.getExamples(), type);
		}
	}

	private final class PreMentionTask implements Callable<Void> {

		private final ClusteringOutput cOut;

		public PreMentionTask(final ClusteringOutput out) {
			this.cOut = out;
		}

		@Override
		public Void call() throws Exception {

			final long start = System.currentTimeMillis();
			System.out.println("computing pre mentions for clusters of target "
					+ cOut.getTargetId());
			computePreMentionsForClusters(cOut.getNounClusters(),
					PreMentionType.NOUN);
			// computePreMentionsForClusters(cOut.getVerbClusters(),
			// PreMentionType.VERB);
			// computePreMentionsForClusters(cOut.getProperNounClusters(),
			// PreMentionType.PROPER_NOUN);
			final long end = System.currentTimeMillis();
			System.out
					.println(String
							.format("pre mentions for clusters of target %s computed, took %s ...",
									cOut.getTargetId(), (end - start) / 1000));

			return null;
		}
	}

}
