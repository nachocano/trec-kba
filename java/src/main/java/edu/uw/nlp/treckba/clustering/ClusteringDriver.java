package edu.uw.nlp.treckba.clustering;

import java.util.Collections;
import java.util.Comparator;
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
		options.addOption("tr", true, "test relevant");
		options.addOption("trr", true, "train relevant");
		options.addOption("ot", true, "output test");
		options.addOption("otr", true, "output train");
		options.addOption("av", true, "alpha verb");
		options.addOption("an", true, "alpha noun");
		options.addOption("gvi", true, "gamma verb increase");
		options.addOption("gvd", true, "gamma verb decrease");
		options.addOption("gni", true, "gamma noun increase");
		options.addOption("gnd", true, "gamma noun decrease");

		final CommandLineParser parser = new BasicParser();

		String trainRelevant = null;
		String testRelevant = null;
		String outputTrain = null;
		String outputTest = null;
		float alphaVerb = 0;
		float alphaNoun = 0;
		float gammaVerbIncrease = 0;
		float gammaVerbDecrease = 0;
		float gammaNounIncrease = 0;
		float gammaNounDecrease = 0;

		try {
			final CommandLine line = parser.parse(options, args);
			trainRelevant = line.getOptionValue("trr");
			Validate.notNull(trainRelevant);
			testRelevant = line.getOptionValue("tr");
			Validate.notNull(testRelevant);
			outputTest = line.getOptionValue("ot");
			Validate.notNull(outputTest);
			outputTrain = line.getOptionValue("otr");
			Validate.notNull(outputTrain);
			alphaVerb = Float.parseFloat(line.getOptionValue("av"));
			Validate.isTrue(alphaVerb != 0);
			alphaNoun = Float.parseFloat(line.getOptionValue("an"));
			Validate.isTrue(alphaNoun != 0);
			gammaVerbIncrease = Float.parseFloat(line.getOptionValue("gvi"));
			Validate.isTrue(gammaVerbIncrease != 0);
			gammaVerbDecrease = Float.parseFloat(line.getOptionValue("gvd"));
			Validate.isTrue(gammaVerbDecrease != 0);
			gammaNounIncrease = Float.parseFloat(line.getOptionValue("gni"));
			Validate.isTrue(gammaNounIncrease != 0);
			gammaNounDecrease = Float.parseFloat(line.getOptionValue("gnd"));
			Validate.isTrue(gammaNounDecrease != 0);

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
		final Map<String, List<ClusterExample>> test = ClusteringUtils
				.readInput(testRelevant);
		System.out.println(sort(test));
		Validate.isTrue(train.keySet().equals(test.keySet()));
		final long start = System.currentTimeMillis();

		final ClusteringFeatureFactory cff = new ClusteringFeatureFactory();
		cff.computeFeatures(train, test, outputTrain, outputTest, nounsParams,
				verbsParams);
		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}

	private static int sort(final Map<String, List<ClusterExample>> map) {
		int count = 0;
		for (final String targetId : map.keySet()) {
			final List<ClusterExample> examples = map.get(targetId);
			count += examples.size();
			Collections.sort(examples, new Comparator<ClusterExample>() {
				@Override
				public int compare(final ClusterExample o1,
						final ClusterExample o2) {
					return o1.getStreamId().compareTo(o2.getStreamId());
				}
			});
		}
		return count;
	}
}
