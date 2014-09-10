package edu.uw.nlp.treckba.tools;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.lang3.Validate;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import edu.uw.nlp.treckba.feature.Compound;
import edu.uw.nlp.treckba.gen.MentionType;
import edu.uw.nlp.treckba.gen.Sentence;
import edu.uw.nlp.treckba.gen.StreamItem;
import edu.uw.nlp.treckba.gen.Token;
import edu.uw.nlp.treckba.utils.Utils;

public class ReadThrift {

	public ReadThrift(final String file) throws Exception {
		final String[] array = new String[] { "jessie kaech" };
		final String fullMatch = Utils.fullMatch(Arrays.asList(array));
		final Pattern full = Pattern.compile(fullMatch);
		TTransport transport = null;
		try {
			transport = new TIOStreamTransport(new BufferedInputStream(
					new FileInputStream(file)));
			final TBinaryProtocol protocol = new TBinaryProtocol(transport);
			transport.open();
			while (true) {
				final StreamItem item = new StreamItem();
				item.read(protocol);
				final String streamId = item.getStream_id();
				if ("1321046280-314ecd0f337c86a841014a90f07d00ad"
						.equals(streamId)) {
					final List<Sentence> sentences = item.getBody()
							.getSentences().get("serif");
					final Set<String> nounLemmas = new HashSet<>();
					final Set<String> verbLemmas = new HashSet<>();
					final Set<String> properNounLemmas = new HashSet<>();
					final Matcher m = full.matcher(item.getBody()
							.getClean_visible().toLowerCase());
					if (m.find()) {
						for (final Sentence sentence : sentences) {
							final Set<String> nounCandidateLemmas = new HashSet<>();
							final Set<String> verbCandidateLemmas = new HashSet<>();
							final List<Compound> properNounsCandidates = new ArrayList<>();
							final List<Token> tokens = sentence.getTokens();
							final StringBuilder lemmas = new StringBuilder();
							for (final Token token : tokens) {

								final String lemma = token.getLemma();
								if (lemma.contains("review")) {
									System.out.println("here");
								}
								lemmas.append(lemma).append(" ");

								final String pos = token.getPos();
								// take the verbs
								if (pos != null && pos.startsWith("V")) {
									final String word = filter(lemma);
									if (word.length() > 1) {
										verbCandidateLemmas.add(word);
									}

								} else if (pos != null
										&& !pos.startsWith("NNP")
										&& token.getMention_type() != MentionType.NAME
										&& pos.startsWith("N")) {
									final String word = filter(lemma);
									if (word.length() > 1) {
										nounCandidateLemmas.add(word);
									}

								} else if (pos != null
										&& pos.startsWith("NNP")
										&& (token.getMention_type() == MentionType.NAME || token
												.getMention_type() == MentionType.NOM)) {
									final String word = filter(lemma);
									if (word.length() > 1) {
										properNounsCandidates.add(new Compound(
												word, token.getMention_id()));
									}
								}
							}

							if (full.matcher(lemmas.toString()).find()) {
								nounLemmas.addAll(nounCandidateLemmas);
								verbLemmas.addAll(verbCandidateLemmas);
								properNounLemmas
										.addAll(Compound
												.compoundsToString(properNounsCandidates));
							}

						}
					}
					System.out.println(nounLemmas.toString());
					System.out.println(verbLemmas.toString());
					System.out.println(properNounLemmas.toString());
				}
			}
		} catch (final TTransportException te) {
			if (te.getType() != TTransportException.END_OF_FILE) {
				System.err
						.println(String.format(
								"exception with file %s. exc %s", file,
								te.getMessage()));
			}
		} catch (final Exception exc) {
			System.err
					.println(String.format("exception: %s", exc.getMessage()));
			throw exc;
		} finally {
			if (transport != null) {
				transport.close();
			}
		}
	}

	private String filter(final String lemma) {
		final String words = lemma.replaceAll("[^a-zA-Z]", "");
		if (words.isEmpty()) {
			return "";
		}
		if (Utils.HTML_TAGS.matcher(words).find()) {
			return "";
		}
		return words;
	}

	public static void main(final String[] args) throws Exception {
		Validate.notBlank(args[0]);
		new ReadThrift(args[0]);
	}
}
