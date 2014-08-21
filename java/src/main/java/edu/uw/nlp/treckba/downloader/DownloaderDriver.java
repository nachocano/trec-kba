package edu.uw.nlp.treckba.downloader;

import java.util.Map;
import java.util.Set;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.Utils;

public class DownloaderDriver {

	public static void main(final String[] args) {

		final Options options = new Options();
		options.addOption("i", true, "input directory");
		options.addOption("f", true, "filename");
		options.addOption("g", true, "gpg");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String filename = null;
		String gpg = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputDir = line.getOptionValue("i");
			Validate.notNull(inputDir);
			filename = line.getOptionValue("f");
			Validate.notNull(filename);
			gpg = line.getOptionValue("g");
			Validate.notNull(gpg);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("downloaderdriver", options);
			return;
		}

		final Map<String, Set<String>> filesPerFolder = Utils
				.createFilesPerFolder(filename);
		final long start = System.currentTimeMillis();
		final Downloader downloader = new Downloader();

		downloader.downloadMissing(inputDir, filesPerFolder, gpg);

		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}
}
