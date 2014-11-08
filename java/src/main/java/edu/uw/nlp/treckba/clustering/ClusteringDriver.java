package edu.uw.nlp.treckba.clustering;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

public class ClusteringDriver {

	public static void main(final String[] args) throws Exception {

		final Options options = new Options();
		// options.addOption("tr", true, "test relevant");
		options.addOption("i", true, "input");
		// options.addOption("ot", true, "output test");
		options.addOption("o", true, "output");
		// options.addOption("av", true, "alpha verb");
		options.addOption("a", true, "alpha");
		options.addOption("gi", true, "gamma increase");
		options.addOption("gd", true, "gamma decrease");
		// options.addOption("gni", true, "gamma noun increase");
		// options.addOption("gnd", true, "gamma noun decrease");
		options.addOption("tn", true, "timestamp normalizer");
		options.addOption("ip", true,
				"number of intermediate points, default 10");
		// options.addOption("viz", true, "vizualization json file");

		final CommandLineParser parser = new BasicParser();

		String trainRelevant = null;
		String testRelevant = null;
		String outputTrain = null;
		String outputTest = null;
		String vizOutput = null;
		float alphaVerb = 0;
		float alphaNoun = 0;
		float gammaVerbIncrease = 0;
		float gammaVerbDecrease = 0;
		float gammaNounIncrease = 0;
		float gammaNounDecrease = 0;
		long timestampNormalizer = 0;
		int intermediatePoints = 0;

		try {
			final CommandLine line = parser.parse(options, args);
			trainRelevant = line.getOptionValue("i");
			Validate.notNull(trainRelevant);
			testRelevant = line.getOptionValue("tr");
			// Validate.notNull(testRelevant);
			outputTest = line.getOptionValue("ot");
			// Validate.notNull(outputTest);
			outputTrain = line.getOptionValue("o");
			Validate.notNull(outputTrain);
			alphaVerb = Float.parseFloat(line.getOptionValue("a"));
			Validate.isTrue(alphaVerb != 0);
			alphaNoun = Float.parseFloat(line.getOptionValue("a"));
			Validate.isTrue(alphaNoun != 0);
			gammaVerbIncrease = Float.parseFloat(line.getOptionValue("gi"));
			// Validate.isTrue(gammaVerbIncrease != 0);
			gammaVerbDecrease = Float.parseFloat(line.getOptionValue("gd"));
			// Validate.isTrue(gammaVerbDecrease != 0);
			gammaNounIncrease = Float.parseFloat(line.getOptionValue("gi"));
			// Validate.isTrue(gammaNounIncrease != 0);
			gammaNounDecrease = Float.parseFloat(line.getOptionValue("gd"));
			// Validate.isTrue(gammaNounDecrease != 0);
			timestampNormalizer = Long.parseLong(line.getOptionValue("tn"));
			Validate.isTrue(timestampNormalizer != 0);
			vizOutput = line.getOptionValue("viz");
			final String ip = line.getOptionValue("ip");
			intermediatePoints = ip == null ? 10 : Integer.parseInt(ip);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("clustering", options);
			throw e;
		}

		final HyperParams nounsParams = new HyperParams(alphaNoun,
				gammaNounIncrease, gammaNounDecrease);
		final HyperParams verbsParams = new HyperParams(alphaVerb,
				gammaVerbIncrease, gammaVerbDecrease);
		final Map<String, List<ClusterExample>> train = ClusteringUtils
				.readInput(trainRelevant);
		System.out.println(sort(train));
		// final Map<String, List<ClusterExample>> test = ClusteringUtils
		// .readInput(testRelevant);
		// System.out.println(sort(test));
		// Validate.isTrue(train.keySet().equals(test.keySet()));
		final long start = System.currentTimeMillis();

		final ClusteringFeatureFactory cff = new ClusteringFeatureFactory();
		cff.computeFeatures(train, null, outputTrain, null, nounsParams,
				verbsParams, timestampNormalizer, vizOutput, intermediatePoints);
		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}

	private static int sort(final Map<String, List<ClusterExample>> map) {
		int count = 0;
		for (final String targetId : map.keySet()) {
			final List<ClusterExample> examples = map.get(targetId);
			count += examples.size();
			Collections.sort(examples, new TimestampComparator());
		}
		return count;
	}
}
