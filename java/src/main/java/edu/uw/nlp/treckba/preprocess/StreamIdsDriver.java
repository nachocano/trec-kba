package edu.uw.nlp.treckba.preprocess;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

public class StreamIdsDriver {

	public static void main(final String[] args) {

		final Options options = new Options();
		options.addOption("i", true, "input directory");
		options.addOption("o", true, "output file (with full path)");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String output = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputDir = line.getOptionValue("i");
			Validate.notNull(inputDir);
			output = line.getOptionValue("o");
			Validate.notNull(output);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("streamids", options);
			return;
		}

		final long start = System.currentTimeMillis();
		final StreamIdsReader sir = new StreamIdsReader();

		sir.readStreamIds(inputDir, output);
		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}

}
