package edu.uw.nlp.treckba.local.mapper;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.Pattern;

import edu.uw.nlp.treckba.utils.Utils;

public class Mapper {

	private final ExecutorService executor = Executors.newFixedThreadPool(20);
	private final AtomicLong errors = new AtomicLong(0);
	private final AtomicLong processed = new AtomicLong(0);
	private final AtomicLong matches = new AtomicLong(0);

	public void execute(final String inputDir, final Set<String> files,
			final String gpg, final Map<String, List<String>> entities) {

		final Map<String, Pattern> regexes = new HashMap<String, Pattern>();
		for (final String targetId : entities.keySet()) {
			final String regex = Utils.fullMatch(entities.get(targetId));
			regexes.put(targetId, Pattern.compile(regex));
		}

		final List<Future<Void>> futures = new ArrayList<>();
		for (final String file : files) {
			final Future<Void> future = executor.submit(new MapperTask(
					inputDir, gpg, file, regexes, errors, processed, matches));
			futures.add(future);
		}

		try {
			for (final Future<Void> future : futures) {
				future.get();
			}

			System.out.println("total files: " + files.size());
			System.out.println("errors: " + errors.get());
			System.out.println("processed: " + processed.get());
			System.out.println("matched: " + matches.get());

		} catch (final InterruptedException e) {
			System.err.println(String.format("Interrupted exception: %s",
					e.getMessage()));
		} catch (final ExecutionException e) {
			System.err.println(String.format("Execution exception: %s",
					e.getMessage()));
		} finally {
			executor.shutdown();
		}
	}
}
