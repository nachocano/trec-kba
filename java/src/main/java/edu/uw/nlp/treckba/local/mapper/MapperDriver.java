package edu.uw.nlp.treckba.local.mapper;

import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.lang3.Validate;

import edu.uw.nlp.treckba.utils.Utils;

public class MapperDriver {

	public static void main(final String[] args) throws Exception {

		final Options options = new Options();
		options.addOption("e", true, "entities ccr file with surface forms");
		options.addOption("i", true, "input directory");
		options.addOption("c", true, "corpus");
		options.addOption("g", true, "gpg");

		final CommandLineParser parser = new BasicParser();

		String inputDir = null;
		String corpusChunk = null;
		String gpg = null;
		String entitiesFile = null;
		try {
			final CommandLine line = parser.parse(options, args);
			inputDir = line.getOptionValue("i");
			Validate.notNull(inputDir);
			corpusChunk = line.getOptionValue("c");
			Validate.notNull(corpusChunk);
			gpg = line.getOptionValue("g");
			Validate.notNull(gpg);
			entitiesFile = line.getOptionValue("e");
			Validate.notNull(entitiesFile);

		} catch (final Exception e) {
			final HelpFormatter formatter = new HelpFormatter();
			formatter.printHelp("mapperdriver", options);
			return;
		}

		final Set<String> files = Utils.corpusChunk(corpusChunk);
		final Map<String, List<String>> entities = Utils.readFile(entitiesFile);

		final long start = System.currentTimeMillis();
		final Mapper mapper = new Mapper();

		mapper.execute(inputDir, files, gpg, entities);

		System.out.println(String.format("total time during processing %s",
				(System.currentTimeMillis() - start) / 1000));
	}
}
