package edu.uw.nlp.treckba.decryption;

import java.io.IOException;
import java.util.Arrays;

public class DecryptionUtils {

	public static int executeDecryption(final String gpg, final String filename)
			throws IOException {
		final String[] cmd = new String[] { gpg, "--output",
				filename.replace(".gpg", ""), "--decrypt", filename };
		System.out.println(Arrays.toString(cmd));
		return run(cmd);
	}

	private static int run(final String[] cmd) throws IOException {
		try {
			return Runtime.getRuntime().exec(cmd).waitFor();
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

}
