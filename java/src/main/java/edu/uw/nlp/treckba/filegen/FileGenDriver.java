package edu.uw.nlp.treckba.filegen;

import java.util.Map;
import java.util.Set;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.StreamIdFilename;
import edu.uw.nlp.treckba.utils.Utils;

public class FileGenDriver {

	public static void main(final String[] args) throws Exception {
		final Options options = new Options();
		options.addOption("i", true, "base input directory");
		options.addOption("f", true, "input file");
		options.addOption("o", true, "output directory");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String inputFile = null;
		String outputDir = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputDir = line.getOptionValue("i");
			inputFile = line.getOptionValue("f");
			outputDir = line.getOptionValue("o");
			Validate.notNull(inputDir);
			Validate.isTrue(inputDir.endsWith("/"));
			Validate.notNull(outputDir);
			Validate.notNull(inputFile);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("filegendriver", options);
			throw e;
		}

		final Map<String, Set<StreamIdFilename>> files = Utils
				.readUnassessedFilesPerEntity(inputDir, inputFile);
		Validate.notEmpty(files);
		System.out.println(files.size());

		final FileGen fileGen = new FileGen();
		fileGen.generateFiles(outputDir, files);
	}

}
