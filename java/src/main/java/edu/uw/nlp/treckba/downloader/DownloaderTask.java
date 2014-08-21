package edu.uw.nlp.treckba.downloader;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicLong;

import org.apache.commons.io.FileUtils;

import edu.uw.nlp.treckba.decryption.DecryptionUtils;
import edu.uw.nlp.treckba.utils.Utils;

public class DownloaderTask implements Callable<Void> {

	private final File inputDir;
	private final String folder;
	private final Set<String> files;
	private final AtomicLong errors;
	private final AtomicLong successes;
	private final String gpg;

	public DownloaderTask(final File dir, final String folder,
			final Set<String> files, final AtomicLong errors,
			final AtomicLong successes, final String gpg) {
		this.inputDir = dir;
		this.folder = folder;
		this.files = files;
		this.errors = errors;
		this.successes = successes;
		this.gpg = gpg;
	}

	@Override
	public Void call() throws Exception {
		final File folderDir = new File(inputDir, folder);
		if (!folderDir.isDirectory()) {
			if (!folderDir.mkdir()) {
				errors.incrementAndGet();
				System.out.println("error: make directory "
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
					downloadAndDecrypt(folder, file);
				} else if (unencrypted.exists() && unencrypted.length() == 0) {
					// remove unencrypted and download it again
					unencrypted.delete();
					downloadAndDecrypt(folder, file);
				}

			} else if (f.exists() && f.length() == 0) {
				// remove file and download it again
				f.delete();
				downloadAndDecrypt(folder, file);
			}
		}
		return null;
	}

	private void downloadAndDecrypt(final String folder, final String file) {
		final String url = Utils.CORPUS_URL + folder + File.separator + file;
		final File folderDir = new File(inputDir, folder);
		final File destination = new File(folderDir, file);
		try {
			FileUtils.copyURLToFile(new URL(url), destination);
			final int status = DecryptionUtils.executeDecryption(gpg,
					destination.getAbsolutePath());
			if (status != 0) {
				errors.incrementAndGet();
				System.out.println("error: decryption "
						+ destination.getAbsolutePath());
			} else {
				destination.delete();
				System.out.println("success: downloaded and decrypted "
						+ folder + File.separator + file);
				successes.incrementAndGet();
			}

		} catch (final MalformedURLException e) {
			System.out.println("error: malformed url " + url);
			errors.incrementAndGet();
		} catch (final IOException e) {
			errors.incrementAndGet();
			System.out.println("error: ioexception downloading " + folder
					+ File.separator + file);
		}
	}
}
