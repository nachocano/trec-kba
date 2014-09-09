package edu.uw.nlp.treckba.debugging;

import java.util.List;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.Utils;

public class DebuggingDriver {

	public static void main(final String[] args) throws Exception {
		final Options options = new Options();
		options.addOption("i", true, "input entity bin file");
		options.addOption("fptp", true,
				"false positives and true positives entity file");
		options.addOption("o", true, "output file");
		options.addOption("e", true, "entitites file with surface forms");

		final CommandLineParser parser = new BasicParser();

		String inputEntityBinFile = null;
		String falseAndTruePositivesFile = null;
		String outputFile = null;
		String entitiesFile = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputEntityBinFile = line.getOptionValue("i");
			Validate.notNull(inputEntityBinFile);
			falseAndTruePositivesFile = line.getOptionValue("fptp");
			Validate.notNull(falseAndTruePositivesFile);
			outputFile = line.getOptionValue("o");
			Validate.notNull(outputFile);
			entitiesFile = line.getOptionValue("e");
			Validate.notNull(entitiesFile);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("debugging", options);
			return;
		}

		final long start = System.currentTimeMillis();
		final List<ResultStreamIdPair> streamIds = Utils
				.readFalseAndTruePositives(falseAndTruePositivesFile);
		final String filename = inputEntityBinFile.substring(
				inputEntityBinFile.lastIndexOf("/") + 1,
				inputEntityBinFile.length());
		final String targetId = Utils.DIFFEO_URL + filename.replace(".bin", "");
		System.out.println(targetId);
		final List<String> entityNames = Utils.readFile(entitiesFile).get(
				targetId);

		final Debugging debugging = new Debugging();

		debugging.debug(inputEntityBinFile, outputFile, streamIds, entityNames);

		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}
}
