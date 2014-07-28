package edu.uw.nlp.treckba.feature;

import java.util.HashMap;
import java.util.Map;

public class Source {

	private static Map<String, Integer> sourcesMap = new HashMap<String, Integer>();

	static {
		sourcesMap.put("arxiv", 0);
		sourcesMap.put("classified", 1);
		sourcesMap.put("forum", 2);
		sourcesMap.put("linking", 3);
		sourcesMap.put("mainstream_news", 4);
		sourcesMap.put("memetracker", 5);
		sourcesMap.put("news", 6);
		sourcesMap.put("review", 7);
		sourcesMap.put("social", 8);
		sourcesMap.put("weblog", 9);
	}

	public static int[] asArray(final String source) {
		final int[] sources = new int[10];
		final Integer idx = sourcesMap.get(source);
		if (idx != null) {
			sources[idx] = 1;
		}
		return sources;
	}
}
