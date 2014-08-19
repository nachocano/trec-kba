package edu.uw.nlp.treckba.feature;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TIOStreamTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import edu.uw.nlp.treckba.gen.ContentItem;
import edu.uw.nlp.treckba.gen.MentionType;
import edu.uw.nlp.treckba.gen.Sentence;
import edu.uw.nlp.treckba.gen.StreamItem;
import edu.uw.nlp.treckba.gen.Token;
import edu.uw.nlp.treckba.utils.Utils;

public class CreateFeaturesTask implements Callable<Void> {

	private final File file;
	private final List<String> entityNames;
	private final String targetId;
	private final ConcurrentLinkedQueue<String> queue;
	private final Map<TruthKey, TruthValue> truthsMap;

	public CreateFeaturesTask(final File file,
			final ConcurrentLinkedQueue<String> queue,
			final String targetEntity, final List<String> entityNames,
			final Map<TruthKey, TruthValue> truthsMap) {
		this.file = file;
		this.queue = queue;
		this.targetId = targetEntity;
		this.entityNames = entityNames;
		this.truthsMap = truthsMap;

	}

	@Override
	public Void call() throws Exception {
		System.out.println("processing... " + targetId);
		final String fullMatch = Utils.fullMatch(entityNames);
		final String partialMatch = Utils.partialMatch(entityNames);
		final Pattern full = Pattern.compile(fullMatch);
		Pattern partial = null;
		if (!partialMatch.isEmpty()) {
			partial = Pattern.compile(partialMatch);
		}
		TTransport transport = null;
		try {
			final FileInputStream inStream = new FileInputStream(file);
			final BufferedInputStream bInStream = new BufferedInputStream(
					inStream);
			transport = new TIOStreamTransport(bInStream);
			final TBinaryProtocol protocol = new TBinaryProtocol(transport);
			transport.open();
			while (true) {
				final StreamItem item = new StreamItem();
				item.read(protocol);

				final TruthKey tk = new TruthKey(item.getStream_id(), targetId);
				if (truthsMap.containsKey(tk)) {

					final ContentItem body = item.getBody();
					final String cleanVisible = body.getClean_visible()
							.toLowerCase();

					// doc level features
					final int docLength = cleanVisible.length();
					final double logDocLength = Math.log(docLength);
					final int[] sources = Source.asArray(item.getSource()
							.toLowerCase());

					// doc - entity features
					final Matcher fullMatcher = full.matcher(cleanVisible);
					final List<Integer> fullMatchesPositions = new ArrayList<>();
					int fullMatchesCount = 0;
					int firstPosFull = -1;
					float firstPosNormFull = -1;
					int lastPosFull = -1;
					float lastPosNormFull = -1;
					int spreadFull = -1;
					float spreadNormFull = -1;
					while (fullMatcher.find()) {
						fullMatchesPositions.add(fullMatcher.start());
						fullMatchesCount++;
					}
					if (fullMatchesCount > 0) {
						firstPosFull = fullMatchesPositions.get(0);
						firstPosNormFull = (float) firstPosFull / docLength;
						lastPosFull = fullMatchesPositions
								.get(fullMatchesCount - 1);
						lastPosNormFull = (float) lastPosFull / docLength;
						spreadFull = lastPosFull - firstPosFull;
						spreadNormFull = (float) spreadFull / docLength;
					}

					int partialMatchesCount = 0;
					int firstPosPartial = -1;
					float firstPosNormPartial = -1;
					int lastPosPartial = -1;
					float lastPosNormPartial = -1;
					int spreadPartial = -1;
					float spreadNormPartial = -1;
					if (partial != null) {
						final Matcher partialMatcher = partial
								.matcher(cleanVisible);
						final List<Integer> partialMatchesPositions = new ArrayList<>();
						while (partialMatcher.find()) {
							partialMatchesPositions.add(partialMatcher.start());
							partialMatchesCount++;
						}
						if (partialMatchesCount > 0) {
							firstPosPartial = partialMatchesPositions.get(0);
							firstPosNormPartial = (float) firstPosPartial
									/ docLength;
							lastPosPartial = partialMatchesPositions
									.get(partialMatchesCount - 1);
							lastPosNormPartial = (float) lastPosPartial
									/ docLength;
							spreadPartial = lastPosPartial - firstPosPartial;
							spreadNormPartial = (float) spreadPartial
									/ docLength;
						}
					}

					final List<Sentence> sentences = body.getSentences().get(
							"serif");
					final Set<String> nounLemmas = new HashSet<>();
					final Set<String> verbLemmas = new HashSet<>();
					for (final Sentence sentence : sentences) {
						boolean containsMatch = false;
						final Set<String> nounCandidateLemmas = new HashSet<>();
						final Set<String> verbCandidateLemmas = new HashSet<>();
						final List<Token> tokens = sentence.getTokens();
						for (final Token token : tokens) {
							final String lemma = token.getLemma();
							final MentionType mentionType = token
									.getMention_type();
							if (partial != null
									&& partial.matcher(lemma).find()
									|| full.matcher(lemma).find()) {
								if (mentionType == MentionType.NAME) {
									containsMatch = true;
									// don't add it as candidate
									continue;
								}
							}
							final String pos = token.getPos();
							// take the verbs
							if (pos != null && pos.startsWith("V")) {
								final String removedNonWords = lemma
										.replaceAll("[^a-zA-Z ]", "");
								if (removedNonWords.length() > 1) {
									verbCandidateLemmas.add(removedNonWords);
								}
							} else if (pos != null && !pos.startsWith("NNP")
									&& pos.startsWith("N")) {
								// take the nouns
								final String nonWords = lemma.replaceAll(
										"[^a-zA-Z ]", "");
								if (nonWords.length() > 1) {
									nounCandidateLemmas.add(nonWords);
								}
							}
						}
						if (containsMatch) {
							nounLemmas.addAll(nounCandidateLemmas);
							verbLemmas.addAll(verbCandidateLemmas);
						}
					}

					// adding features to queue
					final String fullMatchesFeatures = String.format(
							"%d %d %.5f %d %.5f %d %.5f", fullMatchesCount,
							firstPosFull, firstPosNormFull, lastPosFull,
							lastPosNormFull, spreadFull, spreadNormFull);
					final String partialMatchesFeatures = String.format(
							"%d %d %.5f %d %.5f %d %.5f", partialMatchesCount,
							firstPosPartial, firstPosNormPartial,
							lastPosPartial, lastPosNormPartial, spreadPartial,
							spreadNormPartial);

					final TruthValue truthValue = truthsMap.get(tk);

					final String features = String.format(
							"%s %s %s %s %s %s %s %s %s %s",
							item.getStream_id(), targetId,
							truthValue.getDateHour(),
							truthValue.getRelevance(), Utils.toString(sources),
							logDocLength, fullMatchesFeatures,
							partialMatchesFeatures, nounLemmas.toString(),
							verbLemmas.toString());
					queue.add(features);
				}
			}
		} catch (final TTransportException te) {
			if (te.getType() != TTransportException.END_OF_FILE) {
				System.err.println(String.format(
						"exception with file %s. exc %s", file.getName(),
						te.getMessage()));
			}
		} catch (final Exception exc) {
			System.err
					.println(String.format("exception: %s", exc.getMessage()));
		} finally {
			if (transport != null) {
				transport.close();
			}
			System.out.println("finished processing... " + targetId);
		}
		return null;
	}
}