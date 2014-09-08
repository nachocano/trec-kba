package edu.uw.nlp.treckba.utils;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

import edu.uw.nlp.treckba.feature.ExampleKey;
import edu.uw.nlp.treckba.feature.ExampleValue;

public class Utils {

	public static final int UNKNOWN_RELEVANCE = -10;
	public static final String DIFFEO_URL = "https://kb.diffeo.com/";
	public static final String CORPUS_URL = "http://s3.amazonaws.com/aws-publicdatasets/trec/kba/kba-streamcorpus-2014-v0_3_0-kba-filtered/";

	public static String toString(final int[] sources) {
		final StringBuilder sb = new StringBuilder();
		sb.append(sources[0]);
		for (int i = 1; i < sources.length; i++) {
			sb.append(" ").append(sources[i]);
		}
		return sb.toString();
	}

	public static String toString(final List<String> entityNames) {
		final StringBuilder sb = new StringBuilder();
		for (final String entityName : entityNames) {
			sb.append(entityName).append(" ");
		}
		return sb.toString().trim();
	}

	public static Map<String, List<String>> readFile(final String filename)
			throws Exception {
		final Map<String, List<String>> lines = new HashMap<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(filename)));
			String line = null;
			while ((line = br.readLine()) != null) {
				line = line.trim();
				final String[] splitted = line.split("\\|");
				final String key = splitted[0].trim();
				final String namesAsString = splitted[1];
				final String[] names = namesAsString.split(",");
				final List<String> value = new ArrayList<>();
				for (final String name : names) {
					value.add(name.trim());
				}
				lines.put(key, value);
			}
		} catch (final Exception exc) {
			System.out.println(String.format(
					"exception %s while reading file %s", exc.getMessage(),
					filename));
			throw exc;
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out.println(String.format(
							"ioexception %s while closing file %s",
							e.getMessage(), filename));
				}
			}
		}
		return lines;
	}

	public static Map<ExampleKey, ExampleValue> readAllFiltered(
			final String allFile, final Set<String> entities) {
		final Map<ExampleKey, ExampleValue> all = new HashMap<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(allFile)));
			String line = null;
			while ((line = br.readLine()) != null) {
				final String[] str = line.split(" ");
				final String targetId = str[0];
				final String streamId = str[1];
				final String dateHour = str[2];
				if (!entities.contains(targetId)) {
					System.out.println("warn: targetid " + targetId
							+ " is not in the target entities");
					continue;
				}
				final ExampleKey key = new ExampleKey(streamId, targetId);
				final ExampleValue value = new ExampleValue(UNKNOWN_RELEVANCE,
						dateHour);
				all.put(key, value);
			}
		} catch (final FileNotFoundException e) {
			System.out.println("error: file not found exception " + allFile);
		} catch (final IOException e) {
			System.out.println("error: io exception " + allFile);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("error: unexpected io exception while closing br "
									+ allFile);
				}
			}
		}
		return all;
	}

	public static Map<ExampleKey, ExampleValue> readTruthFile(
			final String truthFile, final Set<String> entities)
			throws Exception {
		Map<ExampleKey, ExampleValue> truths = null;
		BufferedReader br = null;
		try {
			final Map<ExampleKey, List<ExampleValue>> noisyTruths = new HashMap<>();
			br = new BufferedReader(new FileReader(new File(truthFile)));
			String line = null;
			while ((line = br.readLine()) != null) {
				final String[] instance = line.split("\t");
				final String targetId = instance[3];
				if (!entities.contains(targetId)) {
					continue;
				}
				final String streamId = instance[2];
				final int relevance = Integer.valueOf(instance[5]);
				final String dateHour = instance[7];
				final ExampleKey key = new ExampleKey(streamId, targetId);
				List<ExampleValue> truthValues = noisyTruths.get(key);
				if (truthValues == null) {
					truthValues = new ArrayList<>();
					truthValues.add(new ExampleValue(relevance, dateHour));
					noisyTruths.put(key, truthValues);
				} else {
					truthValues.add(new ExampleValue(relevance, dateHour));
				}
			}
			truths = Utils.getMostFrequent(noisyTruths);
		} catch (final Exception exc) {
			System.out.println(String.format(
					"error: exception %s while reading file %s",
					exc.getMessage(), truthFile));
			throw exc;
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out.println(String.format(
							"error: ioexception %s while closing file %s",
							e.getMessage(), truthFile));
				}
			}
		}
		return truths;
	}

	public static Map<ExampleKey, ExampleValue> getMostFrequent(
			final Map<ExampleKey, List<ExampleValue>> noisyTruths) {
		final Map<ExampleKey, ExampleValue> truths = new HashMap<>();
		for (final ExampleKey key : noisyTruths.keySet()) {
			final List<ExampleValue> truthValues = noisyTruths.get(key);
			final String dateHour = truthValues.get(0).getDateHour();
			final Map<Integer, Integer> counts = new HashMap<Integer, Integer>();
			for (final ExampleValue tv : truthValues) {
				final int i = tv.getRelevance();
				final Integer count = counts.get(i);
				counts.put(i, count != null ? count + 1 : 0);
			}
			final Integer popularRelevance = Utils.argmax(counts,
					new Comparator<Integer>() {
						@Override
						public int compare(final Integer o1, final Integer o2) {
							return o2.compareTo(o1);
						}
					});
			truths.put(key, new ExampleValue(popularRelevance, dateHour));
		}
		return truths;
	}

	private static Integer argmax(final Map<Integer, Integer> counts,
			final Comparator<Integer> tieBreaker) {
		int max = Integer.MIN_VALUE;
		Integer argmax = null;
		for (final Integer key : counts.keySet()) {
			final int count = counts.get(key);
			if (argmax == null || count > max || count == max
					&& tieBreaker.compare(key, argmax) < 0) {
				max = count;
				argmax = key;
			}
		}
		return argmax;
	}

	public static String fullMatch(final List<String> entityNames) {
		final StringBuilder sb = new StringBuilder();
		if (entityNames.size() > 1) {
			sb.append(fullMatch(entityNames.get(0)));
			for (int i = 1; i < entityNames.size(); i++) {
				sb.append("|").append(fullMatch(entityNames.get(i)));
			}
		} else {
			sb.append(fullMatch(entityNames.get(0)));
		}
		return sb.toString();
	}

	public static String partialMatch(final List<String> entityNames) {
		final StringBuilder sb = new StringBuilder();
		for (final String entityName : entityNames) {
			sb.append(partialMatch(entityName));
		}
		final int index = sb.lastIndexOf("|");
		if (index != -1 && index == sb.length() - 1) {
			return sb.substring(0, index);
		}
		return sb.toString();
	}

	private static String partialMatch(final String entityName) {
		final StringBuilder sb = new StringBuilder();
		final String[] nameSplitted = entityName.split(" ");
		if (nameSplitted.length > 1) {
			sb.append("\\b").append(nameSplitted[0]).append("\\b");
			for (int i = 1; i < nameSplitted.length; i++) {
				sb.append("|\\b").append(nameSplitted[i]).append("\\b");
			}
			sb.append("|");
		}
		return sb.toString();
	}

	private static String fullMatch(final String entityName) {
		final StringBuilder sb = new StringBuilder();
		final String[] names = entityName.split(" ");
		if (names.length > 1) {
			sb.append("\\b" + names[0]);
			for (int i = 1; i < names.length; i++) {
				sb.append("\\s+").append(names[i]);
			}
			sb.append("\\b");
		} else {
			sb.append("\\b").append(names[0]).append("\\b");
		}
		return sb.toString();
	}

	public static Queue<String> readFilePaths(final String pathsFile) {
		final Queue<String> paths = new LinkedList<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(pathsFile)));
			String line = null;
			while ((line = br.readLine()) != null) {
				paths.add(line.replace(".gpg", ""));
			}
		} catch (final FileNotFoundException e) {
			System.out.println("file not found exception " + pathsFile);
		} catch (final IOException e) {
			System.out.println("io exception " + pathsFile);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("unexpected io exception while closing br "
									+ pathsFile);
				}
			}
		}
		return paths;
	}

	public static Map<String, String> readUnassessedFiles(final String inputFile) {
		final Map<String, String> map = new HashMap<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(inputFile)));
			String line = null;
			while ((line = br.readLine()) != null) {
				final String[] str = line.split("\t");
				final String key = String.format("%s|%s", str[0], str[1]);
				final String value = str[2];
				map.put(key, value);
			}
		} catch (final FileNotFoundException e) {
			System.out.println("file not found exception " + inputFile);
		} catch (final IOException e) {
			System.out.println("io exception " + inputFile);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("unexpected io exception while closing br "
									+ inputFile);
				}
			}
		}
		return map;
	}

	public static Map<String, Set<StreamIdFilename>> readUnassessedFilesPerEntity(
			final String inputDir, final String inputFile) {
		final Map<String, Set<StreamIdFilename>> map = new HashMap<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(inputFile)));
			String line = null;
			while ((line = br.readLine()) != null) {
				final String[] str = line.split(" ");
				final String targetId = str[0];
				final String streamId = str[1];
				final String filename = str[2] + "/"
						+ str[3].replace(".gpg", "");
				if (!map.containsKey(targetId)) {
					final Set<StreamIdFilename> set = new HashSet<>();
					map.put(targetId, set);
				}
				map.get(targetId).add(
						new StreamIdFilename(streamId, inputDir + filename));
			}
		} catch (final FileNotFoundException e) {
			System.out.println("file not found exception " + inputFile);
		} catch (final IOException e) {
			System.out.println("io exception " + inputFile);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("unexpected io exception while closing br "
									+ inputFile);
				}
			}
		}
		return map;
	}

	public static Map<String, Set<String>> createFilesPerFolder(
			final String filename) {
		final Map<String, Set<String>> map = new HashMap<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(filename)));
			String line = null;
			while ((line = br.readLine()) != null) {
				final String[] str = line.split("/");
				final String folder = str[0];
				final String file = str[1];
				if (!map.containsKey(folder)) {
					final Set<String> set = new HashSet<>();
					map.put(folder, set);
				}
				map.get(folder).add(file);
			}
		} catch (final FileNotFoundException e) {
			System.out.println("file not found exception " + filename);
		} catch (final IOException e) {
			System.out.println("io exception " + filename);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("unexpected io exception while closing br "
									+ filename);
				}
			}
		}
		return map;
	}

	public static Set<String> corpusChunk(final String corpusChunk) {
		final Set<String> set = new HashSet<>();
		BufferedReader br = null;
		try {
			br = new BufferedReader(new FileReader(new File(corpusChunk)));
			String line = null;
			while ((line = br.readLine()) != null) {
				set.add(line.trim().replace(".gpg", ""));
			}
		} catch (final FileNotFoundException e) {
			System.out.println("file not found exception " + corpusChunk);
		} catch (final IOException e) {
			System.out.println("io exception " + corpusChunk);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("unexpected io exception while closing br "
									+ corpusChunk);
				}
			}
		}
		return set;
	}

	public static int dayOfWeek(final long timestamp) {
		final DateTime dateTime = new DateTime(timestamp * 1000,
				DateTimeZone.UTC);
		final int dayOfWeek = dateTime.getDayOfWeek();
		// 1 Monday - 7 Sunday
		return dayOfWeek - 1;
	}

	public static void main(final String[] args) {
		System.out.println(Utils.dayOfWeek(1350048017L));
	}
}