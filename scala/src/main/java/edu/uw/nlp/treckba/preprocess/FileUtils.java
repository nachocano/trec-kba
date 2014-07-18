package edu.uw.nlp.treckba.preprocess;

import java.io.IOException;
import java.util.Arrays;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocalFileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapred.JobConf;
import org.tukaani.xz.XZInputStream;

/**
 * Decompression, decryption utils. Decryption must be done in a local file in
 * order to call gpg os process. Decompression don't, but did it there anyway.
 * If performance is not good, we should copy back the decrypted file to hdfs
 * and continue from there.
 */
public class FileUtils {

	public static final String GPG_DIR = "GPG_DIR";
	public static final String TMP_DIR = "TMP_DIR";
	private static final String KEY_FILENAME = "trec-kba-rsa.txt";
	private static final String PATTERN = "/(.*\\.[xX][zZ]\\.[gG][pP][gG])$";

	private FileUtils() {
	}

	public static Path decrypt(final Path path, final JobConf conf)
			throws IOException {
		String dir = conf.get(FileUtils.GPG_DIR);
		if (!dir.endsWith("/")) {
			dir += "/";
		}
		final String gpg = dir + "gpg";

		final FileSystem fs = FileSystem.get(conf);
		final LocalFileSystem lfs = LocalFileSystem.getLocal(conf);
		final Path tmp = new Path(conf.get(FileUtils.TMP_DIR));
		// in distributed cache
		final Path key = new Path(KEY_FILENAME);
		if (!lfs.exists(tmp)) {
			if (lfs.mkdirs(tmp)) {
				executeImport(gpg, tmp, key);
			} else {
				throw new IOException("Could not create local tmp folder");
			}
		}

		fs.copyToLocalFile(path, tmp);
		final String gpgName = path.getName().split(PATTERN)[0];
		final String xzName = gpgName.substring(0, gpgName.lastIndexOf("."));
		final Path decryptedPath = new Path(tmp, xzName);
		executeDecryption(gpg, tmp, decryptedPath, new Path(tmp, gpgName));
		return decryptedPath;
	}

	private static void executeDecryption(final String gpg, final Path home,
			final Path output, final Path encrypted) throws IOException {
		final String[] cmd = new String[] { gpg, "--no-permission-warning",
				"--homedir", home.toUri().toString(), "--trust-model",
				"always", "--output", output.toUri().toString(), "--decrypt",
				encrypted.toUri().toString() };
		System.out.println(Arrays.toString(cmd));
		run(cmd);
	}

	private static void executeImport(final String gpg, final Path home,
			final Path key) throws IOException {
		final String[] cmd = new String[] { gpg, "--no-permission-warning",
				"--homedir", home.toUri().toString(), "--import",
				key.toUri().toString() };
		System.out.println(Arrays.toString(cmd));
		run(cmd);
	}

	private static void run(final String[] cmd) throws IOException {
		try {
			Runtime.getRuntime().exec(cmd).waitFor();
		} catch (final InterruptedException exc) {
			System.err.println("Interrupted exc running "
					+ Arrays.toString(cmd) + ". Exc " + exc.getMessage());
			throw new IOException(exc);
		} catch (final IOException exc) {
			System.err.println("IOException running " + Arrays.toString(cmd)
					+ ". Exc " + exc.getMessage());
			throw exc;
		}
	}

	public static Path decompress(final Path path, final FileSystem fs)
			throws IOException {
		XZInputStream xzIn = null;
		FSDataOutputStream out = null;
		FSDataInputStream in = null;
		final Path uncompressedPath = removeExtension(path);
		try {
			in = fs.open(path);
			xzIn = new XZInputStream(in);
			out = fs.create(uncompressedPath);
			final byte[] buffer = new byte[8 * 1024];
			int n;
			while ((n = xzIn.read(buffer)) != -1) {
				out.write(buffer, 0, n);
			}
		} catch (final IOException exc) {
			System.err.println("Exception unxz-ing file "
					+ path.toUri().toString() + ". Exc " + exc.getMessage());
			throw exc;
		} finally {
			if (xzIn != null) {
				xzIn.close();
			}
			if (in != null) {
				in.close();
			}
			if (out != null) {
				out.close();
			}
		}
		return uncompressedPath;
	}

	private static Path removeExtension(final Path path) {
		final String original = path.toUri().toString();
		final String newFilename = original.substring(0,
				original.lastIndexOf("."));
		return new Path(newFilename);
	}

	/*
	 * public static final Path getFileFromCache(JobConf conf, String filename)
	 * throws IOException { Path[] files =
	 * DistributedCache.getLocalCacheFiles(conf); for (Path file : files) { if
	 * (file.getName().endsWith(filename)) { return file; } } return null; }
	 */
}
