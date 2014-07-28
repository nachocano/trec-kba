package edu.uw.nlp.treckba.feature;

import java.util.List;
import java.util.Map;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

public class FeatureDriver {

	public static void main(final String[] args) {

		final Options options = new Options();
		options.addOption("i", true, "input directory");
		options.addOption("o", true, "output file (with full path)");
		options.addOption("e", true, "entities ccr file with surface forms");
		options.addOption("t", true, "modified truth file");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String output = null;
		Map<String, List<String>> entities = null;
		Map<TruthKey, TruthValue> truths = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputDir = line.getOptionValue("i");
			Validate.notNull(inputDir);
			output = line.getOptionValue("o");
			Validate.notNull(output);
			final String entitiesCcr = line.getOptionValue("e");
			Validate.notNull(entitiesCcr);
			entities = Utils.readFile(entitiesCcr);
			Validate.notNull(entities);
			final String truthFile = line.getOptionValue("t");
			truths = Utils.readTruthFile(truthFile, entities.keySet());
			Validate.notNull(truths);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("featuredriver", options);
			return;
		}

		// System.out.println(truths.size());
		// System.out.println(entities.size());

		final long start = System.currentTimeMillis();
		final FeatureFactory ff = new FeatureFactory();

		ff.createFeatures(inputDir, output, entities, truths);
		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}
}
