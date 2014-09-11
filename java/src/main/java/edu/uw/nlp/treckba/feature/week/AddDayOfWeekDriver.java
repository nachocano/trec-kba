package edu.uw.nlp.treckba.feature.week;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.Utils;

public class AddDayOfWeekDriver {

	public static void main(final String[] args) {

		final Options options = new Options();
		options.addOption("i", true, "input test or train file");
		options.addOption("o", true, "output file (with full path)");

		final CommandLineParser parser = new BasicParser();

		String inputFile = null;
		String output = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputFile = line.getOptionValue("i");
			Validate.notNull(inputFile);
			output = line.getOptionValue("o");
			Validate.notNull(output);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("adddayofweekdriver", options);
			return;
		}
		addDayOfWeek(inputFile, output);
	}

	public static void addDayOfWeek(final String input, final String output) {
		BufferedReader br = null;
		PrintWriter pw = null;
		try {
			br = new BufferedReader(new FileReader(new File(input)));
			pw = new PrintWriter(new File(output));
			String line = null;
			while ((line = br.readLine()) != null) {
				final String features = line.substring(0, line.indexOf("["));
				final String[] featuresArray = features.trim().split(" ");
				final String streamId = featuresArray[0];
				final long timestamp = Long.valueOf(streamId.split("-")[0]);
				final String timestampAsStr = dayOfWeekToString(timestamp);
				pw.println(String.format("%s %s", features.trim(),
						timestampAsStr));
			}
		} catch (final FileNotFoundException e) {
			System.out.println("error: file not found exception " + input);
		} catch (final IOException e) {
			System.out.println("error: io exception " + input);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("error: unexpected io exception while closing br "
									+ input);
				}
			}
			if (pw != null) {
				pw.close();
			}
		}
	}

	public static String dayOfWeekToString(final long timestamp) {
		final int[] dayOfWeek = new int[7];
		dayOfWeek[Utils.dayOfWeek(timestamp)] = 1;
		final StringBuilder sb = new StringBuilder().append(dayOfWeek[0]);
		for (int i = 1; i < dayOfWeek.length; i++) {
			sb.append(" ").append(dayOfWeek[i]);
		}
		return sb.toString();
	}
}
