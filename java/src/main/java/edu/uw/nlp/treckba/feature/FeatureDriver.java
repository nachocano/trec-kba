package edu.uw.nlp.treckba.feature;

import java.util.List;
import java.util.Map;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.Utils;

public class FeatureDriver {

	public static void main(final String[] args) {

		final Options options = new Options();
		options.addOption("i", true, "input directory");
		options.addOption("o", true, "output file (with full path)");
		options.addOption("e", true, "entities ccr file with surface forms");
		options.addOption("t", true, "modified truth file");
		options.addOption("un", true, "unassessed doc files");
		options.addOption("u", false, "is unassessed?");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String output = null;
		Map<String, List<String>> entities = null;
		Map<TruthKey, TruthValue> truthsOrUnassessed = null;
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
			if (!line.hasOption("u")) {
				final String truthFile = line.getOptionValue("t");
				truthsOrUnassessed = Utils.readTruthFile(truthFile,
						entities.keySet());
			} else {
				final String unassessedFile = line.getOptionValue("un");
				truthsOrUnassessed = Utils.readUnassessed(unassessedFile,
						entities.keySet());
			}
			Validate.notNull(truthsOrUnassessed);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("featuredriver", options);
			return;
		}

		final long start = System.currentTimeMillis();
		final FeatureFactory ff = new FeatureFactory();

		ff.createFeatures(inputDir, output, entities, truthsOrUnassessed);

		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}
}
