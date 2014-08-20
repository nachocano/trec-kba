package edu.uw.nlp.treckba.downloader;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicLong;

import org.apache.commons.io.FileUtils;

import edu.uw.nlp.treckba.utils.Utils;

public class DownloaderTask implements Callable<Void> {

	private final File inputDir;
	private final String folder;
	private final Set<String> files;
	private final AtomicLong errors;
	private final AtomicLong successes;

	public DownloaderTask(final File dir, final String folder,
			final Set<String> files, final AtomicLong errors,
			final AtomicLong successes) {
		this.inputDir = dir;
		this.folder = folder;
		this.files = files;
		this.errors = errors;
		this.successes = successes;
	}

	@Override
	public Void call() throws Exception {
		final File folderDir = new File(inputDir, folder);
		if (!folderDir.isDirectory()) {
			if (!folderDir.mkdir()) {
				System.out.println("error: couldn't make directory "
						+ folderDir.getName());
				return null;
			}
		}
		for (final String file : files) {
			final File f = new File(folderDir, file);
			if (!f.exists()) {
				// check unencrypted
				final String unencryptedName = file.replace(".gpg", "");
				final File unencrypted = new File(folderDir, unencryptedName);
				if (!unencrypted.exists()) {
					download(folder, file);
				} else if (unencrypted.exists() && unencrypted.length() == 0) {
					// remove unencrypted and download it again
					unencrypted.delete();
					download(folder, file);
				}

			} else if (f.exists() && f.length() == 0) {
				// remove file and download it again
				f.delete();
				download(folder, file);
			}
		}
		return null;
	}

	private void download(final String folder, final String file) {
		final String url = Utils.CORPUS_URL + folder + File.separator + file;
		final File folderDir = new File(inputDir, folder);
		final File destination = new File(folderDir, file);
		try {
			FileUtils.copyURLToFile(new URL(url), destination);
			System.out.println("success: downloaded " + folder + File.separator
					+ file);
		} catch (final MalformedURLException e) {
			System.err.println("error: malformed url " + url);
		} catch (final IOException e) {
			System.err.println("error: ioexception downloading " + url + " to "
					+ folder + File.separator + file);
		}
	}
}
