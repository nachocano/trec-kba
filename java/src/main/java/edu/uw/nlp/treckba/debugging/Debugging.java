package edu.uw.nlp.treckba.debugging;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import edu.uw.nlp.treckba.gen.Sentence;
import edu.uw.nlp.treckba.gen.StreamItem;
import edu.uw.nlp.treckba.gen.Token;
import edu.uw.nlp.treckba.utils.Utils;

public class Debugging {

	public void debug(final String inputFile, final String outputFile,
			final List<String> streamIds, final List<String> entityNames) {
		final String fullMatch = Utils.fullMatch(entityNames);
		final Pattern full = Pattern.compile(fullMatch);
		TTransport transport = null;
		PrintWriter pw = null;
		try {
			pw = new PrintWriter(new File(outputFile));
			transport = new TIOStreamTransport(new BufferedInputStream(
					new FileInputStream(inputFile)));
			final TBinaryProtocol protocol = new TBinaryProtocol(transport);
			transport.open();
			while (true) {
				final StreamItem item = new StreamItem();
				item.read(protocol);
				final String streamId = item.getStream_id();
				if (streamIds.contains(streamId)) {
					final List<Sentence> sentences = item.getBody()
							.getSentences().get("serif");
					final List<String> lemmasForStreamId = new ArrayList<>();
					for (final Sentence sentence : sentences) {
						final List<Token> tokens = sentence.getTokens();
						final StringBuilder lemmas = new StringBuilder();
						for (final Token token : tokens) {
							final String lemma = token.getLemma();
							lemmas.append(lemma).append(" ");
						}
						if (full.matcher(lemmas.toString()).find()) {
							lemmasForStreamId.add(lemmas.toString());
						}
					}
					pw.println(String.format("%s\t%s", streamId,
							Arrays.toString(lemmasForStreamId.toArray())));
				}
			}
		} catch (final TTransportException te) {
			if (te.getType() != TTransportException.END_OF_FILE) {
				System.err.println(String.format(
						"exception with file %s. exc %s", inputFile,
						te.getMessage()));
			}
		} catch (final Exception exc) {
			System.err
					.println(String.format("exception: %s", exc.getMessage()));
		} finally {
			if (transport != null) {
				transport.close();
			}
			if (pw != null) {
				pw.close();
			}
		}
	}
}
