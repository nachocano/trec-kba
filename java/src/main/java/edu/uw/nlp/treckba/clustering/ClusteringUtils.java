package edu.uw.nlp.treckba.clustering;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.lang3.Validate;

public class ClusteringUtils {

	public static Map<String, List<ClusterExample>> readInput(
			final String filename) {
		final Map<String, List<ClusterExample>> examples = new HashMap<>();
		BufferedReader br = null;
		int count = 0;
		try {
			br = new BufferedReader(new FileReader(new File(filename)));
			String line = null;

			while ((line = br.readLine()) != null) {
				final String[] str = line.split(" ");
				// Validate.isTrue(str.length == ClusteringConstants.D);
				count += 1;
				final String streamId = str[0];
				final String targetId = str[1];
				final String dateHour = str[2];
				final int relevance = Integer.valueOf(str[3]);
				final float[] features = new float[ClusteringConstants.NR_FEATURES];
				for (int j = 0, i = 4; j < 25 && i < 29; j++, i++) {
					features[j] = Float.valueOf(str[i]);
				}
				// final float[] nouns = new
				// float[ClusteringConstants.EMBEDDING_DIM];
				// for (int j = 0, i = 29; j < 300 && i < 329; j++, i++) {
				// nouns[j] = Float.valueOf(str[i]);
				// }
				final Map<Integer, Float> nouns = new HashMap<>();
				// maybe there's no stuff
				if (str.length > 29) {
					for (int i = 29; i < str.length; i++) {
						final String[] tuple = str[i].split(",");
						nouns.put(Integer.valueOf(tuple[0]),
								Float.valueOf(tuple[1]));
					}
				}
				// final float[] verbs = new
				// float[ClusteringConstants.EMBEDDING_DIM];
				// for (int j = 0, i = 329; j < 300 && i < 629; j++, i++) {
				// verbs[j] = Float.valueOf(str[i]);
				// }
				// final float[] properNouns = new
				// float[ClusteringConstants.EMBEDDING_DIM];
				// for (int j = 0, i = 629; j < 300 && i < 929; j++, i++) {
				// properNouns[j] = Float.valueOf(str[i]);
				// }
				final ClusterExample ce = new ClusterExample(streamId,
						targetId, dateHour, relevance);
				ce.setNouns(new WordType(nouns));
				// ce.setVerbs(new WordType(verbs));
				// ce.setProperNouns(new WordType(properNouns));
				ce.setFeatures(features);
				if (!examples.containsKey(targetId)) {
					final List<ClusterExample> set = new LinkedList<>();
					examples.put(targetId, set);
				}
				examples.get(targetId).add(ce);
			}
		} catch (final FileNotFoundException e) {
			System.out.println("error: file not found exception " + filename);
		} catch (final IOException e) {
			System.out.println("error: io exception " + filename);
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (final IOException e) {
					System.out
							.println("error: unexpected io exception while closing br "
									+ filename);
				}
			}
		}
		System.out.println(count);
		return examples;
	}

	public static float dotProduct(final float[] a, final float[] b) {
		Validate.isTrue(a.length == b.length);
		float dotProd = 0;
		for (int i = 0; i < a.length; i++) {
			dotProd += a[i] * b[i];
		}
		return dotProd;
	}

	public static float dotProduct(final Map<Integer, Float> a,
			final Map<Integer, Float> b) {
		float sum = 0f;
		final Set<Integer> aKeys = a.keySet();
		final Set<Integer> bKeys = b.keySet();
		if (aKeys.size() <= bKeys.size()) {
			for (final int i : aKeys) {
				if (bKeys.contains(i)) {
					sum += a.get(i) * b.get(i);
				}
			}
		} else {
			for (final int i : bKeys) {
				if (aKeys.contains(i)) {
					sum += a.get(i) * b.get(i);
				}
			}
		}
		return sum;
	}

	public static float[] normalize(final float[] a) {
		final float length = norm2(a);
		for (int i = 0; i < a.length; i++) {
			a[i] /= length;
		}
		return a;
	}

	public static Map<Integer, Float> normalize(final Map<Integer, Float> a) {
		final float length = norm2(a);
		for (final int k : a.keySet()) {
			a.put(k, a.get(k) / length);
		}
		return a;
	}

	public static float norm2(final float[] a) {
		float norm = 0;
		for (final float element : a) {
			norm += Math.pow(element, 2);
		}
		return (float) Math.sqrt(norm);
	}

	public static float norm2(final Map<Integer, Float> a) {
		return (float) Math.sqrt(dotProduct(a, a));
	}

	public static List<ClusterExample> mergeAndSort(
			final Map<String, List<ClusterExample>> train,
			final Map<String, List<ClusterExample>> test) {
		System.out.println("merging and sorting");
		final List<ClusterExample> result = new LinkedList<ClusterExample>();
		for (final String targetId : train.keySet()) {
			result.addAll(train.get(targetId));
			result.addAll(test.get(targetId));
		}
		Collections.sort(result, new TimestampComparator());
		System.out.println("sorted");
		return result;
	}
}
