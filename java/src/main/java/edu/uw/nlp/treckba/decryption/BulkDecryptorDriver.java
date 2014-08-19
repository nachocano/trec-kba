package edu.uw.nlp.treckba.decryption;

import java.util.Map;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.Utils;

public class BulkDecryptorDriver {

	public static void main(final String[] args) {

		final Options options = new Options();
		options.addOption("i", true, "input directory");
		options.addOption("f", true, "input files");
		options.addOption("lo", true, "log output file (with full path)");
		options.addOption("g", true, "gpg path");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String inputFile = null;
		String output = null;
		String gpg = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputDir = line.getOptionValue("i");
			Validate.notNull(inputDir);
			inputFile = line.getOptionValue("f");
			Validate.notNull(inputFile);
			output = line.getOptionValue("lo");
			Validate.notNull(output);
			gpg = line.getOptionValue("g");
			Validate.notNull(gpg);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("bulkdecryption", options);
			return;
		}

		final Map<String, String> files = Utils.readUnassessedFiles(inputFile);
		final long start = System.currentTimeMillis();
		final BulkDecryptor bd = new BulkDecryptor();

		bd.decrypt(inputDir, files, output, gpg);
		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}

}
